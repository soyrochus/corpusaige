#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
from prompt_toolkit.patch_stdout import patch_stdout
import threading
import time
from contextlib import contextmanager

@contextmanager
def spinner(prompt=""):
    def spin():
        if prompt:
            print(prompt)
            
        chars = "|/-\\"
        with patch_stdout():
            while not spinner_stop:
                for char in chars:
                    print('\r' + char, end='', flush=True)
                    time.sleep(0.1)
            print('\r ', end='', flush=True)

    spinner_stop = False
    spinner_thread = threading.Thread(target=spin)
    spinner_thread.start()
    
    try:
        yield
    finally:
        spinner_stop = True
        spinner_thread.join()

# Usage:
#with spinner():
#    time.sleep(10)  # Or do_long_running_task()
