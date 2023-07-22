#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules

import pytest
from pathlib import Path

from corpusaige.documentset import DocumentSet, Entry, FileType

path = Path(__file__).parent.absolute()

def test_from_string():
    assert FileType.from_string('text') == FileType.TEXT
    assert FileType.from_string('msword') == FileType.MSWORD
    with pytest.raises(ValueError):
        FileType.from_string('unknown')


def test_parse_file_type_ext():
    assert FileType.parse_file_type_ext('text') == (FileType.TEXT, 'txt')
    assert FileType.parse_file_type_ext('text:md') == (FileType.TEXT, 'md')
    assert FileType.parse_file_type_ext('msword:doc') == (FileType.MSWORD, 'doc')


def test_create_Entry():
    entry = Entry.create_Entry(path, 'text', True)
    assert entry.path == path
    assert entry.file_type == FileType.TEXT
    assert entry.file_extension == 'txt'
    assert entry.recursive is True
    
def test_valid_path():
    with pytest.raises(ValueError):
        Entry.create_Entry("q:/very/unlikely/to/exist", 'text', True)
    
    entry = Entry.create_Entry(path, 'text', True)
    assert entry.path == path

def test_add_entry():
    doc_set = DocumentSet('Test Set')
    entry = Entry.create_Entry(path, 'text:md', True)
    doc_set.add_entry(entry)
    assert entry in doc_set.entries


def test_add_entries():
    doc_set = DocumentSet('Test Set')
    entries = [Entry.create_Entry(f'{path}{i}', 'text', True, delay_validation=True) for i in range(3)]
    doc_set.add_entries(entries)
    assert doc_set.entries == entries

    single_entry = Entry.create_Entry(path, 'text', True)
    doc_set.add_entries(single_entry)
    assert single_entry in doc_set.entries
