#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

from enum import Enum
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from pathlib import Path

# enum Locale to represent the language of the conversation
# format:  locale, lang, name = language.value
class Locale(Enum):
    en_US=("en-US", "en", "English")
    en_UK=("en-UK", "en", "English")
    es_ES=("es-ES", "es", "Spanish")
    generic=("en-US", "en", "English (fallback)")
    
    @classmethod
    def from_locale(cls, locale:str)-> 'Locale':
        "return the Locale for the given local descriptio or None if not found"
        for item in cls:
            if item.value[0] == locale:
                return item
        return None
    
    @classmethod
    def from_language(cls, lang: str)-> 'Locale':
        "return the Locale for the given language or None if not found"
        for item in cls:
            if item.value[1] == lang:
                return item
        return None

def text_to_speech(text: str, path: Path, language: Locale = Locale.en_US):
 
    locale, lang, name = language.value
    if path.suffix != ".wav":
        raise ValueError("Unsupported file extension")
    
    tts = gTTS(text=text, lang=lang)
    
    # Clone the path with an mp3 extension
    mp3_path = path.with_name(path.stem + ".mp3")   
    tts.save(str(mp3_path))

    # Convert MP3 to WAV 
    sound = AudioSegment.from_mp3(str(mp3_path))
    sound.export(path, format="wav")


def speech_to_text(path: Path, language: Locale = Locale.en_US) -> str:
    
    if path.suffix != ".wav":
        raise ValueError("Unsupported file extension")
    
    locale, lang, name = language.value
     
    # Use speech_recognition to recognize the speech
    recognizer = sr.Recognizer()

    with sr.AudioFile(str(path)) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data, language=locale)
        
        #TODO: add more specific exception handling and process the errors better (now just print)
        except sr.UnknownValueError:    
            print("Could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

