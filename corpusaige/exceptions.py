#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules


class InvalidConfigSection(ValueError):
    pass

class InvalidConfigEntry(ValueError):
    pass

class InvalidProviderConfig(ValueError):
    pass

class InvalidParameters(ValueError):
    pass
