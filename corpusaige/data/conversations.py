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
from sqlalchemy import  func, ForeignKey, select
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase  
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

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
    

def add_interaction(session: Session, conversation_id: int, question: str, answer: str) -> Interaction:
    
    if conversation_id is None:
        conversation = Conversation(title=f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: {question[:30]}")
        session.add(conversation)
    else:
        conversation = session.execute(select(Conversation).where(Conversation.id == conversation_id)).scalar_one()
    
    conversation.interactions.append(Interaction(human_question=question, ai_answer=answer))
    session.commit()
    return conversation.id


