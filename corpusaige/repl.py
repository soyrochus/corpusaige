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
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import PythonLexer
import pygments.lexers
from prompt_toolkit.output import create_output
from .corpus import Corpus


def synonymcommand(*synonyms):
    def decorator(func):
        func.synonyms = synonyms
        return func
    return decorator

def detailed_help(help_text):
    def decorator(func):
        func.detailed_help = help_text
        return func
    return decorator

def get_terminal_size():
    output = create_output()
    size = output.get_size()
    return size.rows, size.columns


def pprint(text, pause_page=True):
    if pause_page:
        # Subtract 1 for the input line
        lines_per_page = get_terminal_size()[0] - 1
        lines = text.split('\n')
        for i in range(0, len(lines), lines_per_page):
            print('\n'.join(lines[i:i+lines_per_page]))
            if i + lines_per_page < len(lines):
                input('Press any key for next page...')
    else:
        print(text)


class CommandCompleter(Completer):
    def __init__(self, commands):
        self.commands = [f'/{n}' for n in list(commands.keys())]

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor(WORD=True)
        for command in self.commands:
            if command.startswith(word):
                yield Completion(command, start_position=-len(word))


class PromptRepl:
    title: str
    session: PromptSession
    commands: dict

    def __init__(self, corpus: Corpus):
        self.title = f"Session: {corpus.name} - path: {corpus.path}"
        self.commands = self.get_commands()
        self.all_commands = self.get_all_commands()
        self.completer = CommandCompleter(self.all_commands)
        self.corpus = corpus
        self.session = PromptSession(completer=self.completer)
        self.pause_page = True
        self.trace_mode = False
        

    def run(self):
        print("Welcome to the Corpusaige shell\n")
        print("Use Alt+Enter or Alt-Enter to send command or prompt.")
        print("Use /exit or /quit to quit the shell.")
        print("Use /help or /? to get full list commands.\nUse TAB to autocomplete commands.\n")

        print(self.title)
        while True:
            try:
                with patch_stdout():
                    user_input = self.get_multiline_input()

                if user_input.startswith('/'):
                    self.handle_command(user_input)
                else:
                    self.send_prompt(user_input)

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("KeyboardInterrupt. Use /exit or /quit to quit the shell.")

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

    def get_all_commands(self):
        commands = self.get_commands()
        synonyms = {}

        for name, func in commands.items():
            if hasattr(func, 'synonyms'):
                for synonym in func.synonyms:
                    synonyms[synonym] = func
        commands.update(synonyms)
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

    def send_prompt(self, message: str) -> None:
        try:
            
            pprint(self.corpus.send_prompt(message), self.pause_page)
        except Exception as e:
            if not self.trace_mode:
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
        cmdtext = ' '.join(subcommands)

        # Can't execute through generic invocation mechanism
        # due to the Exception it uses, so do it manually
        if main_command == 'exit' or main_command == 'quit':
            self.do_exit()

        func = self.all_commands.get(main_command)
        if func is not None:
            try:
                func(*subcommands, cmdtext=cmdtext)
            except Exception as e:
                if self.trace_mode:
                    print(
                        f"Error executing command {main_command}: \n\n{traceback.format_exc()}")
                else:
                    print(f"Error executing command {main_command}: {e}")
        else:
            print("Unknown command. Type /help or /? for assistance.")

    def print(self, text=None, *, list=None, seperator=""):
        if text is not None:
            pprint(text, self.pause_page)
        if len(list) > 0:
            pprint(seperator.join(list), self.pause_page)
        else:
            print("No results found.")
    
    def toggle_trace_mode(self):
        if self.trace_mode:
            self.trace_mode = False
        else:
            self.trace_mode = True  
        
#### Implemented commands 
            
    def do_contextsize(self, *args, cmdtext=None):
        """Gets or sets the number db results to sent to AI
              Usage: /contextsize [num]"""
        num = cmdtext.strip()
        if num is None:
            print(f"Number of items in context: {self.corpus.context_size}")
        else:
            self.corpus.context_size = int(num)
            print(f"Number of items in context set to {self.corpus.context_size}")

    def do_ls(self, *args, cmdtext=None):
        """List documents in the corpus."""
        print(f"Listing documents from the corpus...")
        results = self.corpus.store_ls()
        self.print(list=results, seperator="\n")

    @detailed_help("Usage: /search <text>")
    def do_search(self, *args, cmdtext=None):
        """Search for text in the corpus (without sending to AI)"""
        print(f"Searching for {cmdtext }...")
        results = self.corpus.store_search(cmdtext)
        self.print(list=results)

    def do_add(self, *args, cmdtext=None):
        """Add document set to the corpus"""
        raise NotImplementedError("/add not implemented yet")

    def do_update(self, *args, cmdtext=None):
        """Update document set in the corpus"""
        raise NotImplementedError("/update not implemented yet")

    def do_remove(self, *args, cmdtext=None):
        """Remove document set from the corpus"""
        raise NotImplementedError("/remove not implemented yet")

    def do_store(self, *args, cmdtext=None):
        """Incorporate response from the LLM into the corpus"""
        raise NotImplementedError("/store not implemented yet")

    def do_note(self, *args, cmdtext=None):
        """Add note as document to the corpus"""
        raise NotImplementedError("/note not implemented yet")

    def do_run(self, *args, cmdtext=None):
        """Run a script"""
        raise NotImplementedError("/run not implemented yet")

    def do_act(self, *args, cmdtext=None):
        """Let de LLM perform an action (to be approved by the user)"""
        raise NotImplementedError("/act not implemented yet")

    @detailed_help("""Operation on the cache:
Usage: /cache <command>
    - keys   <namespace> - get the keys of the given namespace
    - get    <id>        - obtain the item with the given id
    - delete <id>        - delete the item with the given id""")
    def do_cache(self, *args, cmdtext=None):
        """Perform operations on the cache (see /help cache for more info)"""
        raise NotImplementedError("/cache not implemented yet")

    @synonymcommand('debug')
    def do_trace(self, *args, cmdtext=None):
        """Toggle trace (debug) mode on or off."""
        self.toggle_trace_mode()
        print(f"Trace (debug) mode: {'on' if self.trace_mode else 'off'}")

    @synonymcommand("?")
    def do_help(self, *args, cmdtext=None):
        """Show this help message."""
        if len(args) == 0:
            print("Available commands:")
            for command in self.commands:
                if hasattr(self.commands[command], 'synonyms'):
                    _end = f"; synonym(s): {' '.join(sorted(self.commands[command].synonyms))}\n"
                else:
                    _end = "\n"
                print(
                    f"/{command:<10} - {self.commands[command].__doc__}", end=_end)
        else:
            command = args[0]
            if command in self.commands:
                cmd = self.commands[command]
                print(cmd.__doc__)
                if hasattr(cmd, 'detailed_help'):
                    print(cmd.detailed_help)
            else:
                print(f"Unknown command: {command}")
                
    def do_sources(self, *args, cmdtext=None):
        """Toggle between showing sources or not."""
        self.corpus.toggle_sources()
        print(f"Show sources: {'on' if self.corpus.show_sources else 'off'}")

    @synonymcommand('quit')
    def do_exit(self, *args, cmdtext=None):
        """Exit the shell."""
        raise EOFError()

    def do_clear(self, *args, cmdtext=None):
        """Clear the screen."""
        print("\033c", end="")

    @synonymcommand("pause")
    def do_pause_page(self, *args, cmdtext=None):
        """Toggle pause page on or off."""
        self.pause_page = not self.pause_page
        print(f"Pause page: {'on' if self.pause_page else 'off'}")

