#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
from prompt_toolkit import PromptSession
from prompt_toolkit.document import Document
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import PythonLexer
import pygments.lexers

from .corpus import Corpus

class ChatRepl:
    title: str
    session: PromptSession
    commands: dict
    
    def __init__(self, corpus: Corpus):
        self.title = f"Session: {corpus.name} - path: {corpus.path}" 
        self.session = PromptSession()
        self.commands = self.get_commands()
        self.corpus = corpus

    def run(self):
        print("Welcome to the Corpusaige shell. Type /help or /? to list commands.\n")
        print(self.title)
        while True:
            try:
                with patch_stdout():
                    user_input = self.get_multiline_input()

                if user_input.startswith('/'):
                    self.handle_command(user_input)
                else:
                    self.send_chat(user_input)

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("KeyboardInterrupt. Use /exit to quit the shell.")

            except EOFError:
                # Handle Ctrl+D gracefully
                print("Exiting the shell...")
                break

    def get_commands(self):
        commands = {}
        for name in dir(self):
            if name.startswith("do_"):
                command = name[3:]
                commands[command] = getattr(self, name)
        return commands

    def get_multiline_input(self):
        lines = []
        while True:
            line = self.session.prompt('> ', lexer=PygmentsLexer(PythonLexer), 
                                       multiline=True, is_password=False,
                                       vi_mode=False, enable_history_search=True)
            lines.append(line)
            
            # Break the loop if the input is complete
            if not line.endswith('\\'):
                break

        return '\n'.join(lines)

    def send_chat(self, message: str)-> None:
        self.corpus.send_prompt(message)

    def handle_command(self, command: str):
        command = command[1:].strip()

        if command == 'help' or command == '?':
            self.show_help()
        elif command == 'exit':
            self.do_exit()
        else:
            print("Unknown command. Type /help or /? for assistance.")

    def show_help(self):
       
        print("Available commands:")
        for command in self.commands:
            print(f"/{command:<10} - {self.commands[command].__doc__}")

    def do_help(self):
        """Show this help message."""
        self.show_help()


    def do_exit(self):
        """Exit the shell."""	
        raise EOFError()

  