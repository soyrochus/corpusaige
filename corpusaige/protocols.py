
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


class Printer(Protocol):
    def pprint(self, text:str, pause_page: bool =True):
        """Print text to the screen, optionally pausing after each page"""
        ...
            
    def print(self, text:str):
        """Print text to the screen"""
        ...