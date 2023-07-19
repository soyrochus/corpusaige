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
from typing import List, Dict, Any

class CorpusConfig:

    def __init__(self, config_path: str):
        self.config_path = Path(config_path).absolute()
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)
        
        self.main = self.config["main"]
        self.name = self.main["name"]
        self.llm = self.main["llm"]
        self.vector_db = self.main["vector-db"]
        self.data_sections = self.main["data-sections"].split(",")
        
        self.llm_config = self.config[self.llm]
        self.vector_db_config = self.config[self.vector_db]
        self.data_section_configs = {section: self.config[section] for section in self.data_sections}

    def get_llm_config(self) -> Dict[str, Any]:
        return dict(self.llm_config.items())
        
    def get_vector_db_config(self) -> Dict[str, Any]:
        return dict(self.vector_db_config.items())
        
    def get_data_section_config(self, section: str) -> Dict[str, Any]:
        return self.data_section_configs.get(section, {})

    def get_all_data_section_configs(self) -> Dict[str, Dict[str, Any]]:
        return self.data_section_configs


def get_config(config_path: str = "corpus.ini") -> CorpusConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if os.path.isdir(config_path):
        config_path = os.path.join(config_path, "corpus.ini")

    return CorpusConfig(config_path)
