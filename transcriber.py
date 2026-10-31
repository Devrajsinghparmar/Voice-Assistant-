"""
Speech-to-Text (STT) Transcriber Module.

Supports Groq Whisper API (whisper-large-v3-turbo) with automatic language detection.
"""

import os
from config import config


class Transcriber:
    def __init__(self):
        self.provider = config.API_PROVIDER
        self.client = None
        self._current_key = None
        self._get_client()

    def _get_client(self):
        """Dynamically retrieves or initializes the Groq/OpenAI client with active API key."""
        api_key = os.getenv("GROQ_API_KEY", "").strip() or config.GROQ_API_KEY
        if api_key and api_key != "your_groq_api_key_here":
            if self.client is None or self._current_key != api_key:
                try:
                    if self.provider == "groq":
                        from groq import Groq
                        self.client = Groq(api_key=api_key)
                    else:
                        from openai import OpenAI
                        self.client = OpenAI(api_key=api_key)
                    self._current_key = api_key
                except Exception as e:
                    print(f"[Transcriber Init Warning] Could not init client: {e}")
        return self.client

    def transcribe(self, audio_file_path: str, language: str = None) -> str:
        """
        Transcribes audio WAV file into text using automatic language detection.

        :param audio_file_path: Path to WAV audio file.
        :param language: Optional language code (None for auto-detection).
        :return: Transcribed text string.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        if os.path.getsize(audio_file_path) < 1000:
            return ""

        client = self._get_client()
        if not client:
            raise ValueError(
                f"API Key for provider '{self.provider.upper()}' is missing or invalid. Please configure GROQ_API_KEY in Vercel Environment Variables."
            )

        try:
            stt_model = config.STT_MODEL

            with open(audio_file_path, "rb") as audio_file:
                if self.provider == "groq":
                    kwargs = {
                        "file": (os.path.basename(audio_file_path), audio_file.read()),
                        "model": stt_model,
                        "prompt": "Automatically detect speech language (English, Hindi, or Hinglish) and transcribe accurately.",
                        "response_format": "json",
                        "timeout": 25.0,
                    }
                    if language:
                        kwargs["language"] = language

                    transcript_response = client.audio.transcriptions.create(**kwargs)
                    text = transcript_response.text.strip()
                else:
                    kwargs = {
                        "model": stt_model,
                        "file": audio_file,
                        "prompt": "Automatically detect speech language (English, Hindi, or Hinglish) and transcribe accurately.",
                        "timeout": 25.0,
                    }
                    if language:
                        kwargs["language"] = language

                    transcript_response = client.audio.transcriptions.create(**kwargs)
                    text = transcript_response.text.strip()

            return text
        except Exception as e:
            print(f"[Transcriber Error] {self.provider.upper()} Whisper transcription failed: {e}")
            raise e


if __name__ == "__main__":
    t = Transcriber()
    print(f"Transcriber initialized ({config.API_PROVIDER})")
