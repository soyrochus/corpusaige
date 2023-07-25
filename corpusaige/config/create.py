#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

import os
import sys
from typing import Any
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import configparser

from corpusaige.config.read import CorpusConfig, get_config


def radiolist_dialog_with_params(title, text, values) -> str:
    # Model is chosen from a radiolist dialog
    model : Any = radiolist_dialog(
        title=title,
        text=text,
        ok_text="Select",
        cancel_text="Cancel",
        values=values,
        style=Style.from_dict({
            'dialog': 'bg:#000000 #ffffff',
            'dialog frame.label': 'bg:#000000 #ffffff',
            'dialog.body': 'bg:#000000 #ffffff',
            'dialog shadow': 'bg:#000000 #ffffff'
        })
    ).run()

    # If the user cancels the dialog, exit the program
    if model is None:
        print("User canceled operation. Exiting...")
        sys.exit(0)  # Exit the program

    return model


def prompt_user_for_init(name: str, corpus_path: str = './') -> CorpusConfig:

    print(f"Creating new corpus {name} at {corpus_path}")
    # create configparser object
    config = configparser.ConfigParser()

    # Main section
    name = prompt("Enter title/description of project: ")
    # ai_provider = prompt("Enter AI provider (openai, unspecified): ", completer=WordCompleter(['openai', 'unspecified']))
    # vector_db = prompt("Enter vector-db (chroma, unspecified): ", completer=WordCompleter(['chroma', 'unspecified']))
    ai_provider = radiolist_dialog_with_params("Select LLM Provider", "Select LLM Provider", [
                                               ("openai", "openai"), ("unspecified", "unspecified")])
    vector_db = radiolist_dialog_with_params("Select Vector DB", "Select Vector DB", [
                                             ("chroma", "chroma"), ("unspecified", "unspecified")])

    config['main'] = {'name': name, 'llm': ai_provider,
                      'vector-db': vector_db, 'data-sections': ''}

    # OpenAI section
    if ai_provider.lower() == 'openai':
        api_key = prompt("Enter OpenAI API Key (empty allowed): ")

        #llm_model = radiolist_dialog_with_params("Select Open AI llm-model", "Select llm-model", [(
        #    "gpt-3.5-turbo", "gpt-3.5-turbo"), ("unspecified", "unspecified")])
        
        llm_model = radiolist_dialog_with_params("Select Open AI llm-model", "Select llm-model", [(
            "gpt-4", "gpt-4"), ("unspecified", "unspecified")])
        
        embedding_model = radiolist_dialog_with_params("Select Open AI model", "Select model", [(
            "text-embedding-ada-002", "text-embedding-ada-002"), ("unspecified", "unspecified")])
       
        config['openai'] = {'api-key': api_key, 'llm-model': llm_model, 'embedding-model': embedding_model}

    # Chroma section
    if vector_db.lower() == 'chroma':
        # type_ = prompt("Enter type (local, unspecified): ", completer=WordCompleter(['local', 'unspecified']))
        type_ = radiolist_dialog_with_params("Select Chroma type", "Select type", [
                                             ("local", "local"), ("unspecified", "unspecified")])
        path = prompt("Enter path: ", default='./db')

        config['chroma'] = {'type': type_, 'path': path}

    # write configuration to .ini file
    config_file_path = os.path.join(corpus_path, 'corpus.ini')
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

    return get_config(config_file_path)
    