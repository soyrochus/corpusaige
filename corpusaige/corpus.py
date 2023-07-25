#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
from pathlib import Path
from typing import List, Protocol
from corpusaige.documentset import DocumentSet
from corpusaige.interactions import StatefullInteraction, VectorRepository
from .config.read import CorpusConfig


class Corpus(Protocol):
    name: str
    path: Path
    debug_mode: bool = False
    show_sources: bool = False
    results_num: int = 4

    def send_prompt(self, prompt: str) -> str | None:
        pass

    def add_docset(self, docset: DocumentSet) -> None:
        pass

    def store_search(self, search_str: str) -> List[str]:
        pass

    #def store_ls(self, set_name: str) -> List[str]:
    def store_ls(self) -> List[str]:
        pass
    
    def toggle_debug(self):
        pass

    def toggle_sources(self):
        pass


class StatefullCorpus(Corpus):

    debug_mode: bool = False
    show_sources: bool = False
    print_output: bool = False
    repository: VectorRepository

    def __init__(self, config: CorpusConfig, debug_mode: bool = False, show_sources: bool = False, print_output: bool = False):
        self.name = config.name
        self.path = config.config_path
        self.debug_mode = debug_mode
        self.show_sources = show_sources
        self.print_output = print_output
        self.repository = VectorRepository(config)
        self.interaction = StatefullInteraction(
            config, retriever=self.repository.as_retriever())

    def send_prompt(self, prompt: str) -> str | None:
        return self.interaction.send_prompt(prompt, self.show_sources, self.print_output)

    def toggle_debug(self):
        self.debug_mode = not self.debug_mode

    def toggle_sources(self):
        self.show_sources = not self.show_sources

    def add_docset(self, docset: DocumentSet) -> None:
        self.repository.add_docset(docset)

    def store_search(self, search_str: str) -> List[str]:
        return self.repository.search(search_str)

    #def store_ls(self, docset_name=None) -> List[str]:
    def store_ls(self) -> List[str]:
        return self.repository.ls()
