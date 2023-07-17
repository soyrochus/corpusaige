#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
import cmd

class CorpusaigeShell(cmd.Cmd):
    prompt = 'Corpusaige> '

    def default(self, line):
        """The default method called when a command is not recognized."""
        print(f'Unknown command: {line}')

    def do_exit(self, arg):
        """Exit the shell."""
        return True

