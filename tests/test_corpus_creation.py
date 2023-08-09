#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules

#A Test to validate the creation of a Corpus with all items it creates in its directory (ini file, annotations and script dirs etc)


import configparser
import os
import pytest

from corpusaige.config.create import create_corpus
from corpusaige.config.read import get_config


corpus_ini_str = """[main]
name = Test Corpus
llm = openai
vector-db = chroma
data-sections = 

[openai]
api-key = sk-f4k3key4t3sting
llm-model = gpt-4
embedding-model = text-embedding-ada-002

[chroma]
type = local
path = ./db

"""
@pytest.fixture(scope="session")
def corpus_dir(tmpdir_factory):
    corpus_dir_path = tmpdir_factory.mktemp("corpus")
    config_p = configparser.ConfigParser()
    config_p.read_string(corpus_ini_str)
    config = create_corpus(corpus_dir_path, config_p)
    
    return corpus_dir_path
    
def test_create_corpus(corpus_dir:str):
    config = get_config(corpus_dir)
    assert config.main['name'] == "Test Corpus"
    assert config.main['llm'] == "openai"
    
    assert os.path.exists(os.path.join(corpus_dir, 'corpus-state.db'))
    assert os.path.exists(os.path.join(corpus_dir, 'annotations'))
    assert os.path.exists(os.path.join(corpus_dir, 'scripts'))
