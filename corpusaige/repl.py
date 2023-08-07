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
from ast import literal_eval
from prompt_toolkit.output import create_output
from sqlalchemy import Engine
from sqlalchemy.orm.session import Session
from corpusaige.data import annotations, conversations
from corpusaige.data.conversations import Conversation
from corpusaige.documentset import DocumentSet
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

def is_valid_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


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

    def __init__(self, corpus: Corpus, db_state_engine: Engine ):
        
        self.title = f"Session: {corpus.name} - path: {corpus.path}"
        self.commands = self.get_commands()
        self.all_commands = self.get_all_commands()
        self.completer = CommandCompleter(self.all_commands)
        self.corpus = corpus
        self.session = PromptSession(completer=self.completer)
        self.pause_page = True
        self.trace_mode = False
        
        self.conversation_id: int | None = None
        self.interaction_id: int | None = None
        self.db_state_engine : Engine = db_state_engine
        self._default_prompt = ""
        
    @property   
    def default_prompt(self)-> str:
        return self._default_prompt
    
    @default_prompt.setter   
    def default_prompt(self, text: str) -> None:
        self._default_prompt = text
    
    def run(self):
        print("Welcome to the Corpusaige shell\n")
        print("Use Alt+Enter or Alt-Enter to send command or prompt.")
        print("Use /exit or /quit to quit the shell.")
        print("Use /help or /? to get full list commands.\nUse TAB to autocomplete commands.\n")

        print(self.title)
        while True:
            try:
                
                with patch_stdout():
                    user_input = self.get_multiline_input(self.default_prompt)
                    self.default_prompt = ""
                
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                else:
                    #print("Sending prompt to GPT-4...")
                    self.send_prompt(user_input)

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("KeyboardInterrupt. Use /exit or /quit to quit the shell.")
                self.default_prompt = ""

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

    def send_prompt(self, message: str) -> None:
        try:
          
            #refactoring needed. seperate db functions from repl
            with Session(self.db_state_engine) as session:
                answer = self.corpus.send_prompt(message)
                self.print(answer)
                self.conversation_id, self.interaction_id = conversations.add_interaction(session, self.conversation_id, message, answer)
                
                
        except Exception as e:
            if not self.trace_mode:
                print(f"Error sending chat: {str(e)}")
            else:
                print(f"Error sending chat:\n {traceback.format_exc()}")

    def handle_command(self, command: str):
        # Remove leading '/' and trim the command
        command = command[1:].strip()

        # Split the command into main command and subcommands
        command_parts = command.split()
        main_command = command_parts[0].lower()
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
        elif len(list) > 0:
            pprint(seperator.join(list), self.pause_page)
        else:
            print("No results found.")
    
    def toggle_trace_mode(self):
        if self.trace_mode:
            self.trace_mode = False
        else:
            self.trace_mode = True  
        
#### Implemented commands 
            
    @detailed_help("Usage: /contextsize [num]")
    def do_contextsize(self, *args, cmdtext=None):
        """Gets or sets the number db results to sent to AI"""
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

    @detailed_help("""Usage: /add "name", "path", "filetype",<recursive - by default True>
       /add "name", ["path1", "path2"], ["filetype1", "filetype2"],<recursive>""")
    def do_add(self, *args, cmdtext=None):
        """Add document set to the corpus"""
        
        ds = literal_eval(f"[{cmdtext}]")
        name = ds[0]
        paths = ds[1 ] if type(ds[1]) is list else [ds[1]]
        ftypes = ds[2] if type(ds[2]) is list else [ds[2]]
        recursive = ds[3] if len(ds) > 3 else False
        docset = DocumentSet.initialize(name, paths, ftypes, recursive)
        self.corpus.add_docset(docset)
        print(f"Added document set {name} to the corpus.")
    
    @detailed_help("""Usage: /conversation           - List all conversations
       /conversation <id>      - List all interactions in a conversation
       /conversation show <id> - Show interaction
       /conversation load <id> - Load conversation answer into edit buffer ready for /store
       /conversation load      - Load last answer into edit buffer ready for /store""")
    @synonymcommand("history")
    def do_conversation(self, *args, cmdtext=None):
        """List conversations/interactiions with the AI"""
        
        match args:
            case ():
                self.show_conversations()
            case (id,) if is_valid_integer(id):
                self.show_interactions(int(id))
            case ('show', id) if is_valid_integer(id):
                self.show_interaction(int(id))
            case ('load',):
                self.load_prompt_for_store()
            case ('load', id) if is_valid_integer(id):
                self.load_prompt_for_store(int(id))
            case _:
                raise ValueError("Invalid command or arguments")
    
    def show_conversations(self):
        with Session(self.db_state_engine) as session:
            convs = conversations.get_conversations(session)
            for conv in convs:
                print(f"{conv.id:>5} : {conv.title}")
    
    def show_interactions(self, id:int):
        if id < 0:
            raise ValueError("Invalid conversation id")
        with Session(self.db_state_engine) as session:
            conv = conversations.get_conversation_by_id(session, id)
            for interact in conv.interactions:
                print(f"{interact.id:>5} : {interact.human_question[:120]}")
    
    def show_interaction(self, id: int):
        if int(id) < 0:
            raise ValueError("Invalid interaction id")
        with Session(self.db_state_engine) as session:
            interact = conversations.get_interaction_by_id(session, id)
            self.print(list=[interact.human_question, interact.ai_answer], seperator="\n-----------------------------------------\n")
    
    def load_prompt_for_store(self, id=None):
        if id is None and self.interaction_id is None:
            raise ValueError("No interaction. Use /conversation load <id> to load an interaction")
        elif id is None:
            id = self.interaction_id
        
        with Session(self.db_state_engine) as session:
            conv = conversations.get_interaction_by_id(session, id)
            self.default_prompt = f"/store {conv.ai_answer}"
    
    def do_store(self, *args, cmdtext=None):
        """Incorporate note or response from the LLM into the corpus"""
        if cmdtext is None or cmdtext.strip() == "":
            print("No text to store.")
        else:
            with Session(self.db_state_engine) as session:
                annotation_id, stored_file = annotations.add_annotation(session, self.corpus.get_annotations_path(), "title", cmdtext)
                self.corpus.store_annotation('Corpusaige annotations', stored_file)
                self.default_prompt = ""
                print(f"Stored annotation in: {stored_file} and vector db")
        
    def do_update(self, *args, cmdtext=None):
        """Update document set in the corpus"""
        raise NotImplementedError("/update not implemented yet")

    def do_remove(self, *args, cmdtext=None):
        """Remove document set from the corpus"""
        raise NotImplementedError("/remove not implemented yet")


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
                    f"/{command:<12} - {self.commands[command].__doc__}", end=_end)
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

