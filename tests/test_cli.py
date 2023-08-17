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
import pytest
from unittest import mock
import sys
from corpusaige.ui.cli import cli_run  

APP_NAME = 'corpusaige.py'

@mock.patch('corpusaige.ui.cli.get_config') # Mock the get_config function where it is used in the cli module, NOT where it is defined
@mock.patch('corpusaige.ui.cli.new_corpus')
@mock.patch('corpusaige.ui.cli.add_docset')
@mock.patch('corpusaige.ui.cli.shell')
def test_cli_run(mock_shell, mock_add_docset, mock_new_corpus, mock_get_config):
    sys.argv = [APP_NAME, 'new', 'Test_Name']
    cli_run()
    mock_new_corpus.assert_called()

    sys.argv = [APP_NAME, 'add', '-n', 'test_docset', '-p', '/home/test', '-t', 'text', '--recursive']
    cli_run()
    mock_add_docset.assert_called()

    sys.argv = [APP_NAME, 'shell']
    cli_run()
    mock_shell.assert_called()
    
    sys.argv = [APP_NAME,'-p', os.getcwd(), 'shell']
    cli_run()
    #guarantee that the mock_shell function was called, multiple times if necesarry
    mock_shell.assert_called()
    
    with pytest.raises(Exception):
        sys.argv = [APP_NAME,'nonsense']
        cli_run()


# if __name__ == "__main__":
#     pytest.main()