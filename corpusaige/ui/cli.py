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
from pathlib import Path
import sys
import tkinter as tk
import traceback
from typing import List
from corpusaige.exceptions import InvalidParameters
from corpusaige.ui.console_tools import is_data_available
from corpusaige.ui.gui import GuiApp
from corpusaige.providers import create_local_vectordb
from corpusaige.ui.shell import ShellApp
from ..corpus import StatefullCorpus, create_corpus, ensure_dir_path_exists
from .repl import PromptRepl
from ..config.read import CorpusConfig, get_config
from ..config.create import prompt_user_for_init
from ..documentset import DocumentSet
from ..app_meta_data import AppMetaData

#print error with traceback if DEBUG is True
DEBUG = True
#DEBUG = False



def new_corpus(name: str, path: Path):
    """
    Creates a new corpus using a wizzard
    """
    corpus_path = (path / name).absolute()
    ensure_dir_path_exists(corpus_path)
    config_parser = prompt_user_for_init()
    print(f"Creating new corpus {name} at {corpus_path}")
    config = create_corpus(corpus_path, config_parser)
    #TODO replace with more generic factory functions based on config
    create_local_vectordb(config)
 
    print(f"\nCorpus {name} created successfully in {corpus_path}.")
    print("Please add files to the corpus using the 'add' command.")

def add_docset(config: CorpusConfig, name: str, doc_paths: List[Path | str], doc_types: List[str], recursive: bool):
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

    prompt = PromptRepl(corpus)
    ShellApp(prompt, DEBUG).run()
    
def gui(config: CorpusConfig):
    """
    Displays the Corpusaige gui for the given corpus.
    """
    root = tk.Tk()
    corpus = StatefullCorpus(config)
    prompt = PromptRepl(corpus)
    GuiApp(root, prompt, True).run()
    
def remove(config: CorpusConfig, docset_name: str, force: bool):
    """
    Remove the doc_set with the given name.
    """
    corpus = StatefullCorpus(config)
    if force or input(f"Are you sure you want to remove {docset_name}? (y/n)").lower() == "y":
        corpus.remove_docset(docset_name)
    else:
        print("Remove cancelled.")    

def prompt(config: CorpusConfig, read: bool, line: str):
    """Send prompt (not repl command) to corpus/AI."""
    if read and line:
        raise InvalidParameters("Cannot use both --read and --line")
    elif not read and not line:
        raise InvalidParameters("Must use either --read or --line")
    
    if read and is_data_available(0):
            input_str = sys.stdin.read()
    elif line:
        input_str = line
    else:
        raise InvalidParameters("No data available on stdin")
        
    corpus = StatefullCorpus(config)
    print(f"Prompt: {input_str}")
    print(f"Result: {corpus.send_prompt(input_str)}")
    
    
def cli_run():
    
    app_meta_data = AppMetaData()
    
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
    
    # remove files command
    rm_parser = subparsers.add_parser('remove', help='Remove a document set (i.e. files) from a corpus')
    rm_parser.add_argument('-f', '--force', action='store_true', help='Do not ask for confirmation')
    rm_parser.add_argument('-n', '--name', required=True, help='Name for document set')
    
    # Shell command
    subparsers.add_parser('shell', help='Display the Corpusaige Shell (console)')

     # Gui command
    subparsers.add_parser('gui', help='Display the Corpusaige Gui')

    # Send prompt command
    prompt_parser = subparsers.add_parser('prompt', help='Send prompt (not repl command) to corpus/AI.')
    prompt_parser.add_argument('-r', '--read', action='store_true', help='Read from stdin')
    prompt_parser.add_argument('-l', '--line', help='Send a single git line')

    # Global optional parameter
    parser.add_argument('-p', '--path', default='.', help='Path to corpus (default: current dir)')
    
    parser.add_argument('-v', '--version', action='version', version=f'{app_meta_data.name} {app_meta_data.version}')
  
    args = parser.parse_args(sys.argv[1:])

    # Execute the command
    match args.command:
        case 'new':
            new_corpus(args.name, args.path)
        case 'add':
            config = get_config(args.path)
            add_docset(config, args.name, args.doc_paths, args.doc_types, args.recursive)
        case 'shell':
            config = get_config(args.path)
            shell(config)
        case 'gui':
            config = get_config(args.path)
            gui(config)
        case 'remove':
            config = get_config(args.path)
            remove(config, args.name, args.force)
        case 'prompt':
            config = get_config(args.path)
            prompt(config, args.read, args.line)
        case _:
            # If no command is provided, print help message and exit
            parser.print_help()
            exit()
        
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
        
