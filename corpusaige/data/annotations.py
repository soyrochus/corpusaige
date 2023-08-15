#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

import os
from sqlalchemy import select, func
from sqlalchemy.orm import mapped_column, Mapped, Session
from typing import Tuple
from corpusaige.data import Base
from datetime import datetime


class Annotation(Base):
    __tablename__ = 'annotation'
    
    id : Mapped[int] = mapped_column(primary_key=True)  
    title: Mapped[str] 
    text: Mapped[str]
    date : Mapped[datetime]= mapped_column(insert_default=func.now()) #type: ignore
   
   
    def __repr__(self):
        return f"<Annotation(id={self.id!r}, text={self.title!r})>"
    
    def export(self, path:str) -> Tuple[int, str]:
        fname = f"{self.title}.txt"
        
        with open(os.path.join(path, fname), "w") as f:
                f.write(self.text)
                f.close()
        return self.id, fname
            
def add_annotation(session: Session, export_path: str, title:str, text:str) ->  Tuple[int, str]:
    annotation = Annotation(title=title, text=text)
    session.add(annotation)
    session.commit()
    
    return annotation.export(export_path)
    
def get_annotation_by_id(session: Session, annotation_id: int) -> Annotation:
    return session.execute(select(Annotation).where(Annotation.id == annotation_id)).scalar_one()