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
from sqlalchemy import func, ForeignKey
from sqlalchemy import Integer, String, UnicodeText
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped, relationship

class Base(DeclarativeBase):
    pass

class Interaction(Base):
    __tablename__ = "interaction"
    id : Mapped[int] = mapped_column(primary_key=True)
    conversation_id = mapped_column(ForeignKey("conversation.id"))
    human_quesion: Mapped[str] # mapped_column(UnicodeText)
    date_question : Mapped[datetime]= mapped_column(insert_default=func.now()) #type: ignore
    ai_answer : Mapped[Optional[str]]# = mapped_column(UnicodeText)
    date_answer: Mapped[Optional[datetime]] # mapped_column(insert_default=func.now())   #type: ignore
    addresses: Mapped[List["Conversation"]] = relationship(back_populates="interaction")
    
class Conversation(Base):
    __tablename__ = "conversation"
        
    id : Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    interactions: Mapped[List["Interaction"]] = relationship("Interaction", back_populates="conversation")
    

        
