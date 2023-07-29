#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""
from typing import List, Protocol
from corpusaige.config.read import CorpusConfig
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from corpusaige.documentset import DocumentSet, Entry, FileType
from corpusaige.providers import vectorstore_factory


class Repository(Protocol):
    def add_docset(self, docset: DocumentSet):
        pass
    def search(self, search_str: str, results_num:int) -> List[str]:
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

    def search(self, search_str: str, results_num: int) -> List[str]:
        result = self.vectorstore.similarity_search(search_str, k=results_num)
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