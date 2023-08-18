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

from sqlalchemy import Engine
from sqlalchemy.orm.session import Session
from corpusaige.data import annotations, conversations
from corpusaige.data.db import create_db, init_db
from corpusaige.documentset import Document, DocumentSet
from corpusaige.exceptions import InvalidParameters
from corpusaige.interactions import StatefullInteraction
from corpusaige.protocols import Output
from corpusaige.storage import VectorRepository
from .config.read import CorpusConfig, get_config
from corpusaige.config import CORPUS_INI, CORPUS_STATE_DB, CORPUS_ANNOTATIONS, CORPUS_SCRIPTS
from importlib import import_module

from corpusaige.data.conversations import Conversation, Interaction

class Corpus(Protocol):
    name: str
    path: Path
    show_sources: bool = False
    context_size: int = 15

    def send_prompt(self, prompt: str) -> str:
        ...

    def add_docset(self, docset: DocumentSet) -> None:
        ...

    def remove_docset(self, docset_name: str) -> None:
        ...
           
    def add_doc(self, doc: Document, docset_name: str) -> None:
        ...
        
    #def store_annotation(self, annotation_docset_name: str, annotation_file: str) -> None:
    def add_annotation(self, annotation_docset_name: str, title: str, cmdtext: str)-> None:
        ...
    
    def store_search(self, search_str: str) -> List[str]:
        ...

    #def store_ls(self, set_name: str) -> List[str]:
    def ls_docs(self, all_docs: bool = False, doc_set:str = '') -> List[str]:
        ...

    def get_conversations(self) -> List[Conversation]:
        ...
    
    def get_conversation(self, conversation_id: int) -> Conversation:
        ...

    def get_interaction(self, interaction_id: int) -> Interaction:
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
    
    def set_output(self, printer: Output):
       ...
        
    def run_script(self, script_name: str, *args) -> Any:
        ...


class BasicConsoleOutput(Output):
    def pprint(self, text:str, pause_page: bool =True):
       print(text)
            
    def print(self, text:str):
        print(text)
    
    def clear(self):
       pass
class StatefullCorpus(Corpus):

    name : str
    path : Path
    repository: VectorRepository
    out: Output
    last_conversation_id: int | None
    last_interaction_id: int | None

    def __init__(self, config: str | CorpusConfig,show_sources: bool = False, 
                                            context_size: int = 15):
       
        #if config is a string, get the config from the file
        if isinstance(config, str):
            config = get_config(config)
        
        self.name = config.name
        self.path = config.config_path
        self.show_sources = show_sources
        self.context_size = context_size
        self.repository = VectorRepository(config)
        self.interaction = StatefullInteraction(
            config, retriever=self.repository.as_retriever())
        
        self.out = BasicConsoleOutput()
        
        self.last_conversation_id = None
        self.last_interaction_id = None
        
        self.scripts = self._get_scripts()
        self._db_state_engine = init_db(self.state_db_path)
        #set import path to corpus scripts folder
        sys.path.append(str(self.corpus_folder_path / CORPUS_SCRIPTS))

    @property
    def state_db_path(self) -> Path:
        return self.path.parent / CORPUS_STATE_DB
    
    @property
    def state_db_engine(self) -> Engine:
        return self._db_state_engine
    
    @property
    def annotations_path(self) -> Path:
        return self.corpus_folder_path / CORPUS_ANNOTATIONS
    
    @property
    def corpus_folder_path(self) -> Path:
        return self.path.parent
    
    def send_prompt(self, prompt: str) -> str :
        
        with Session(self.state_db_engine) as session:
            answer = self.interaction.send_prompt(prompt, self.show_sources, self.context_size)
            self.last_conversation_id, self.last_interaction_id = conversations.add_interaction(session, self.last_conversation_id, prompt, answer)
    
        return answer

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

    def get_conversations(self) -> List[Conversation]:
        with Session(self.state_db_engine) as session:
            return conversations.get_conversations(session)
    
    def get_conversation(self, conversation_id: int) -> Conversation:
        with Session(self.state_db_engine) as session:
            return conversations.get_conversation_by_id(session, conversation_id)

    def get_interaction(self, interaction_id: int) -> Interaction:
        with Session(self.state_db_engine) as session:
            return conversations.get_interaction_by_id(session, interaction_id)
       
    # def store_annotation(self, annotation_docset_name: str, annotation_file: str) -> None:
    #     path = self.annotations_path / annotation_file
    #     self.add_doc(Document.initialize(path),  annotation_docset_name)
    
    def add_annotation(self, annotation_docset_name: str, title: str, cmdtext: str)-> None:
        
        with Session(self.state_db_engine) as session:    
            annotation_id, stored_file = annotations.add_annotation(session, self.annotations_path, title, cmdtext)
            path = self.annotations_path / stored_file
            self.add_doc(Document.initialize(path), annotation_docset_name)
    
    
    def set_output(self, output: Output):
        self.out = output
        
    def run_script(self, script_name: str, *args: List[str]) -> Any:
        
        if script_name in self.scripts:
            script = import_module(script_name)
            #connect 'print' function in script to printer.print redirecting output to active app
            script.print = self.out.print #type: ignore 
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