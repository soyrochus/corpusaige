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
from corpusaige.config.read import get_config
from corpusaige.ui.console_tools import zip_dir
from corpusaige.corpus import StatefullCorpus
from corpusaige.documentset import DocumentSet


if __name__ == '__main__':
    #get directory in which script is located
    script_dir = Path(__file__).parent.resolve()
    
    corpus_dir_path = script_dir / "assets" / "test-corpus"
    
    config = get_config(corpus_dir_path)
    corpus = StatefullCorpus(config)
    
    rust_book_path = script_dir.parent / "test-case" / "book" / "src"
    rust_book_docset = DocumentSet.initialize("Rust Book", [rust_book_path], ["text:md"], False)
    corpus.add_docset(rust_book_docset)
    print(rust_book_docset)
    
    rbe_path = script_dir.parent / "test-case" / "rust-by-example" / "src"
    rbe_docset = DocumentSet.initialize("Rust by Example", [rbe_path], ["text:md"], True)
    corpus.add_docset(rbe_docset)
    print(rbe_docset)
    
    zip_dir(corpus_dir_path / "db", corpus_dir_path.parent / "chromadb.zip")
    print("Done")