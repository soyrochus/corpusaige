
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules

from corpusaige.config import ConfigEntries, CorpusConfig
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma

def llm_factory(config: CorpusConfig) -> any:
    if config.llm == "openai":
        llmconfig : ConfigEntries = config.get_llm_config()
        model = llmconfig.get("model", "")
        api_key = llmconfig.get("api-key", "")
        
        return OpenAI(model=model, openai_api_key=api_key)
    else:
        raise NotImplementedError(f"LLM type {config.llm} not implemented")
    
def embeddings_factory(config: CorpusConfig) -> any:
    if config.llm == "openai":
        
        llmconfig : ConfigEntries = config.get_llm_config()
        model = llmconfig.get("model", "")
        api_key = llmconfig.get("api-key", "")
        
        return OpenAIEmbeddings(model=model, openai_api_key=api_key)
    else:
        raise NotImplementedError(f"Embedding function type {config.llm} not implemented")   
   
    
def retriever_factory(config: CorpusConfig) -> any:
    
    if config.vector_db == "chroma":
        vbconfig : ConfigEntries = config.get_vector_db_config()
        path = vbconfig.get("path", None)
        connection_string = vbconfig.get("connection-string", None)
        if path is None and connection_string is None: 
            raise ValueError("ChromaDb: Either path or connection must be provided") 
        
        embedding = embeddings_factory(config)
        if path:
            vectordb = Chroma(persist_directory=path,
                   embedding_function=embedding)
            return vectordb.as_retriever()
        else:
            raise NotImplementedError("ChromaDb: Service connection not implemented")
    else:
        raise NotImplementedError(f"VectorDb type {config.vector_db} not implemented")