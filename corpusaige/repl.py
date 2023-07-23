#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules
import traceback
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
        print("Welcome to the Corpusaige shell")
        print("Use Alt+Enter or Alt-Enter to send command or prompt.")
        print("Use command /exit to quit the shell. Use /help or /? to get full list commands.\n")

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

    def send_chat(self, message: str) -> None:
        try:
            self.corpus.send_prompt(message)
        except Exception as e:
            if not self.corpus.debug_mode:
                print(f"Error sending chat: {str(e)}")
            else:
                print(f"Error sending chat:\n {traceback.format_exc()}")

    def handle_command(self, command: str):
        # Remove leading '/' and trim the command
        command = command[1:].strip().lower()

        # Split the command into main command and subcommands
        command_parts = command.split()
        main_command = command_parts[0]
        subcommands = command_parts[1:]

        # Can't execute through generic invocation mechanism
        # due to the Exception it uses, so do it manually
        if main_command == 'exit':
            self.do_exit()

        if main_command == '?':
            main_command = 'help'

        func = self.commands.get(main_command)
        if func is not None:
            try:
                # Call the function with subcommands as arguments
                if main_command == 'db':
                    func(*subcommands)
                else:
                    func()
            except Exception as e:
                print(f"Error executing command {main_command}: {str(e)}")
        else:
            print("Unknown command. Type /help or /? for assistance.")

    def do_db(self, *args):
        """Perform database operations:
            - db search <text> - search for text in the database
            - db ls            - list all documents in the database 
        """
        if not args:
            print("No subcommand provided for db.")
            return

        subcommand = args[0]
        text = ' '.join(args[1:])
        if subcommand == 'search':
            print(f"Searching for {text} in the database...")
            results = self.corpus.store_search(text)
            self.show_results(results)
        elif subcommand == 'ls':
            print(f"Listing documents from the database...")
            #results = self.corpus.store_ls(text.strip() if text else None)
            results = self.corpus.store_ls()
            self.show_results(results, seperator = None)
        else:
            print(f"Unknown subcommand {subcommand} for db command.")

    def show_results(self, results, seperator = "\n\n"):
        if results:
            for res in results:
                if seperator:
                    print(seperator)
                print(res)
        else:
            print("No results found.")

    def do_debug(self):
        """Toggle debug mode on or off."""
        self.corpus.toggle_debug()
        print(f"Debug mode: {'on' if self.corpus.debug_mode else 'off'}")

    def do_help(self):
        """Show this help message."""
        print("Available commands:")
        for command in self.commands:
            print(f"/{command:<10} - {self.commands[command].__doc__}")

    def do_sources(self):
        """Toggle between showing sources or not."""
        self.corpus.toggle_sources()
        print(f"Show sources: {'on' if self.corpus.show_sources else 'off'}")

    def do_exit(self):
        """Exit the shell."""
        raise EOFError()

    def do_clear(self):
        """Clear the screen."""
        print("\033c", end="")
