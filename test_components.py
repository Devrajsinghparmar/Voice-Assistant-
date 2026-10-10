"""
System Component Diagnostic Test Script.

Run this script to verify microphone input, TTS output, and Groq/OpenAI API connectivity.
"""

import sys
import time
from config import config
from audio_recorder import AudioRecorder
from tts_engine import TTSEngine
from assistant import VoiceAssistant
from transcriber import Transcriber

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def test_tts():
    print("\n--- [1/4] Testing Text-to-Speech Engine (pyttsx3) ---")
    tts = TTSEngine()
    test_phrase = "Testing text to speech engine. System check operational."
    tts.speak(test_phrase)
    print("[PASSED] TTS Test Complete.")


def test_microphone():
    print("\n--- [2/4] Testing Audio Microphone Recording ---")
    recorder = AudioRecorder()
    if not AudioRecorder.check_input_device():
        print("[WARNING] No microphone input device detected on system!")
        return False
    
    print("Microphone found. Recording 3 seconds test audio...")
    audio_path = recorder.record_fixed(3.0)
    print(f"[PASSED] Microphone Test Complete. Saved to {audio_path}")
    return True


def test_api_connection():
    provider = config.API_PROVIDER.upper()
    print(f"\n--- [3/4] Testing {provider} API Key & LLM Model ({config.LLM_MODEL}) ---")
    if not config.validate_api_key():
        print(f"[FAIL] {provider} API key is missing or set to default placeholder in .env!")
        print("       Please update your .env file with GROQ_API_KEY=gsk_your_key")
        return False
    
    assistant = VoiceAssistant()
    response = assistant.get_response("Hello, confirm you are working.")
    print(f"Assistant Response: {response}")
    print(f"[PASSED] {provider} LLM Test Complete.")
    return True


def test_whisper_stt(mic_ok: bool, api_ok: bool):
    provider = config.API_PROVIDER.upper()
    print(f"\n--- [4/4] Testing Speech-to-Text Transcriber ({provider} Whisper: {config.STT_MODEL}) ---")
    if not mic_ok:
        print("[SKIP] Skipping Whisper STT test since microphone test was not successful.")
        return
    
    if not api_ok:
        print(f"[SKIP] Skipping Whisper STT test (Requires valid {provider} API key).")
        return
    
    transcriber = Transcriber()
    try:
        text = transcriber.transcribe(config.TEMP_AUDIO_FILE)
        print(f"Transcribed Text from test recording: '{text}'")
        print(f"[PASSED] {provider} Whisper STT Test Complete.")
    except Exception as e:
        print(f"[FAIL] {provider} Whisper STT Test Failed: {e}")


def main():
    print("==================================================")
    print("    Personal Voice Assistant System Diagnostics   ")
    print("==================================================")
    print(f"  Provider: {config.API_PROVIDER.upper()} | Model: {config.LLM_MODEL}")
    
    test_tts()
    mic_ok = test_microphone()
    api_ok = test_api_connection()
    test_whisper_stt(mic_ok, api_ok)

    print("\n==================================================")
    print("            Diagnostic Checks Summary             ")
    print("==================================================")
    print(f"Microphone:   {'PASSED' if mic_ok else 'FAILED / NOT DETECTED'}")
    print(f"API Provider: {'PASSED' if api_ok else 'FAILED / MISSING KEY'} ({config.API_PROVIDER.upper()})")
    print("==================================================\n")


if __name__ == "__main__":
    main()
