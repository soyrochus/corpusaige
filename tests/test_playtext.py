#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

from corpusaige.ui.audio.text_handling import get_sentences


def test_text_handling():
    assert get_sentences("The sentence is ") == ("", "The sentence is ") 
    
    assert get_sentences("The sentence is done.") == ("The sentence is done.", "") 
    
    assert get_sentences("The sentence is done. And this one?") == ("The sentence is done. And this one?", "") 
    
    assert get_sentences("The sentence is done. And this one? Further more") == ("The sentence is done. And this one?", "Further more") 
    
    
    