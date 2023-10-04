#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

import os
import re
import tempfile
from typing import Any, Dict, List, Tuple, Union
from pathlib import Path

import sounddevice as sd
import numpy as np
import wavio

def get_sentences(buffer: str) -> Tuple[str, str]:
    pattern = re.compile(r'([^.!?]*[.!?])\s*')
    sentences = pattern.findall(buffer)
    remaining = pattern.sub('', buffer, count=len(sentences))
    return (' '.join(sentences).strip(), remaining)


from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from gtts import gTTS
import io
from pydub import AudioSegment
from pydub.playback import play

# def play_text(sentences: str, lang: str= 'es'):
#     # Generate speech
#     tts = gTTS(text=sentences, lang=lang)
    
#     #voice_wav = str(Path("voice.wav"))
#     voice_wav = str(Path("recorded_voice.wav").absolute().as_posix())
#     voice_mp3 = str(Path("recorded_voice.mp3").absolute().as_posix())
    
#     # Save audio to temporary file and close it
#     tts.save(voice_mp3)
#     #temp.close()
     
#     try:
#         # Load and play audio
#         wav_obj = wavio.read(voice_mp3)
#         sd.play(wav_obj.data, wav_obj.rate)
#         sd.wait()
        
        
#         # Load audio
#         #audio = AudioSegment.from_mp3(voice_mp3)
#         # Convert MP3 to WAV
#         #audio = audio.set_frame_rate(44100).set_channels(2)
#         # Play audio
#         # play(audio)
#     #finally:
#         # Ensure temporary file is deleted
#         #if  os.path.exists(temp_filename):
#         #    os.remove(temp_filename)
#     except Exception as e:
#         print(f"Error playing audio: {e}")
        

def play_text(sentences: str, lang: str= "es"):
    # Generate speech
    tts = gTTS(text=sentences, lang=lang)
    
    voice_wav = str(Path("recorded_voice.wav").absolute().as_posix())
    voice_mp3 = str(Path("recorded_voice.mp3").absolute().as_posix())

    tts.save(voice_mp3)
    
    # Load MP3 and convert to WAV
    audio = AudioSegment.from_mp3(voice_mp3)
    
    # Create and open a temporary file for WAV
    audio.export(voice_wav, format="wav")
    
    # Load and play WAV
    #audio = AudioSegment.from_wav(voice_wav)
    #play(audio)
    wav_obj = wavio.read(voice_wav)
    sd.play(wav_obj.data, wav_obj.rate)
    sd.wait()
      
                     
class StreamingAudioOutCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming. Only works with LLMs that support streaming."""

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        self.buffer = ""

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        #sys.stdout.write(token)
        #sys.stdout.flush()
        self.buffer += token
        sentences, self.buffer = get_sentences(self.buffer)      
        if len (sentences) > 0:
            play_text(sentences)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        if len(self.buffer) > 0:
            play_text(self.buffer)
            self.buffer = ""

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when LLM errors."""
        self.buffer = ""

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends running."""

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when chain errors."""

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        pass

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when tool errors."""

    def on_text(self, text: str, **kwargs: Any) -> None:
        """Run on arbitrary text."""

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Run on agent end."""

