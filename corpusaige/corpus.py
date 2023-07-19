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
from typing import Protocol
from corpusaige.interactions import StatelessInteraction
from .config import CorpusConfig

class Corpus(Protocol):
    name: str
    path: Path

    def send_prompt(self, prompt: str) -> None:
        pass

class MockCorpus(Corpus):

    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path

    def send_prompt(self, prompt: str) -> None:
        print(f"MockCorpus: {self.name} - {self.path} - {prompt}")
        
class CorpusReader(Corpus):

    def __init__(self, config: CorpusConfig):
        self.name = config.name
        self.path = config.config_path
        self.interaction = StatelessInteraction(config)

    def send_prompt(self, prompt: str) -> None:
        self.interaction.send_prompt(prompt)
        
