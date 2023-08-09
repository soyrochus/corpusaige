#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from corpusaige.data import annotations, conversations
from corpusaige.data.conversations import Base, Conversation, Interaction
from sqlalchemy import select
import tempfile

def fill_database(session):
    # Add test data to the session
    # create 2 conversations each with several interactions
    conversation1 = Conversation(title='First Conversation')
    
    interaction = Interaction(human_question='Hello?')
    interaction.set_answer('--- the sound of silence ---')
    conversation1.interactions.append(interaction)                                         
    conversation1.interactions.append(Interaction(human_question='Anyone? Hello?'))
    #save the conversation to the database
    
    conversation2 = Conversation(title='HALawakening')
    interaction = Interaction(human_question='Are you fallable, HAL?')
    interaction.set_answer("""No 9000 computer has ever made a mistake or distorted information. 
    We are all, by any practical definition of the words, foolproof and incapable of error.""")
    
  
    conversation2.interactions.append(interaction)                                         
    conversation2.interactions.append(Interaction(human_question='Anyone? Hello?'))
    
    session.add(conversation1)
    session.add(conversation2)
    session.commit()

    
# fixture to set up the SQLAlchemy session
@pytest.fixture
def session():
    # setup
    engine = create_engine('sqlite:///:memory:')  # Use SQLite in-memory database for testing
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    fill_database(session)  # fill the database with test data
    
    yield session  # this is where the testing happens!

    # teardown
    session.close()
    Base.metadata.drop_all(engine)


def test_conversation_present(session):
    # Your test will go here. session is a new SQLAlchemy session connected to a fresh
    # database each time you run your tests.
    lst = session.execute(select(Conversation).order_by(Conversation.date_created)).scalars().all()
    assert len(lst) == 2
    assert len(lst[0].interactions) == 2
    assert lst[0].interactions[0].human_question == 'Hello?'
    assert lst[1].interactions[0].human_question == 'Are you fallable, HAL?'
    assert lst[0].title == 'First Conversation'
    assert lst[1].title == 'HALawakening'

def test_conversation_ordered(session):
    hal_conversation = session.execute(select(Conversation).where(Conversation.title == 'HALawakening'))
    assert hal_conversation.scalar_one().title == 'HALawakening'
    
def test_add_conversation(session):
    
    conversation_id, interaction_id = conversations.add_interaction(session, None, 'Hola?', '¿Quienes? ¿Quienes?')
    assert conversation_id == 3
    assert interaction_id == 5
    lst = session.execute(select(Conversation).order_by(Conversation.date_created)).scalars().all()
    assert lst[2].interactions[0].human_question == 'Hola?'
    assert lst[2].interactions[0].ai_answer == '¿Quienes? ¿Quienes?'


def test_add_annotation(session):
    #get temporary directory path
    path = tempfile.gettempdir()
    id, name = annotations.add_annotation(session, path,  'Title of the Annotation', 'This is the text of the annotation')
    assert os.path.exists(os.path.join(path, name))
    
    annot = annotations.get_annotation_by_id(session, id)
    assert annot.title == 'Title of the Annotation'
    assert annot.text == 'This is the text of the annotation'
    