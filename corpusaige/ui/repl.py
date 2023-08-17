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

from ast import literal_eval
from sqlalchemy import Engine
from sqlalchemy.orm.session import Session
from corpusaige.data import annotations, conversations
from corpusaige.documentset import DocumentSet
from corpusaige.exceptions import InvalidParameters
from corpusaige.protocols import Printer
from ..corpus import Corpus



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




def is_valid_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class PromptRepl:
    title: str
    commands: dict
    prn: Printer 

    def __init__(self, corpus: Corpus, db_state_engine: Engine):
        
       
        self.title = f"Session: {corpus.name} - path: {corpus.path}"
        self.commands = self.get_commands()
        self.all_commands = self.get_all_commands()
        
        self.corpus = corpus
       
        self.pause_page = True
        self.trace_mode = False
        
        self.conversation_id: int | None = None
        self.interaction_id: int | None = None
        self.db_state_engine : Engine = db_state_engine
        self._default_prompt = ""
    
    def set_printer(self, printer: Printer):
        self.prn = printer
        self.corpus.set_printer(printer)
    
    @property   
    def default_prompt(self)-> str:
        return self._default_prompt
    
    @default_prompt.setter   
    def default_prompt(self, text: str) -> None:
        self._default_prompt = text
    
        
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

    def send_prompt(self, message: str) -> None:
        try:
          
            #refactoring needed. seperate db functions from repl
            with Session(self.db_state_engine) as session:
                answer = self.corpus.send_prompt(message)
                self.prn.pprint(answer)
                self.conversation_id, self.interaction_id = conversations.add_interaction(session, self.conversation_id, message, answer)
                
                
        except Exception as e:
            if not self.trace_mode:
                self.prn.print(f"Error sending chat: {str(e)}")
            else:
                self.prn.print(f"Error sending chat:\n {traceback.format_exc()}")

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
                    self.prn.print(
                        f"Error executing command {main_command}: \n\n{traceback.format_exc()}")
                else:
                    self.prn.print(f"Error executing command {main_command}: {e}")
        else:
            self.prn.print("Unknown command. Type /help or /? for assistance.")

    def print_results(self, text=None, *, list=None, seperator=""):
        if text is not None:
            self.prn.pprint(text, self.pause_page)
        elif len(list) > 0:
            self.prn.pprint(seperator.join(list), self.pause_page)
        else:
            self.prn.print("No results found.")
    
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
            self.prn.print(f"Number of items in context: {self.corpus.context_size}")
        else:
            self.corpus.context_size = int(num)
            self.prn.print(f"Number of items in context set to {self.corpus.context_size}")

    @detailed_help("""Usage: /ls          - List document sets in the corpus
       /ls [docset] - List documents in the document set            
       /ls    *     - List all documents in the corpus""")
    @synonymcommand("dir")
    def do_ls(self, *args, cmdtext=None):
        """List documents in the corpus."""
        
        match args:
            case ():
                self.prn.print("Listing doc-sets from the corpus...")
                results = self.corpus.ls_docs(all_docs=False, doc_set='')
            case ('*',) :
                self.prn.print("Listing all documents from the corpus...")
                results = self.corpus.ls_docs(all_docs=True, doc_set='')
            case _:
                self.prn.print("Listing documents from the given doc-set...")
                results = self.corpus.ls_docs(all_docs=False,doc_set=cmdtext)

        results.sort()
        #self.print(list=results, seperator="\n")
        self.print_results(list=results, seperator="\n")


    @detailed_help("Usage: /search <text>")
    def do_search(self, *args, cmdtext=None):
        """Search for text in the corpus (without sending to AI)"""
        self.prn.print(f"Searching for {cmdtext }...")
        results = self.corpus.store_search(cmdtext)
        self.print_results(list=results)

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
        self.prn.print(f"Added document set {name} to the corpus.")
    
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
                raise InvalidParameters("Invalid command or arguments")
    
    def show_conversations(self):
        with Session(self.db_state_engine) as session:
            convs = conversations.get_conversations(session)
            for conv in convs:
                self.prn.print(f"{conv.id:>5} : {conv.title}")
    
    def show_interactions(self, id:int):
        if id < 0:
            raise InvalidParameters("Invalid conversation id")
        with Session(self.db_state_engine) as session:
            conv = conversations.get_conversation_by_id(session, id)
            for interact in conv.interactions:
                self.prn.print(f"{interact.id:>5} : {interact.human_question[:120]}")
    
    def show_interaction(self, id: int):
        if int(id) < 0:
            raise InvalidParameters("Invalid interaction id")
        with Session(self.db_state_engine) as session:
            interact = conversations.get_interaction_by_id(session, id)
            self.print_results(list=[interact.human_question, interact.ai_answer], seperator="\n-----------------------------------------\n")
    
    def load_prompt_for_store(self, id=None):
        if id is None and self.interaction_id is None:
            raise InvalidParameters("No interaction. Use /conversation load <id> to load an interaction")
        elif id is None:
            id = self.interaction_id
        
        with Session(self.db_state_engine) as session:
            conv = conversations.get_interaction_by_id(session, id)
            self.default_prompt = f"/store {conv.ai_answer}"
    
    @synonymcommand("annotate")
    def do_store(self, *args, cmdtext=None):
        """Incorporate annotation (from scratch or response from the LLM) into the corpus"""
        if cmdtext is None or cmdtext.strip() == "":
            self.prn.print("No text to store.")
        else:
            
            raise NotImplementedError("/store not implemented yet")
            #title = prompt("Enter title for annotation: ")
            #title = strip_invalid_file_chars(title)
            title= "Not implemented yet"
            
            with Session(self.db_state_engine) as session:    
                annotation_id, stored_file = annotations.add_annotation(session, self.corpus.annotations_path, title, cmdtext)
                self.corpus.store_annotation('Corpusaige annotations', stored_file)
                self.prn.print(f"Stored annotation in: {stored_file} and vector db")

    def do_update(self, *args, cmdtext=None):
        """Update document set in the corpus"""
        raise NotImplementedError("/update not implemented yet")

    @detailed_help("""Usage: /remove <doc-set-name>""") 
    @synonymcommand("del", "rm")
    def do_remove(self, *args, cmdtext=None):
        """Remove document set from the corpus"""
        if cmdtext is None or cmdtext.strip() == "":
            raise InvalidParameters("No document set name specified")
        else:
            self.corpus.remove_docset(cmdtext)
        

    @detailed_help("""Usage: /run <script_name> <<*args>>
Scripys can be added to the corpus by placing them in the scripts folder""")  
    def do_run(self, *args, cmdtext=None):
        """Run a script"""
        self.prn.print(f"Running script {cmdtext}...")
        #match on <<script_name>> <<*args>> 
        match args:
            case ():
                raise InvalidParameters("Missing script name")
            case (script_name, *args) if script_name in self.corpus.scripts:
                result = self.corpus.run_script(script_name, *args)
                if result is not None:
                    self.prn.print(result)
            case _:
                raise InvalidParameters("Invalid script or arguments")
                
    def do_act(self, *args, cmdtext=None):
        """Let de LLM perform an action (to be approved by the user)"""
        raise NotImplementedError("/act not implemented yet")

    @synonymcommand('debug')
    def do_trace(self, *args, cmdtext=None):
        """Toggle trace (debug) mode on or off."""
        self.toggle_trace_mode()
        self.prn.print(f"Trace (debug) mode: {'on' if self.trace_mode else 'off'}")

    def get_help_for_command(self, command_name):
        command = self.all_commands[command_name]
        if hasattr(command, 'synonyms'):
            _end = f"; synonym(s): {' '.join(sorted(command.synonyms))}"
        else:
            _end = ""
        return f"/{command_name:<12} - {command.__doc__} {_end}"
                
    @synonymcommand("?")
    def do_help(self, *args, cmdtext=None):
        """Show this help message."""
        if len(args) == 0:
            self.prn.print("Available commands:")
            for command in self.commands:
                self.prn.print(self.get_help_for_command(command))
    
        else:
            command = args[0]
            if command in self.all_commands:
                cmd = self.all_commands[command]
                self.prn.print(self.get_help_for_command(command))
                if hasattr(cmd, 'detailed_help'):
                    self.prn.print(cmd.detailed_help)
            else:
                self.prn.print(f"Unknown command: {command}")
                
    def do_sources(self, *args, cmdtext=None):
        """Toggle between showing sources or not."""
        self.corpus.toggle_sources()
        self.prn.print(f"Show sources: {'on' if self.corpus.show_sources else 'off'}")

    @synonymcommand('quit')
    def do_exit(self, *args, cmdtext=None):
        """Exit the shell."""
        raise EOFError()

    def do_clear(self, *args, cmdtext=None):
        """Clear the screen."""
        #self.prn.print("\033c", end="")
        self.prn.clear()

    @synonymcommand("pause")
    def do_pause_page(self, *args, cmdtext=None):
        """Toggle pause page on or off."""
        self.pause_page = not self.pause_page
        self.prn.print(f"Pause page: {'on' if self.pause_page else 'off'}")
