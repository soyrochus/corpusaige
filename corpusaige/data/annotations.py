#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

import os
from sqlalchemy import ForeignKey, select, func
from corpusaige.documentset import Document
from sqlalchemy.orm import mapped_column, Mapped, relationship, Session
from typing import List, Optional, Tuple
from corpusaige.interactions import Interaction
from .db import Base
from datetime import datetime


class Annotation(Base):
    __tablename__ = 'annotation'
    
    id : Mapped[int] = mapped_column(primary_key=True)  
    interaction_id = mapped_column(ForeignKey("interaction.id"))
    title: Mapped[str] 
    text: Mapped[str]
    date : Mapped[datetime]= mapped_column(insert_default=func.now()) #type: ignore
   
   
    def __repr__(self):
        return f"<Annotation(id={self.id!r}, text={self.title!r})>"
    
    def export(self, path) -> dict:
        with open(os.path.join(path, f"{self.title}.txt"), "w") as f:
                f.write(self.text)
                f.close()
            
def add_annotation(session: Session, export_path: str, title:str, text:str, interaction_id: int | None = None) ->  int:
    annotation = Annotation(title=title, text=text, interaction_id=interaction_id)
    session.add(annotation)
    session.commit()
    
    annotation.export(export_path)
    return annotation.id

def get_annotation_by_id(session: Session, annotation_id: int) -> Annotation:
    return session.execute(select(Annotation).where(Annotation.id == annotation_id)).scalar_one()