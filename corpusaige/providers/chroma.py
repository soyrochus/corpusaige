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
from corpusaige.exceptions import InvalidConfigEntry
from corpusaige.registry import ServiceRegistry
from corpusaige.providers import embeddings_factory
from langchain.vectorstores import Chroma


_name = "chroma"

_exported_items = ["get_vectordb_factory", "local_vectordb_creator_factory"]


def get_vectordb_factory(config: CorpusConfig) -> Any:

    vbconfig = config.get_vector_db_config()
    path = config.resolve_path_to_config(vbconfig.get("path", None)) 
        
    # type: ignore
    connection_string = vbconfig.get("connection-string", None)
    if path is None and connection_string is None:
        raise InvalidConfigEntry("ChromaDb: Either path or connection must be provided")

    embedding = embeddings_factory(config)
    if path:
        vectordb = Chroma(persist_directory=str(path),
                            embedding_function=embedding)
        return vectordb
    else:
        raise NotImplementedError(
            "ChromaDb: Service connection not implemented")
  


def local_vectordb_creator_factory(config: CorpusConfig) -> None:
    """
        Create local instance of particular vector database type
    """
    
    def _():
        vbconfig: ConfigEntries = config.get_vector_db_config()
        path = config.resolve_path_to_config(
            vbconfig.get("path", None))   # type: ignore
        vectordb = Chroma(persist_directory=str(path))
        vectordb.persist()
        
    return _
   