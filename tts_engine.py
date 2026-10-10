"""
Text-to-Speech (TTS) Engine Module using pyttsx3 and OpenAI TTS API.

Supports dynamic voice frequency tone (pitch), speech speed (rate), and Man/Woman voice models.
"""

import os
import sys
import pyttsx3
from config import config

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class TTSEngine:
    def __init__(
        self,
        engine_type: str = config.TTS_ENGINE,
        rate: int = config.VOICE_RATE,
        pitch: float = config.VOICE_PITCH,
        volume: float = config.VOICE_VOLUME,
        voice_gender: str = config.TTS_VOICE_GENDER,
    ):
        self.engine_type = engine_type
        self.rate = rate
        self.pitch = pitch
        self.volume = volume
        self.voice_gender = voice_gender.lower()

        try:
            self.pyttsx3_engine = pyttsx3.init()
            self.set_voice_gender(self.voice_gender)
        except Exception as e:
            print(f"[TTS Warning] Could not initialize pyttsx3 engine: {e}")
            self.pyttsx3_engine = None

    def set_voice_gender(self, gender: str) -> str:
        """Sets voice model to Male ('man') or Female ('woman')."""
        self.voice_gender = gender.lower()
        if not self.pyttsx3_engine:
            return "Default Voice"

        self.pyttsx3_engine.setProperty("rate", self.rate)
        self.pyttsx3_engine.setProperty("volume", self.volume)

        voices = self.pyttsx3_engine.getProperty("voices")
        if not voices:
            return "Default Voice"

        target = "male" if self.voice_gender in ["male", "man"] else "female"
        selected_voice = voices[0]

        for v in voices:
            v_name = v.name.lower()
            if target == "male":
                if "david" in v_name or "male" in v_name or "george" in v_name or "mark" in v_name:
                    selected_voice = v
                    break
            else:
                if "zira" in v_name or "female" in v_name or "susan" in v_name or "hazel" in v_name:
                    selected_voice = v
                    break

        self.pyttsx3_engine.setProperty("voice", selected_voice.id)
        return selected_voice.name

    def set_speech_rate(self, rate: int):
        """Sets speech speed rate in Words Per Minute (100 to 300)."""
        self.rate = max(80, min(350, int(rate)))
        if self.pyttsx3_engine:
            self.pyttsx3_engine.setProperty("rate", self.rate)

    def set_pitch_tone(self, pitch: float):
        """Sets voice frequency tone pitch multiplier (0.5 to 1.8)."""
        self.pitch = max(0.5, min(2.0, float(pitch)))

    def speak(self, text: str, gender: str = None, rate: int = None, pitch: float = None) -> None:
        """
        Converts text string into audible speech using specified voice frequency tone, speed, and gender.

        :param text: Text string to speak.
        :param gender: Optional voice model ('man' or 'woman').
        :param rate: Optional speech rate speed in WPM.
        :param pitch: Optional frequency pitch tone.
        """
        if not text.strip():
            return

        if gender:
            self.set_voice_gender(gender)
        if rate:
            self.set_speech_rate(rate)
        if pitch:
            self.set_pitch_tone(pitch)

        active_gender_label = "Man Voice" if self.voice_gender in ["male", "man"] else "Woman Voice"
        print(f"\n[TTS Speaking ({active_gender_label} | Speed: {self.rate}wpm | Pitch Tone: {self.pitch}x)]: {text}\n")

        if self.engine_type == "openai" and config.validate_api_key():
            try:
                self._speak_openai(text, self.voice_gender)
                return
            except Exception as e:
                print(f"[TTS Error] OpenAI Speech failed, falling back to pyttsx3: {e}")

        self._speak_pyttsx3(text)

    def _speak_pyttsx3(self, text: str) -> None:
        """Audible speech using pyttsx3 engine."""
        if self.pyttsx3_engine:
            try:
                self.pyttsx3_engine.say(text)
                self.pyttsx3_engine.runAndWait()
            except Exception as e:
                print(f"[TTS Error] pyttsx3 playback error: {e}")
        else:
            print(f"[TTS Fallback Console]: {text}")

    def _speak_openai(self, text: str, gender: str) -> None:
        """Audible speech using OpenAI Audio Speech API."""
        from openai import OpenAI

        client = OpenAI(api_key=config.OPENAI_API_KEY)
        speech_file = "response_speech.mp3"
        voice_name = "onyx" if gender in ["male", "man"] else "nova"

        response = client.audio.speech.create(
            model="tts-1",
            voice=voice_name,
            input=text,
        )
        response.stream_to_file(speech_file)

        if os.name == "nt":
            os.system(f"start /min wmplayer \"{os.path.abspath(speech_file)}\"")
        else:
            os.system(f"afplay \"{speech_file}\" || mpg123 \"{speech_file}\"")


if __name__ == "__main__":
    tts = TTSEngine()
    tts.speak("Testing Deep Tone Pitch", pitch=0.6, rate=150)
    tts.speak("Testing High Crisp Tone Pitch", pitch=1.4, rate=200)
