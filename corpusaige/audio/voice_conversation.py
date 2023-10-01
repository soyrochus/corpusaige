#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

from enum import Enum
from pathlib import Path
from typing import Callable
import sounddevice as sd
import numpy as np
import wavio
from pynput import keyboard
from corpusaige.audio.audio_utils import Locale, text_to_speech, speech_to_text
from corpusaige.corpus import Corpus

conversation_recording = False
conversation_terminate = False
conversation_paused = False
conversation_muted = False

class InterruptConversation(Exception):
    pass

def create_response_handler(corpus: Corpus, conversation: "VoiceConversation"):
     
    def _(conversation: "VoiceConversation"):
        global conversation_muted
        txt = speech_to_text(conversation.audio_file, conversation.language)
    
        if txt is None or txt.strip() == "":
            txt = "Sorry, I did not understand you."
            text_to_speech(txt, conversation.audio_file, conversation.language)
            return 
        
        response = corpus.send_prompt(txt)
        
        if response is None or txt.strip() == "":
            response = "Sorry, I did not understand you."
        
        print(f"Response: {response}")
            
        if not conversation_muted:
            text_to_speech(response, conversation.audio_file, conversation.language)
    return _

class VoiceConversation:
    
    corpus: Corpus
    language: Locale
    audio_file: Path
    response_handler: Callable
    
    def __init__(self, corpus: Corpus, language: Locale = Locale.es_ES, audio_file: Path = Path("recorded_voice.wav")):
        self.corpus = corpus
        self.audio_file = audio_file
        self.language = language #TODO: make configurable
        self.response_handler = create_response_handler(corpus, self)

    def start(self):
        
        print("Welcome to the Corpusaige voice interface\n")
     
        print("Use: Talk into the microphone to record your voice.\n")
        print("     Press 'space' to stop recording audio and send it to the AI")
        print("     Press 'm' to mute/unmute the conversation.")
        print("     Press 'p' to pause/resume the conversation.")
        print("     Press 'enter' to stop the conversation and quit the application")
        print(f"Corpus: {self.corpus.name}")
           
        listener = keyboard.Listener(on_release=on_release)
        listener.start()
        try:
            while True:
                self.record()
                if self.response_handler: 
                    self.response_handler(self)
                self.play()
        except InterruptConversation:
            print("Conversation ended.")           
    
    def stop(self):
        raise InterruptConversation
    
    def record(self):
        global conversation_recording, conversation_terminate
        global conversation_muted, conversation_paused
        
        conversation_recording = True
        conversation_terminate = False
        conversation_paused = False
        conversation_muted = False
        buffer = []
        
        def callback(indata, frames, time, status):
            global conversation_paused
            if not conversation_paused:
                buffer.append(indata.copy())
                
        print("Speak now...")
        # with sd.InputStream(callback=lambda indata, frames, time, status: buffer.append(indata.copy()), 
        #                     channels=1, 
        #                     samplerate=44100) as stream:
        with sd.InputStream(callback=callback, 
                            channels=1, 
                            samplerate=44100) as stream:
            while conversation_recording:
                sd.sleep(100)
                if conversation_terminate:
                    raise InterruptConversation()   
                       
        audio_data = np.concatenate(buffer, axis=0)
        wavio.write(str(self.audio_file), audio_data, 44100, sampwidth=2)
        
    def play(self):
        global conversation_muted
        if not conversation_muted:
            wav_obj = wavio.read(str(self.audio_file))
            sd.play(wav_obj.data, wav_obj.rate)
            sd.wait()
        
def on_release(key):
    global conversation_recording, conversation_terminate
    global conversation_muted, conversation_paused
    
    if key == keyboard.Key.space:
        print("Recording has stopped.")
        conversation_recording = False
        conversation_terminate = False
    elif key == keyboard.Key.enter:
        conversation_recording = False
        conversation_terminate = True
        return False
    elif key == keyboard.KeyCode.from_char("p"):
        conversation_paused = not conversation_paused
        print("Conversation paused" if conversation_paused else "Conversation resumed")
    elif key == keyboard.KeyCode.from_char("m"):
        conversation_muted = not conversation_muted
        print("Conversation muted" if conversation_muted else "Conversation unmuted")
        


