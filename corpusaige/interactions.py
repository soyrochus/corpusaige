#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules

from typing import Any, List, Protocol
from corpusaige.config.read import CorpusConfig
from corpusaige.documentset import DocumentSet, Entry, FileType
from corpusaige.providers import llm_factory, vectorstore_factory
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class Interaction(Protocol):

    def send_prompt(self, prompt: str) -> str | None:
        pass

# Cite sources

def process_llm_response(llm_response):
    print(llm_response['result'])
    print('\n\nSources:')
    for source in llm_response["source_documents"]:
        print(source.metadata['source'])
        
class StatelessInteraction(Interaction):
    def __init__(self, config: CorpusConfig):
        # create the chain to answer questions
        self.llm = llm_factory(config)
        self.vectorstore = vectorstore_factory(config)
        retriever = self.vectorstore.as_retriever()
        
        self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm,
                                                    chain_type="stuff",
                                                    retriever=retriever,
                                                    return_source_documents=True,
                                                    verbose=True)

    def send_prompt(self, prompt: str) -> str | None:
        llm_response = self.qa_chain(prompt)
        process_llm_response(llm_response)
        return None
       
class StatefullInteraction(Interaction):
    def __init__(self, config: CorpusConfig, retriever = None):
        # create the chain to answer questions
        self.llm = llm_factory(config)
        if retriever is None:
            self.retriever = vectorstore_factory(config).as_retriever()
        else:
            self.retriever = retriever 
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", 
                                               input_key='question', 
                                               output_key='answer', 
                                               return_messages=True)
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm, 
            retriever = self.retriever, 
            memory=self.memory, 
            return_source_documents=True)
            #verbose=True)

    def send_prompt(self, prompt: str, show_sources = False, print_output = True) -> str | None:
        llm_response = self.qa_chain({"question": prompt})
        if print_output:
            print(f"\n{llm_response['answer']}\n")
            if show_sources:
                print(f'\n\nSources: {llm_response["source_documents"][0]}')
            return None
        else:
            if show_sources:
                return f'llm_response["answer"]\n\nSources: {llm_response["source_documents"][0]}'
            else:
                return llm_response['answer']
     

class Repository(Protocol):
    def add_docset(self, docset: DocumentSet):
        pass
    def search(self, search_str: str) -> List[str]:
        pass
    def ls(self) -> List[str]:
        pass
    
class VectorRepository(Repository):
    def __init__(self, config: CorpusConfig):
        self.config = config
        self.vectorstore = vectorstore_factory(config)
    
    def as_retriever(self):
        return self.vectorstore.as_retriever()
    
    def get_glob(self, entry: Entry) -> str:
        if entry.recursive:
            return f"./**/*.{entry.file_extension}"
        else:
            return f"./*.{entry.file_extension}"    
        
    def add_docset(self, doc_set: DocumentSet):
       
        chunks = None
        for entry in doc_set.entries:
            if entry.file_type == FileType.TEXT:
                
                text_splitter = RecursiveCharacterTextSplitter (chunk_size=1000, chunk_overlap=200)
                loader = DirectoryLoader(entry.path, self.get_glob(entry))
                docs = loader.load()
                for doc in docs:
                    doc.metadata['doc-set'] = doc_set.name
                if chunks is None:
                    chunks = text_splitter.split_documents(docs)
                else:
                    chunks.extend(text_splitter.split_documents(docs))
            else:
                raise NotImplementedError(f'File type {entry.file_type} not supported yet.')
        self.vectorstore.add_documents(chunks)
        self.vectorstore.persist()

    def search(self, search_str: str) -> List[str]:
        result = self.vectorstore.similarity_search(search_str)
        #return [doc.page_content for doc in result]
        return ["\n\n".join([doc.metadata['source'],doc.page_content]) for doc in result]
    
    #def ls(self, set_name: str | None) -> List[str]:
    def ls(self) -> List[str]:
        # Where clause not in version of Chroma in use
        # if set_name:
        #     result = self.vectorstore.get(where={'doc-set', set_name})
        # else:
        result = self.vectorstore.get()
            
        sources = [metadata['source'] for metadata in result['metadatas']]
        #remove duplicates from list
        return list(dict.fromkeys(sources))