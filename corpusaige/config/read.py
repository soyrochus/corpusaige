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
from typing import Dict, TypeAlias

from corpusaige.config import CORPUS_INI

from ..exceptions import InvalidConfigSection

ConfigEntries : TypeAlias = Dict[str,str]
class CorpusConfig:
    config_path: Path
    config: configparser.ConfigParser
    
    def __init__(self, config_path: Path | str):
        if isinstance(config_path, str):
            config_path = Path(config_path)
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

    def resolve_path_to_config(self, path: str | Path) -> Path:
        if isinstance(path, str):
            path = Path(path)   
        if path.exists():
            return path.absolute()
        else:
            return (self.get_config_dir() / path).absolute()
    
    def get_config_dir(self) -> Path:
        return self.config_path.parent
    
    def get_all_data_section_configs(self) -> Dict[str, ConfigEntries]:
        configs: dict[str, ConfigEntries] = {}
        for key, value in self.data_section_configs.items():
            configs[key] = dict(value.items())
        return configs

def get_config(config_path: str | Path) -> CorpusConfig:
   
    if isinstance(config_path, str):
        config_path = Path(config_path)
        
    if config_path.is_dir():
        config_path = config_path / CORPUS_INI
    
    config_path = config_path.absolute()
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    return CorpusConfig(config_path)
