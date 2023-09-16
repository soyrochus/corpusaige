#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""


# Import necessary modules
from corpusaige.config.read import ConfigEntries, CorpusConfig
from typing import Any

from corpusaige.exceptions import InvalidConfigEntry, InvalidProviderConfig
from corpusaige.registry import ServiceRegistry


def llm_factory(config: CorpusConfig) -> Any:
    
    factory = ServiceRegistry.get_service_item(config.llm, "get_llm_factory")
    if factory is None:
        raise InvalidProviderConfig(f"LLM type {config.llm} not found or factory not implemented")
    
    return factory(config)

       
def embeddings_factory(config: CorpusConfig) -> Any:
    factory = ServiceRegistry.get_service_item(config.llm, "get_embeddings_factory")
    if factory is None:
        raise InvalidProviderConfig(f"LLM type {config.llm} not found or factory not implemented")
    return factory(config)

def vectorstore_factory(config: CorpusConfig) -> Any:
   
    factory = ServiceRegistry.get_service_item(config.vector_db, "get_vectordb_factory")
    if factory is None:
        raise InvalidProviderConfig(f"VectorStore type {config.vector_db} not found or factory not implemented")                                           
    return factory(config)

def vectorstore_creator_factory(config: CorpusConfig) -> Any:
    factory = ServiceRegistry.get_service_item(config.vector_db, "local_vectordb_creator_factory")
    if factory is None:
        raise InvalidProviderConfig(f"VectorStore type {config.vector_db} not found or factory not implemented")  
    return factory(config)
     
def register_internal_factories():
    """Register all factories of  'internal' providers/plugins."""
    from corpusaige.providers import chroma, openai
    ServiceRegistry.register_provider(openai) # type: ignore
    ServiceRegistry.register_provider(chroma) # type: ignore