#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy import  func, ForeignKey, select
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
from sqlalchemy.orm import Session
from corpusaige.data import Base

class Interaction(Base):
    __tablename__ = "interaction"
    id : Mapped[int] = mapped_column(primary_key=True)   #,increment=True)
    conversation_id = mapped_column(ForeignKey("conversation.id"))
    human_question: Mapped[str] 
    date_question : Mapped[datetime]= mapped_column(insert_default=func.now()) #type: ignore
    ai_answer : Mapped[Optional[str]] 
    date_answer: Mapped[Optional[datetime]]   #type: ignore
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="interactions")  # Changed "addresses" to "conversation" and "interaction" to "interactions"

    def __repr__(self):
        return f"<Interaction(id={self.id!r})>"  #user_id={self.user_id!r}, text={self.text!r})>"
    
    def set_answer(self, answer: str)-> None:  
         self.ai_answer = answer
         self.date_answer = datetime.now()
        
class Conversation(Base):
    __tablename__ = "conversation"
    id : Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    date_created: Mapped[datetime] = mapped_column(insert_default=func.now()) #type: ignore
    interactions: Mapped[List["Interaction"]] = relationship("Interaction", back_populates="conversation")  # Corrected "interaction" to "conversation"

    def __repr__(self):
        return f"<Interaction(id={self.id!r}, {self.title})>"  
    
def remove_whitespace(s):
    """Remove all whitespace characters apart from spaces from a string"""
    return s.translate(str.maketrans('', '', '\n\t\r\v\f'))

def add_interaction(session: Session, conversation_id: int | None, question: str, answer: str) -> Tuple[int, int]:
    
    question_stripped = remove_whitespace(question[:50]).strip()
    if conversation_id is None:
        conversation = Conversation(title=f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: {question_stripped}")
        session.add(conversation)
    else:
        conversation = session.execute(select(Conversation).where(Conversation.id == conversation_id)).scalar_one()
    
    interaction = Interaction(human_question=question, ai_answer=answer)
    conversation.interactions.append(interaction)
    session.commit()
    return conversation.id, interaction.id

def get_conversations(session) -> List[Conversation]:
    """Get all conversations from the database"""
    return session.execute(select(Conversation).order_by(Conversation.date_created)).scalars().all()

def get_conversation_by_id(session, id: int) -> Conversation:
    """Get a conversation by its id"""
    return session.execute(select(Conversation).where(Conversation.id == id)).scalar_one()  

def get_interaction_by_id(session, id: int) -> Interaction:
    """Get an interaction by its id"""
    return session.execute(select(Interaction).where(Interaction.id == id)).scalar_one()    