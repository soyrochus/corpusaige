#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
import argparse
import os
import sys
import traceback
from typing import List
from corpusaige.data.db import init_db
from corpusaige.providers import create_local_vectordb
from .corpus import Corpus, StatefullCorpus
from .repl import PromptRepl
from .config.read import CorpusConfig, get_config
from .config.create import prompt_user_for_init
from corpusaige import corpus
from .documentset import DocumentSet

#print error with traceback if DEBUG is True
DEBUG = True
#DEBUG = False

def new_corpus(name: str, path: str):
    """
    Creates a new corpus using a wizzard
    """
    new_path = os.path.abspath(os.path.join(path, name))
    ensure_path_exists(new_path)
    config = prompt_user_for_init(name, new_path)
    create_local_vectordb(config)
 
    print(f"\nCorpus {name} created successfully in {new_path}.")
    print("Please add files to the corpus using the 'add' command.")

def add_docset(config: CorpusConfig, name: str, doc_paths: List[str], doc_types: List[str], recursive: bool):
    """
    Adds files of the given type(s) and path/glob to the corpus.
    """
    # Implementation goes here
    docset = DocumentSet.initialize(name, doc_paths, doc_types, recursive)
    StatefullCorpus(config).add_docset(docset)
   

def shell(config: CorpusConfig):
    """
    Displays the Corpusaige shell for the given corpus.
    """
    corpus = StatefullCorpus(config)
    corpus_path = corpus.path

    _, db_state_session = init_db(corpus.state_db_path)
    PromptRepl(corpus, db_state_session).run()

def cli_run():
    parser = argparse.ArgumentParser(
        prog='crpsg (or python -m corpusaige)', description='Corpusaige command line interface',
        exit_on_error=False, add_help=True, allow_abbrev=True)
    subparsers = parser.add_subparsers(dest='command')

    # New corpus command
    new_parser = subparsers.add_parser('new', help='Create a new corpus')
    new_parser.add_argument('name', help='Name of the new corpus')

    # Add files command
    add_parser = subparsers.add_parser('add', help='Add a document set (i.e. files) to a corpus')
    add_parser.add_argument('-r', '--recursive', action='store_true', help='Recursively add files')
    add_parser.add_argument('-t', '--doc-types', nargs='+', required=True, help='Document (File) types to add')
    add_parser.add_argument('-p', '--doc-paths', nargs='+', required=True, help='(root) Path containing documents to add')
    add_parser.add_argument('-n', '--name', required=True, help='Name for document set')
    
    # Shell command
    shell_parser = subparsers.add_parser('shell', help='Display the Corpusaige Shell')

    # Global optional parameter
    parser.add_argument('-p', '--path', default='.', help='Path to corpus (default: current dir)')
    
    args = parser.parse_args(sys.argv[1:])

    # If no command is provided, print help message and exit
    if args.command is None:
        parser.print_help()
        exit()

    if args.command == 'new':
        new_corpus(args.name, args.path)
    elif args.command == 'add':
        config = get_config(args.path)
        add_docset(config, args.name, args.doc_paths, args.doc_types, args.recursive)
    elif args.command == 'shell':
        config = get_config(args.path)
        shell(config)

    
def main():
    
    try:
        cli_run()  
    except(Exception) as error:
        if DEBUG:
            #print error with traceback if DEBUG is True
            print(traceback.format_exc())
        else:
            print(error)
        exit(1)
        
def ensure_path_exists(path):
    """
    Ensures that the directory at the given path exists.
    If the directory does not exist, it is created.
    """
    if not os.path.exists(path):
        os.makedirs(path)