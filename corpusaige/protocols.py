
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules

from typing import Protocol


class Output(Protocol):
   
    @property
    def paged_printing(self)-> bool:
        """Paged printing of text to the screen if needed/possible"""
        ... 
    @paged_printing.setter
    def paged_printing(self, paging: bool)-> None:
        """Paged printing of text to the screen if needed/possible"""
        ...
    def print(self, text:str):
        """Print text to the screen"""
        ...
        
    def clear(self):
        """Clear the screen"""
        ...
        

class Input(Protocol):
    
    def prompt(self, prompt: str) -> str:
        """Prompt for input"""
        ...