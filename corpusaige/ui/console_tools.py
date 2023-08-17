#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
import os
from prompt_toolkit.patch_stdout import patch_stdout
import threading
import time
from contextlib import contextmanager
from pathlib import Path
import zipfile

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

def zip_dir(zip_path: Path, dest_file: Path) -> None:
    """Zips a directory recursively into a specified zip file name.
    
    Args:
        zip_path (Path): The path of the directory to zip.
        dest_file (Path): The name of the resulting zip file.

    Returns:
        None
    """
    
    # Create a zip file (overwrites existing one with the same name)
    
    with zipfile.ZipFile(dest_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk the directory
        for root, _, files in os.walk(zip_path):
            for file in files:
                file_path = Path(root) / file
                # Make the archive names relative to the input directory
                arcname = file_path.relative_to(zip_path)
                zipf.write(file_path, arcname)
