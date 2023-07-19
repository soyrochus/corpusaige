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

from .config import CorpusConfig

class Corpus(Protocol):
    name: str
    path: str

    def send_chat(self, prompt: str) -> None:
        pass

class MockCorpus(Corpus):
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    def send_chat(self, prompt: str) -> None:
        print(f"MockCorpus: {self.name} - {self.path} - {prompt}")
        
def corpus_factory(config: CorpusConfig) -> Corpus:
    return MockCorpus(config.name, config.config_path)