#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
from configparser import ConfigParser
from pathlib import Path
import sys
from typing import Any, List, Protocol
from corpusaige.data.db import create_db
from corpusaige.documentset import Document, DocumentSet
from corpusaige.exceptions import InvalidParameters
from corpusaige.interactions import StatefullInteraction
from corpusaige.storage import VectorRepository
from .config.read import CorpusConfig, get_config
from corpusaige.config import CORPUS_INI, CORPUS_STATE_DB, CORPUS_ANNOTATIONS, CORPUS_SCRIPTS
from importlib import import_module

class Corpus(Protocol):
    name: str
    path: Path
    show_sources: bool = False
    context_size: int = 4

    def send_prompt(self, prompt: str) -> str:
        ...

    def add_docset(self, docset: DocumentSet) -> None:
        ...

    def remove_docset(self, docset_name: str) -> None:
        ...
           
    def add_doc(self, doc: Document) -> None:
        ...
        
    def store_annotation(self, annotation_docset_name: str, annotation_file: str) -> None:
        ...
    
    def store_search(self, search_str: str) -> List[str]:
        ...

    #def store_ls(self, set_name: str) -> List[str]:
    def ls_docs(self, all_docs: bool = False, doc_set:str = '') -> List[str]:
        ...

    def toggle_sources(self):
        ...

    @property
    def state_db_path(self) -> Path:
        ...
    
    @property
    def annotations_path(self) -> Path:
        ...
    
    @property
    def corpus_folder_path(self) -> Path:
        ...    
    
    def run_script(self, script_name: str, *args) -> Any:
        ...

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
        sys.path.append(str(self.corpus_folder_path / CORPUS_SCRIPTS))

    @property
    def state_db_path(self) -> Path:
        return self.path.parent / CORPUS_STATE_DB
    
    @property
    def annotations_path(self) -> Path:
        return self.corpus_folder_path / CORPUS_ANNOTATIONS
    
    @property
    def corpus_folder_path(self) -> Path:
        return self.path.parent
    
    def send_prompt(self, prompt: str) -> str :
        return self.interaction.send_prompt(prompt, self.show_sources, self.context_size)

    def toggle_sources(self):
        self.show_sources = not self.show_sources

    def add_docset(self, docset: DocumentSet) -> None:
        self.repository.add_docset(docset)

    def remove_docset(self, docset_name: str) -> None:
        self.repository.remove_docset(docset_name)

    def add_doc(self, doc: Document, docset_name: str) -> None:
        self.repository.add_doc(doc, docset_name)
        
    def store_search(self, search_str: str) -> List[str]:
        return self.repository.search(search_str, self.context_size)

    def ls_docs(self, all_docs: bool = False, doc_set:str = '') -> List[str]:
        
        return self.repository.ls(all_docs, doc_set)

    def store_annotation(self, annotation_docset_name: str, annotation_file: str) -> None:
        path = self.annotations_path / annotation_file
        self.add_doc(Document.initialize(path),  annotation_docset_name)
        
    def run_script(self, script_name: str, *args: List[str]) -> Any:
        
        if script_name in self.scripts:
            script = import_module(script_name)
            return script.run(self, *args)
        else:
            raise InvalidParameters(f"Script {script_name} not found in scripts directory")
    
    def _get_scripts(self):
        scripts = []
        for file in (self.corpus_folder_path / CORPUS_SCRIPTS).iterdir():
            if file.suffix == '.py':
                #append file name whthout extension to scripts list
                scripts.append(file.stem)
        return scripts
    
def create_corpus(corpus_dir_path: Path, config_parser: ConfigParser) -> CorpusConfig:
    
    # write configuration to .ini file
    config_file_path = corpus_dir_path /CORPUS_INI
    with open(config_file_path, 'w') as configfile:
        config_parser.write(configfile)

    #create db file in corpus
    db_file_path = corpus_dir_path / CORPUS_STATE_DB
    annotations_path = corpus_dir_path / CORPUS_ANNOTATIONS
    scripts_path = corpus_dir_path /CORPUS_SCRIPTS
    
    create_db(db_file_path)
    ensure_dir_path_exists(annotations_path)
    ensure_dir_path_exists(scripts_path)
    
    return get_config(config_file_path)
    
def ensure_dir_path_exists(path: Path):
    """
    Ensures that the directory at the given path exists.
    If the directory does not exist, it is created.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)