#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules

import tkinter as tk
from tkinter import scrolledtext, Menu, messagebox
from corpusaige.config.read import get_config
from corpusaige.corpus import StatefullCorpus
from corpusaige.data.db import init_db

from corpusaige.protocols import Printer
from corpusaige.repl import PromptRepl

class GuiRepl(Printer):
    root: tk.Tk
    repl: PromptRepl
   
    def __init__(self, root: tk.Tk, repl: PromptRepl,  DEBUG=False ):
        self.root = root
        self.root.title = 'Corpusaige GuiRepl' 
        self.root.bind('<Map>', self.on_first_show)
        
        
        #back reference to the PromptRepl. Any output from the PromptRepl will be printed 
        # to the screen by the GuiRepl
        self.repl = repl
        self.repl.set_printer(self)
        
        # Colors
        self.dark_mode_colors = {
            'bg': '#2E3B4E',
            'fg': '#E2E2E2',
            'input_bg': '#3A4D70',
            'button_bg': '#4A5F8E'
        }

        self.light_mode_colors = {
            'bg': '#EDEDED',
            'fg': '#333333',
            'input_bg': '#FFFFFF',
            'button_bg': '#CCCCCC'
        }

        # Menu bar
        menubar = Menu(root)

        # File menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # View menu
        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Clear", command=self.clear_contents)
        
        # Appearance sub-menu
        appearance = Menu(viewmenu, tearoff=0)
        appearance.add_command(label="Dark Mode", command=lambda: self.set_mode('dark'))
        appearance.add_command(label="Light Mode", command=lambda: self.set_mode('light'))
        viewmenu.add_cascade(label="Appearance", menu=appearance)
        
        menubar.add_cascade(label="View", menu=viewmenu)

        # Help menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        self.root.config(menu=menubar)
        
        self.setup_widgets()

    def on_first_show(self, event):
        self.root.unbind('<Map>')
        self.print("Welcome to the Corpusaige shell\n")
        self.print("Use Alt+Enter or Alt-Enter to send command or prompt.")
        self.print("Use /exit or /quit to quit the shell.")
        self.print("Use /help or /? to get full list commands.\n") #\nUse TAB to autocomplete commands.\n")

        self.print(self.repl.title)
        
    def setup_widgets(self):
        # Configure the weights of rows and columns to make resizing smooth
        self.root.grid_rowconfigure(0, weight=4)  # 4/5 of the size
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=4)
        self.root.grid_columnconfigure(1, weight=1)

        # Output TextBox
        self.output_box = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED)
        self.output_box.grid(row=0, column=0, columnspan=2, sticky='nsew')

        # Input TextBox
        self.input_box = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5)
        self.input_box.grid(row=1, column=0, sticky='nsew')
        self.input_box.bind('<Alt-Return>', lambda event: self.send_message())
        self.input_box.bind('<Escape><Return>', lambda event: self.send_message())

        # Send Button
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, sticky='nsew')

        #self.set_mode('dark')  # Default to dark mode
        self.set_mode('light')  # Default to light mode

    def send_message(self):
        # Retrieve input, clear the input box, and append to output
        user_input = self.input_box.get("1.0", tk.END).strip()
        self.print("Prompt: " + user_input)
        self.input_box.delete("1.0", tk.END)

        # Handle the input message (here, we just echo it for simplicity)
        self.print( "Result: ")
        
        #user_input = self.get_multiline_input(self.repl.default_prompt)
        self.repl.default_prompt = ""
    
        try:    
            if user_input.startswith('/'):
                self.repl.handle_command(user_input)
            else:
                #with spinner("Sending prompt..."):
                self.repl.send_prompt(user_input)
        except EOFError:
                print("Exiting the shell...")
                self.root.quit()
            
    def append_to_output(self, message):
        self.output_box.config(state=tk.NORMAL)
        self.output_box.insert(tk.END, message + '\n')
        self.output_box.config(state=tk.DISABLED)
        self.output_box.see(tk.END)

    def clear_contents(self):
        self.input_box.delete("1.0", tk.END)
        self.output_box.config(state=tk.NORMAL)
        self.output_box.delete("1.0", tk.END)
        self.output_box.config(state=tk.DISABLED)

    def set_mode(self, mode):
        if mode == 'dark':
            self.current_colors = self.dark_mode_colors
        else:
            self.current_colors = self.light_mode_colors

        self.root.configure(bg=self.current_colors['bg'])

        self.output_box.configure(bg=self.current_colors['bg'], fg=self.current_colors['fg'])
        self.input_box.configure(bg=self.current_colors['input_bg'], fg=self.current_colors['fg'])
        self.send_button.configure(bg=self.current_colors['button_bg'], fg=self.current_colors['fg'])

    def show_about(self):
        messagebox.showinfo("About", """Copyright © 2023
Licensed under
the MIT License""")

    def pprint(self, text:str, pause_page: bool =True):
        # if pause_page:
        #     # Subtract 1 for the input line
        #     lines_per_page = get_terminal_size()[0] - 1
        #     lines = text.split('\n')
        #     for i in range(0, len(lines), lines_per_page):
        #         print('\n'.join(lines[i:i+lines_per_page]))
        #         if i + lines_per_page < len(lines):
        #             input('Press any key for next page...')
        # else:
        self.print(text)
            
    def print(self, text:str):
        self.append_to_output(text)
    
    def clear(self):
        """Clear the screen"""
        self.clear_contents()
        
    def run(self):
        
        self.root.mainloop()

# if __name__ == "__main__":
#     root = tk.Tk()
   
#     config = get_config('.')
#     corpus = StatefullCorpus(config)

#     db_state_engine = init_db(corpus.state_db_path)
#     prompt = PromptRepl(corpus, db_state_engine)
#     GuiRepl(root, prompt, True).run()