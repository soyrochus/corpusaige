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
from typing import List, Optional, Tuple
from sqlalchemy import func, ForeignKey, select
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase  
from sqlalchemy.orm import mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    pass

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
        return f"<Interaction(id={self.id!r})>"  
    
    
# def get_conversations(session, conversation_id: int) -> Tuple[Conversation, List[Interaction]]:
#     """Return a single conversation and all its interactions. Use the select syntax to join the tables."""
#     stmt = select(Conversation).join(Interaction).filter(Conversation.id == conversation_id)
#     result = session.execute(stmt).one()
#     return result.Conversation, result.Interaction