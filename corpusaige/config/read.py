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
import os
from pathlib import Path
from typing import List, Dict, Any, TypeAlias

from ..exceptions import InvalidConfigSection

ConfigEntries : TypeAlias = Dict[str,str]
class CorpusConfig:

    def __init__(self, config_path: str):
        self.config_path = Path(config_path).absolute()
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)
        
        self.main = self.config["main"]
        self.name = self.main["name"]
        self.llm = self.main["llm"]
        self.vector_db = self.main["vector-db"]
        sections = self.main["data-sections"]
        if not sections:
            self.data_sections = []
        else:
            self.data_sections = self.main["data-sections"].split(",")
        
        self.llm_config = self.config[self.llm]
        self.vector_db_config = self.config[self.vector_db]
        self.data_section_configs = {section: self.config[section] for section in self.data_sections}

    def get_llm_config(self) -> ConfigEntries:
        return dict(self.llm_config.items())
        
    def get_vector_db_config(self) -> ConfigEntries:
        return dict(self.vector_db_config.items())
        
    def get_data_section_config(self, section: str) -> ConfigEntries:
        entries = self.data_section_configs.get(section)
        if entries is None:
            raise InvalidConfigSection(f"Invalid data section: {section}")
        else: 
            return dict(entries.items())

    def resolve_path_to_config(self, path: str) -> str:
        if os.path.exists(path):
            return os.path.abspath(path)
        else:
            return os.path.abspath(os.path.join(self.get_config_dir(), path))
    
    def get_config_dir(self) -> str:
        return os.path.dirname(self.config_path)
    
    def get_all_data_section_configs(self) -> Dict[str, ConfigEntries]:
        configs: dict[str, ConfigEntries] = {}
        for key, value in self.data_section_configs.items():
            configs[key] = dict(value.items())
        return configs

def get_config(config_path: str = "corpus.ini") -> CorpusConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if os.path.isdir(config_path):
        config_path = os.path.join(config_path, "corpus.ini")

    return CorpusConfig(config_path)
