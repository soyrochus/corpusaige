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
from pathlib import Path
import pytest
from corpusaige.config import CORPUS_SCRIPTS

from corpusaige.config.read import get_config
from corpusaige.corpus import StatefullCorpus, create_corpus


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
test_script_str = """# Test Script

def run(corpus, *args):
    return corpus.name
    
"""

@pytest.fixture(scope="session")
def corpus_dir(tmpdir_factory):
    corpus_dir_path = Path(tmpdir_factory.mktemp("corpus"))
    config_p = configparser.ConfigParser()
    config_p.read_string(corpus_ini_str)
    config = create_corpus(corpus_dir_path, config_p)
    
    with open(corpus_dir_path / CORPUS_SCRIPTS / 'simple_test_script.py', 'w') as f:
        f.write(test_script_str)
        
    return corpus_dir_path
    
def test_create_corpus(corpus_dir:Path):
    config = get_config(corpus_dir)
    assert config.main['name'] == "Test Corpus"
    assert config.main['llm'] == "openai"
    
    assert (corpus_dir / 'corpus-state.db').exists()
    assert (corpus_dir / corpus_dir / 'annotations').exists()
    assert (corpus_dir / corpus_dir / 'scripts').exists()

class DummyPrinter:

    def print(self, *args, **kwargs):
        print(*args, **kwargs)
        
def test_run_script(corpus_dir):
    corpus = StatefullCorpus(get_config(corpus_dir))
    corpus.out = DummyPrinter()
    assert corpus.run_script('simple_test_script') == "Test Corpus"