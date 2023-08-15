#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules

import configparser
from pathlib import Path
from corpusaige.corpus import create_corpus, ensure_dir_path_exists

corpus_ini_str = """[main]
name = Test Corpus
llm = openai
vector-db = chroma
data-sections = 

[openai]
api-key = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
llm-model = gpt-4
embedding-model = text-embedding-ada-002

[chroma]
type = local
path = ./db

"""


if __name__ == '__main__':
    #get directory in which script is located
    script_dir = Path(__file__).resolve().parent
    
    corpus_dir_path = script_dir / "assets" / "test-corpus"
    ensure_dir_path_exists(corpus_dir_path)
    
    config_p = configparser.ConfigParser()
    config_p.read_string(corpus_ini_str)
    config = create_corpus(corpus_dir_path, config_p)
    
    