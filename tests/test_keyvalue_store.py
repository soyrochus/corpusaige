#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

from dataclasses import dataclass
from enum import Enum
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from corpusaige.data.conversations import Base
from corpusaige.data.keyvalue_store import get, put, delete

# fixture to set up the SQLAlchemy session
@pytest.fixture
def session():
    # setup
    engine = create_engine('sqlite:///:memory:')  # Use SQLite in-memory database for testing
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    #fill_database(session)  # fill the database with test data
    
    yield session  # this is where the testing happens!

    # teardown
    session.close()
    Base.metadata.drop_all(engine)

def test_simple_keyvalue_operations(session):
    
    put(session, "sampleKey", {"data": "sampleData"})
    assert get(session, "sampleKey") == {"data": "sampleData"}
    delete(session, "sampleKey")
    assert get(session, "sampleKey") is None


class Animal(Enum):
    CAT = 1
    DOG = 2
    BIRD = 3
    OTHER = 4

@dataclass    
class Pet:
    name: str
    type: Animal
    age: int
    
def test_persisting_complex_data(session):
    
    put(session, "dog", Pet("Fido", Animal.DOG, 3))
    put(session, "other", Pet("Floppy", Animal.OTHER, 1))
    
    
    assert get(session, "dog") != get(session, "other")
    assert get(session, "dog") == get(session, "dog")
     
    delete(session, "dog")
    assert get(session, "dog") is None