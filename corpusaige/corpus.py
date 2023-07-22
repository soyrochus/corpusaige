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
from corpusaige.interactions import StatefullInteraction, StatelessInteraction
from .config.read import CorpusConfig

class Corpus(Protocol):
    name: str
    path: Path

    def send_prompt(self, prompt: str) -> str | None:
        pass

class MockCorpus(Corpus):

    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path

    def send_prompt(self, prompt: str) -> str | None:
        print(f"MockCorpus: {self.name} - {self.path} - {prompt}")
        return None
        
class CorpusReader(Corpus):

    debug_mode: bool = False
    show_sources: bool = False
    print_output: bool = False
    
    def __init__(self, config: CorpusConfig, debug_mode: bool = False, show_sources: bool = False, print_output: bool = False):
        self.name = config.name
        self.path = config.config_path
        self.debug_mode = debug_mode
        self.show_sources = show_sources
        self.print_output = print_output
        self.interaction = StatefullInteraction(config)
        #self.interaction = StatelessInteraction(config)

    def send_prompt(self, prompt: str) -> str | None:
        return self.interaction.send_prompt(prompt, self.show_sources, self.print_output)
        
