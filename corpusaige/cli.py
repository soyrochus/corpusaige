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
import sys
import traceback

from .corpus import Corpus, CorpusReader
from .repl import ChatRepl
from .config import CorpusConfig, get_config
from corpusaige import corpus

#print error with traceback if DEBUG is True
DEBUG = True
#DEBUG = False

def new_corpus(config: CorpusConfig, name: str):
    """
    Creates a new corpus with the given name.
    """
    # Implementation goes here
    pass


def add_files(config: CorpusConfig, file_types, path_glob):
    """
    Adds files of the given type(s) and path/glob to the corpus.
    """
    # Implementation goes here
    pass


def shell(corpus: Corpus):
    """
    Displays the Corpusaige shell help message.
    """
    # Implementation goes here
    ChatRepl(corpus).run()

def main():
    
    try:
        parser = argparse.ArgumentParser(
            prog='corpusaige', description='Corpusaige command line interface')
        subparsers = parser.add_subparsers(dest='command')

        # New corpus command
        new_parser = subparsers.add_parser('new', help='Create a new corpus')
        new_parser.add_argument('name', help='Name of the new corpus')

        # Add files command
        add_parser = subparsers.add_parser('add', help='Add files to a corpus')
        add_parser.add_argument('-t', '--file-types',
                                nargs='+', help='File types to add')
        add_parser.add_argument(
            'path_glob', help='Path or glob pattern of files to add')

        # Shell command
        shell_parser = subparsers.add_parser('shell', help='Display the Corpusaige Shell')

        # Global optional parameter
        parser.add_argument('-p', '--path', default='corpus.ini', help='Path to corpus (default: current dir)')
        
        args = parser.parse_args(sys.argv[1:])

        # If no command is provided, print help message and exit
        if args.command is None:
            parser.print_help()
            exit()
   
        config = get_config(args.path)
        if args.command == 'new':
            new_corpus(config, args.name)
        elif args.command == 'add':
            add_files(config, args.file_types, args.path_glob)
        elif args.command == 'shell':
            shell(CorpusReader(config))

    except(Exception) as error:
        if DEBUG:
            #print error with traceback if DEBUG is True
            print(traceback.format_exc())
        else:
            print(error)
        exit(1)