#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""
from prompt_toolkit import PromptSession
import prompt_toolkit
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import PythonLexer
from prompt_toolkit.output import create_output
from corpusaige.ui.console_tools import spinner
from corpusaige.protocols import Input, Output

from corpusaige.ui.repl import PromptRepl


class CommandCompleter(Completer):
    
    def __init__(self, commands):
        self.commands = [f'/{n}' for n in list(commands.keys())]

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor(WORD=True)
        for command in self.commands:
            if command.startswith(word):
                yield Completion(command, start_position=-len(word))

def get_terminal_size():
    output = create_output()
    size = output.get_size()
    return size.rows, size.columns

class ShellApp(Input, Output):
    """ShellApp class for the shell interface - utilizing PromptRepl through composition"""
   
    completer : CommandCompleter
    session : PromptSession
    repl: PromptRepl
    _paged_printing: bool = False
    
    def __init__(self, repl: PromptRepl,  DEBUG=False ):
        
        if DEBUG:
            import builtins
            builtins._shell = self  # type: ignore
    
        # Double back reference to the PromptRepl. Any output from the PromptRepl will be printed 
        # to the screen by the ShellRepl and input can be obtained from ShellApp
        self.repl = repl
        self.repl.set_input_output(self, self)
         
        self.completer = CommandCompleter(self.repl.all_commands)
        self.session = PromptSession(completer=self.completer)
        self._paged_printing = False
        
    @property
    def paged_printing(self)-> bool:
        """Paged printing of text to the screen if needed/possible"""
        return self._paged_printing 
    
    @paged_printing.setter
    def paged_printing(self, paging: bool)-> None:
        """Paged printing of text to the screen if needed/possible"""
        self._paged_printing = paging
    
    def print(self, text:str):
        if self._paged_printing:
            # Subtract 1 for the input line
            lines_per_page = get_terminal_size()[0] - 1
            lines = text.split('\n')
            for i in range(0, len(lines), lines_per_page):
                print('\n'.join(lines[i:i+lines_per_page]))
                if i + lines_per_page < len(lines):
                    input('Press any key for next page...')
        else:
            self.print(text)
    
    def clear(self):
        """Clear the screen"""
        self.print("\033c", end="")
    
    def prompt(self, prompt: str) -> str:
        """Prompt for input"""
        return prompt_toolkit.prompt(prompt)
    
    def run(self):
        print("Welcome to the Corpusaige shell\n")
        print("Use: - Alt+Enter or Alt-Enter to send command or prompt.")
        print("     - the Up and Down keys for command history")
        print("     - /exit or /quit to quit the shell.")
        print("     - /help or /? to get full list commands.\nUse TAB to autocomplete commands.\n")

        print(self.repl.title)
        while True:
            try:
                
                with patch_stdout():
                    user_input = self.get_multiline_input(self.repl.prepared_prompt)
                
                if user_input.startswith('/'):
                    # No spinner here as it screws up the paged printing
                    self.repl.handle_command(user_input)
                else:
                    
                    with spinner("Sending prompt..."):
                        self.repl.send_prompt(user_input)

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("KeyboardInterrupt. Use /exit or /quit to quit the shell.")

            except EOFError:
                # Handle Ctrl+D gracefully
                print("Exiting the shell...")
                break
    
    def get_multiline_input(self, default_prompt: str) -> str:
        lines = []
        while True:
            line = self.session.prompt('> ', lexer=PygmentsLexer(PythonLexer),
                                       multiline=True, is_password=False,
                                       vi_mode=False, enable_history_search=True,
                                       default=default_prompt)
            lines.append(line)

            # Break the loop if the input is complete
            if not line.endswith('\\'):
                break

        return '\n'.join(lines)