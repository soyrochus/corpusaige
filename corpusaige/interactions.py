#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules

from typing import Protocol
from corpusaige.config import CorpusConfig
from corpusaige.providers import llm_factory, retriever_factory
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

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
        llm = llm_factory(config)
        retriever = retriever_factory(config)
        
        self.qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                                    chain_type="stuff",
                                                    retriever=retriever,
                                                    return_source_documents=True,
                                                    verbose=True)

    def send_prompt(self, prompt: str) -> str | None:
        llm_response = self.qa_chain(prompt)
        process_llm_response(llm_response)
        return None
       
class StatefullInteraction(Interaction):
    def __init__(self, config: CorpusConfig):
        # create the chain to answer questions
        self.llm = llm_factory(config)
        self.retriever = retriever_factory(config)
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
     

