
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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from corpusaige.conversations import Base

# fixture to set up the SQLAlchemy session
@pytest.fixture
def session():
    # setup
    clear_mappers()
    engine = create_engine('sqlite:///:memory:')  # Use SQLite in-memory database for testing
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session  # this is where the testing happens!

    # teardown
    session.close()
    Base.metadata.drop_all(engine)

# Use this fixture in your tests like so:
def test_example(session):
    # Your test will go here. session is a new SQLAlchemy session connected to a fresh
    # database each time you run your tests.
    pass


