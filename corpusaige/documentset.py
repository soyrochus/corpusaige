#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""
from __future__ import annotations  # hack to avoid error with pytest using OR operator in type hinting

# Import necessary modules
from enum import Enum
from pathlib import Path
from typing import List, Tuple, Union

from corpusaige.exceptions import InvalidParameters
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
            raise InvalidParameters(f'Invalid FileType: {s}')

    @classmethod
    def parse_file_type_ext(cls, file_type_ext: str) ->  Tuple['FileType', str]:
        parts = file_type_ext.split(':')

        file_type = FileType.from_string(parts[0])
        file_extension = parts[1] if len(parts) > 1 else FileType.get_default_ext(file_type)
        return file_type, file_extension

    @classmethod 
    def get_file_type(cls, ext:str)-> 'FileType' | None:
        map = {'.txt': FileType.TEXT, '.docx': FileType.MSWORD, '.pdf': FileType.PDF, '.xslx' : FileType.MSEXCEL}
        return map.get(ext, None)
        
    @classmethod
    def parse_type_from_path(cls, path: Path) -> 'FileType':
        #determine FileType from file extension
        file_extension = path.suffix
        fileType = cls.get_file_type(file_extension)
        if fileType is None:
            raise InvalidParameters(f'Invalid file extension: {file_extension}')
        return fileType
class Document:
    path:Path
    file_type: FileType
    
    def __init__(self, path: Path, file_type: FileType):
        self.path = path
        self.file_type  = file_type
    
    def path_relative_to(self, root_path: Path) -> Path:
        return self.path.relative_to(root_path)
                   
    @staticmethod
    def initialize(path: Path, delay_validation=False) -> 'Document':
        
        _path = path.absolute()
        
        if not delay_validation and not _path.exists():
            raise InvalidParameters(f'Invalid path: {_path}')
        
        _file_type = FileType.parse_type_from_path(_path)
        
        return Document(_path, _file_type)
    
class Entry:
    def __init__(self, path: Path, file_type: FileType, file_extension: str, recursive: bool):
        self.path = path
        self.file_type = file_type
        self.file_extension = file_extension
        self.recursive = recursive
    
    def path_relative_to(self, root_path: Path) -> Path:
        return self.path.relative_to(root_path)
                   
                   
    @staticmethod
    def create_Entry(path: Path, file_type_ext: str, recursive: bool, delay_validation=False) -> 'Entry':
        
        _path = path.absolute() 
        
        if not delay_validation and not _path.is_dir():
            raise InvalidParameters(f'Invalid path: {_path}')
        
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
    def initialize(cls, name: str, doc_paths: List[str | Path], doc_types: List[str], recursive: bool)-> 'DocumentSet':
        docset = DocumentSet(name)
        for doc_path in doc_paths:
            #if isinstance(doc_path, str):
            doc_path = Path(doc_path)
            for doc_type in doc_types:
                docset.add_entry(Entry.create_Entry(doc_path, doc_type, recursive))
        return docset
    
    