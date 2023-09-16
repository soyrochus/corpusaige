#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""


import sys
from typing import Any
from corpusaige.config.read import ConfigEntries, CorpusConfig
from corpusaige.registry import ServiceRegistry
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI


_name = "openai"

_exported_items = ["get_llm_factory", "get_embeddings_factory"]

def get_llm_factory(config: CorpusConfig) -> Any:
   
        llmconfig: ConfigEntries = config.get_llm_config()
        llm_model = llmconfig.get("llm-model", "")
        api_key = llmconfig.get("api-key", "")

        # type: ignore
        return ChatOpenAI(model=llm_model, openai_api_key=api_key)
   

def get_embeddings_factory(config: CorpusConfig) -> Any:
   
        llmconfig: ConfigEntries = config.get_llm_config()

        embedding_model = llmconfig.get("embedding-model", "")
        api_key = llmconfig.get("api-key", "")

        # type: ignore
        return OpenAIEmbeddings(model=embedding_model, openai_api_key=api_key)
  

def register_factories():
    """Register all factories of this provider."""
    ServiceRegistry.add_provider(sys.modules[__name__])