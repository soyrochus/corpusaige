#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules

from collections import deque
import tkinter as tk
from tkinter import scrolledtext, Menu, messagebox
from tkinter import font

from corpusaige.protocols import Input, Output
from corpusaige.ui.gui_tools import exec_task_with_progress
from corpusaige.ui.repl import PromptRepl
from tkinter import simpledialog

class GuiApp(Input, Output):
    root: tk.Tk
    repl: PromptRepl
   
    def __init__(self, root: tk.Tk, repl: PromptRepl,  DEBUG=False ):
        self.root = root
        self.root.title('Corpusaige GuiRepl') 
        self.root.bind('<Map>', self.on_first_show)
        
        
        # Double back reference to the PromptRepl. Any output from the PromptRepl will be printed 
        # to the screen by the GuiApp and input can be obtained from GuiApp
        self.repl = repl 
        self.repl.set_input_output(self, self)
        
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
        
        # List fonts in order of preference.
        import platform
        match platform.system():
            case "Windows":
                font_family = 'Consolas'
            case "Darwin": # MacOS
                font_family = 'Menlo'
            case "Linux":
                font_family = 'Monospace'
            case _:
                font_family = 'Monospace'

        self.text_font = font.Font(family=font_family, size=14)

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
        self.print("Use: - 'Send' button or press Alt+Enter or CTRL-Enter to send command or prompt.")
        self.print("     - the CTRL-Up and CTRL-Down keys for command history")
        self.print("     - /exit or /quit to quit the shell.")
        self.print("     - /help or /? to get full list commands.\n") #\nUse TAB to autocomplete commands.\n")

        self.print(self.repl.title)
        
    def setup_widgets(self):
        # Configure the weights of rows and columns to make resizing smooth
        self.root.grid_rowconfigure(0, weight=4)  # 4/5 of the size
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=4)
        self.root.grid_columnconfigure(1, weight=1)

        # Output TextBox
        self.output_box = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED, font=self.text_font)
        self.output_box.grid(row=0, column=0, columnspan=2, sticky='nsew')

        # Input TextBox
        self.input_box = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5, font=self.text_font)
        self.input_box.grid(row=1, column=0, sticky='nsew')
        self.input_box.bind('<Alt-Return>', lambda event: self.send_message())
        self.input_box.bind('<Escape><Return>', lambda event: self.send_message())

        # Send Button
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, sticky='nsew')

        #self.set_mode('dark')  # Default to dark mode
        self.set_mode('light')  # Default to light mode
        
        # Command history and index initialization
        self.command_history = deque(maxlen=20)  # Let's say we keep the last 10 commands
        self.command_index = -1

        # Key bindings for command history navigation
        self.input_box.bind('<Control-Up>', self.prev_command)
        self.input_box.bind('<Control-Down>', self.next_command)

    def send_message(self):
        # Retrieve input, clear the input box, and append to output
        user_input = self.input_box.get("1.0", tk.END).strip()
        
        if user_input:  # Avoid adding empty strings to history
            self.command_history.append(user_input)
        self.command_index = -1
        
        
        self.print("Prompt: " + user_input)
        self.input_box.delete("1.0", tk.END)
        #self.input_box

        # Handle the input message (here, we just echo it for simplicity)
        self.print( "Result: ")
 
        try:    
            if user_input.startswith('/'):
                
                #No spinner here as it interferes with the user input
                self.repl.handle_command(user_input)
                #exec_task_with_progress(self.root, "Executing...", lambda: self.repl.handle_command(user_input))
            
            else:
                
                exec_task_with_progress(self.root,"Sending prompt...", lambda: self.repl.send_prompt(user_input))
                
        except EOFError:
                print("Exiting the shell...")
                self.root.quit()
        
        self.input_box.insert(tk.END, self.repl.prepared_prompt)
    
    def prev_command(self, event=None):
        """Navigate to the previous command in the history."""
        if self.command_history and self.command_index < len(self.command_history) - 1:
            self.command_index += 1
            command = self.command_history[-(self.command_index + 1)]  # Get command from the end of the list
            self.input_box.delete("1.0", tk.END)
            self.input_box.insert(tk.END, command)

    def next_command(self, event=None):
        """Navigate to the next command in the history."""
        if self.command_history and self.command_index > 0:
            self.command_index -= 1
            command = self.command_history[-(self.command_index + 1)]
            self.input_box.delete("1.0", tk.END)
            self.input_box.insert(tk.END, command)
        elif self.command_history and self.command_index == 0:  # At the start of the history, clear the input box
            self.command_index = -1
            self.input_box.delete("1.0", tk.END)
    
            
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

    @property
    def paged_printing(self)-> bool:
        """Paged printing of text to the screen if needed/possible"""
        return False
    
    @paged_printing.setter
    def paged_printing(self, paging: bool)-> None:
        """Paged printing of text to the screen if needed/possible"""
        raise NotImplementedError("Paged printing not necessary (and therefore not implemented) in GUI")
        
    def print(self, text:str):
        self.append_to_output(text)
    
    def clear(self):
        """Clear the screen"""
        self.clear_contents()
    
    def prompt(self, prompt: str) -> str:
        """Prompt for input"""
        answer = simpledialog.askstring("", prompt) 
        if answer is not None:
            return answer
        else:
            return ""
    
    def run(self):
        
        self.root.mainloop()
