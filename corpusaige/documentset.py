#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
from enum import Enum
import os
from typing import List, Tuple, Union
#from datetime import datetime

class FileType(Enum):
    TEXT = 'Text'
    MSWORD = 'MSWord'
    PDF = 'Pdf'
    MSEXCEL = 'MSExcel'
    
    @classmethod 
    def get_default_ext(cls, ft: 'FileType')-> str:
        map = {'TEXT': 'txt', 'MSWORD': 'docx', 'PDF': 'pdf', 'MSEXCEL': 'xlsx'}
        return map[ft.name]
        
    @classmethod
    def from_string(cls, s: str) -> 'FileType':
        try:
            return cls[s.upper()]
        except KeyError:
            raise ValueError(f'Invalid FileType: {s}')

    @classmethod
    def parse_file_type_ext(cls, file_type_ext: str) ->  Tuple['FileType', str]:
        parts = file_type_ext.split(':')

        file_type = FileType.from_string(parts[0])
        file_extension = parts[1] if len(parts) > 1 else FileType.get_default_ext(file_type)
        return file_type, file_extension

#
class Entry:
    def __init__(self, path: str, file_type: FileType, file_extension: str, recursive: bool):
        self.path = path
        self.file_type = file_type
        self.file_extension = file_extension
        self.recursive = recursive
        
    @staticmethod
    def create_Entry(path: str, file_type_ext: str, recursive: bool, delay_validation=False) -> 'Entry':
        
        _path = os.path.abspath(path)
        
        if not delay_validation and not os.path.isdir(_path) and not os.path.exists(_path):
            raise ValueError(f'Invalid path: {_path}')
        
        _file_type, _file_ext = FileType.parse_file_type_ext(file_type_ext)
        
        return Entry(path,_file_type, _file_ext, recursive)
        
class DocumentSet:
    def __init__(self, name: str):
        self.name = name
        self.entries: List[Entry] = []

    def add_entry(self, entry: Entry):
        self.entries.append(entry)

    def add_entries(self, entries: Union[List[Entry], Entry]):
        if isinstance(entries, list):
            self.entries.extend(entries)
        else:
            self.add_entry(entries)
            
    @classmethod
    def initialize(cls, name: str, doc_paths: List[str], doc_types: List[str], recursive: bool)-> 'DocumentSet':
        docset = DocumentSet(name)
        for doc_path in doc_paths:
            for doc_type in doc_types:
                docset.add_entry(Entry.create_Entry(doc_path, doc_type, recursive))
        return docset