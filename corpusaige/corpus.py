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
import sys
from typing import Any, List, Protocol
from corpusaige.documentset import Document, DocumentSet
from corpusaige.interactions import StatefullInteraction, VectorRepository
from .config.read import CorpusConfig
from corpusaige.config import CORPUS_STATE_DB, CORPUS_ANNOTATIONS, CORPUS_SCRIPTS
from importlib import import_module

class Corpus(Protocol):
    name: str
    path: Path
    show_sources: bool = False
    context_size: int = 4

    def send_prompt(self, prompt: str) -> str:
        pass

    def add_docset(self, docset: DocumentSet) -> None:
        pass

    def add_doc(self, doc: Document) -> None:
        pass
        
    def store_annotation(self, annotation_docset_name: str, annotation_file: str) -> None:
        pass
    
    def store_search(self, search_str: str) -> List[str]:
        pass

    #def store_ls(self, set_name: str) -> List[str]:
    def store_ls(self) -> List[str]:
        pass

    def toggle_sources(self):
        pass

    def get_annotations_path(self) -> str:
        pass
    
    def get_corpus_folder_path(self) -> str:
        pass    
    
    def run_script(self, script_name: str, *args) -> Any:
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
        
        self.scripts = self._get_scripts()
        #set import path to corpus scripts folder
        sys.path.append(os.path.join(self.get_corpus_folder_path(), CORPUS_SCRIPTS))

    @property
    def state_db_path(self) -> str:
        return os.path.join(os.path.dirname(self.path), CORPUS_STATE_DB)
    
    def send_prompt(self, prompt: str) -> str :
        return self.interaction.send_prompt(prompt, self.show_sources, self.context_size)

    def toggle_sources(self):
        self.show_sources = not self.show_sources

    def add_docset(self, docset: DocumentSet) -> None:
        self.repository.add_docset(docset)

    def add_doc(self, doc: Document) -> None:
        self.repository.add_doc(doc)
        
    def store_search(self, search_str: str) -> List[str]:
        return self.repository.search(search_str, self.context_size)

    #def store_ls(self, docset_name=None) -> List[str]:
    def store_ls(self) -> List[str]:
        return self.repository.ls()

    def get_annotations_path(self) -> str:
        return os.path.join(self.get_corpus_folder_path(), CORPUS_ANNOTATIONS)
    
    def get_corpus_folder_path(self) -> str:
        return os.path.dirname(self.path)    
    
    def store_annotation(self, annotation_docset_name: str, annotation_file: str) -> None:
        path = os.path.join(self.get_annotations_path(),annotation_file)
        self.add_doc(Document.initialize(path, annotation_docset_name))
        
    
    def run_script(self, script_name: str, *args: List[str]) -> Any:
        
        if script_name in self.scripts:
            script = import_module(script_name)
            return script.run(self, *args)
        else:
            raise ValueError(f"Script {script_name} not found in scripts directory")
    
    def _get_scripts(self):
        scripts = []
        for file in os.listdir(os.path.join(self.get_corpus_folder_path(), CORPUS_SCRIPTS)):
            if file.endswith(".py"):
                #append file name whthout extension to scripts list
                scripts.append(os.path.splitext(file)[0])
        return scripts