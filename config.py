"""
Configuration Module for Personal Voice Assistant (Deva).

Supports Groq API, OpenAI API, Man/Woman voice options,
Auto-Language Detection (English, Hindi, Hinglish), Voice Frequency controls,
and JSON Knowledge Base integration (passwords, daily routines, team Q&A).
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env relative to config.py location
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)


@dataclass
class Config:
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()

    # Provider Selection ('groq' or 'openai')
    _configured_provider: str = os.getenv("API_PROVIDER", "").strip().lower()

    @property
    def API_PROVIDER(self) -> str:
        if self._configured_provider in ["groq", "openai"]:
            return self._configured_provider
        if self.GROQ_API_KEY and self.GROQ_API_KEY != "your_groq_api_key_here":
            return "groq"
        if self.OPENAI_API_KEY and self.OPENAI_API_KEY != "your_openai_api_key_here":
            return "openai"
        return "groq"

    # LLM Model Selection
    @property
    def LLM_MODEL(self) -> str:
        custom_model = os.getenv("LLM_MODEL", "").strip()
        if custom_model:
            return custom_model
        return "openai/gpt-oss-120b" if self.API_PROVIDER == "groq" else "gpt-4o-mini"

    # Speech-to-Text Model Selection
    @property
    def STT_MODEL(self) -> str:
        custom_stt = os.getenv("STT_MODEL", "").strip()
        if custom_stt:
            return custom_stt
        return "whisper-large-v3-turbo" if self.API_PROVIDER == "groq" else "whisper-1"

    # Audio Recording Settings
    SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", "44100"))
    AUDIO_CHANNELS: int = int(os.getenv("AUDIO_CHANNELS", "1"))
    AUDIO_DURATION: float = float(os.getenv("AUDIO_DURATION", "5.0"))
    TEMP_AUDIO_FILE: str = os.getenv("TEMP_AUDIO_FILE", "input_audio.wav")

    # Text-to-Speech & Frequency Tone Settings
    TTS_ENGINE: str = os.getenv("TTS_ENGINE", "pyttsx3")
    VOICE_RATE: int = int(os.getenv("VOICE_RATE", "175"))
    VOICE_PITCH: float = float(os.getenv("VOICE_PITCH", "1.0"))
    VOICE_VOLUME: float = float(os.getenv("VOICE_VOLUME", "1.0"))
    TTS_VOICE_GENDER: str = os.getenv("TTS_VOICE_GENDER", "female").strip().lower()

    # Default Language
    LANGUAGE: str = os.getenv("LANGUAGE", "english").strip().lower()

    # Assistant Persona Name
    ASSISTANT_NAME: str = "Deva"

    # Auto-Detect Language & Knowledge Base System Prompt
    @staticmethod
    def get_system_prompt(knowledge_context: str = "") -> str:
        base_prompt = (
            "You are Deva, a smart, friendly, and helpful personal voice assistant. "
            "AUTOMATICALLY DETECT the language of the user's input (English, Hindi, or Hinglish/Roman Hindi). "
            "Always respond in the EXACT SAME language used by the user! "
            "If the user asks about passwords, daily routines, or team information, check the stored Team Knowledge Base below and provide the exact answer. "
            "Keep responses concise, clear, and natural for speech synthesis.\n"
        )
        if knowledge_context:
            base_prompt += f"\n{knowledge_context}"
        return base_prompt

    def validate_api_key(self) -> bool:
        provider = self.API_PROVIDER
        if provider == "groq":
            return bool(self.GROQ_API_KEY and self.GROQ_API_KEY != "your_groq_api_key_here")
        elif provider == "openai":
            return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY != "your_openai_api_key_here")
        return False


config = Config()
