#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .conversations import Base

def create_db(path)-> Engine:
    # Connect to the database. If it doesn't exist, it will be created.
    engine = create_engine(f'sqlite:///{path}')

    # Create tables in the database
    Base.metadata.create_all(engine)
    
    return engine

def init_db(path)-> Engine:
    # Connect to the database
    engine = create_engine(f'sqlite:///{path}')
    
    return engine