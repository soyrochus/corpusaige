
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
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from typing import Any


def llm_factory(config: CorpusConfig) -> Any:
    if config.llm == "openai":
        llmconfig: ConfigEntries = config.get_llm_config()
        model = llmconfig.get("model", "")
        api_key = llmconfig.get("api-key", "")

        return OpenAI(model=model, openai_api_key=api_key)  # type: ignore
    else:
        raise NotImplementedError(f"LLM type {config.llm} not implemented")


def embeddings_factory(config: CorpusConfig) -> Any:
    if config.llm == "openai":

        llmconfig: ConfigEntries = config.get_llm_config()
        model = llmconfig.get("model", "")
        api_key = llmconfig.get("api-key", "")

        # type: ignore
        return OpenAIEmbeddings(model=model, openai_api_key=api_key)
    else:
        raise NotImplementedError(
            f"Embedding function type {config.llm} not implemented")


def vectorstore_factory(config: CorpusConfig) -> Any:
    if config.vector_db == "chroma":
        vbconfig: ConfigEntries = config.get_vector_db_config()
        path = config.resolve_path_to_config(
            vbconfig.get("path", None))  # type: ignore
        connection_string = vbconfig.get("connection-string", None)
        if path is None and connection_string is None:
            raise ValueError(
                "ChromaDb: Either path or connection must be provided")

        embedding = embeddings_factory(config)
        if path:
            vectordb = Chroma(persist_directory=path,
                              embedding_function=embedding)
            return vectordb
        else:
            raise NotImplementedError(
                "ChromaDb: Service connection not implemented")
    else:
        raise NotImplementedError(
            f"VectorDb type {config.vector_db} not implemented")


def create_local_vectordb(config: CorpusConfig) -> None:
    """
        Create local instance of particular vector database type
    """
    if config.vector_db == "chroma":
        vbconfig: ConfigEntries = config.get_vector_db_config()
        path = config.resolve_path_to_config(
            vbconfig.get("path", None))   # type: ignore
        vectordb = Chroma(persist_directory=path)
        vectordb.persist()
    else:
        raise NotImplementedError(
            f"VectorDb type {config.vector_db} not implemented")
