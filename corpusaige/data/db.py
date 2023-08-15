#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

from pathlib import Path
from sqlalchemy import Engine, create_engine
from corpusaige.data import Base
from corpusaige.data.conversations import Interaction, Conversation # noqa: F401 - ignore Not used
from corpusaige.data.annotations import Annotation # noqa: F401 - ignore Not Used 


def create_db(path: Path)-> Engine:
    # Connect to the database. If it doesn't exist, it will be created.
    engine = create_engine(f'sqlite:///{path}')

    # Create tables in the database
    Base.metadata.create_all(engine)
    
    return engine

def init_db(path: Path)-> Engine:
    # Connect to the database
    engine = create_engine(f'sqlite:///{path}')
    
    return engine


if __name__ == "__main__":
    import sys
    create_db(Path(sys.argv[1]))