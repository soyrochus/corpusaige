#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
import os
from pathlib import Path
from typing import List, Protocol
from corpusaige.documentset import DocumentSet
from corpusaige.interactions import StatefullInteraction, VectorRepository
from .config.read import CorpusConfig
from corpusaige.config import CORPUS_STATE_DB


class Corpus(Protocol):
    name: str
    path: Path
    show_sources: bool = False
    context_size: int = 4

    def send_prompt(self, prompt: str) -> str:
        pass

    def add_docset(self, docset: DocumentSet) -> None:
        pass

    def store_search(self, search_str: str) -> List[str]:
        pass

    #def store_ls(self, set_name: str) -> List[str]:
    def store_ls(self) -> List[str]:
        pass

    def toggle_sources(self):
        pass


class StatefullCorpus(Corpus):

    repository: VectorRepository

    def __init__(self, config: CorpusConfig,show_sources: bool = False, 
                                            context_size: int = 4):
        self.name = config.name
        self.path = config.config_path
        self.show_sources = show_sources
        self.context_size = context_size
        self.repository = VectorRepository(config)
        self.interaction = StatefullInteraction(
            config, retriever=self.repository.as_retriever())

    @property
    def state_db_path(self) -> str:
        return os.path.join(os.path.dirname(self.path), CORPUS_STATE_DB)
    
    def send_prompt(self, prompt: str) -> str :
        return self.interaction.send_prompt(prompt, self.show_sources, self.context_size)

    def toggle_sources(self):
        self.show_sources = not self.show_sources

    def add_docset(self, docset: DocumentSet) -> None:
        self.repository.add_docset(docset)

    def store_search(self, search_str: str) -> List[str]:
        return self.repository.search(search_str, self.context_size)

    #def store_ls(self, docset_name=None) -> List[str]:
    def store_ls(self) -> List[str]:
        return self.repository.ls()
