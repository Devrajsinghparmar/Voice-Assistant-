"""
Main Application Entry Point for Personal Voice Assistant (Deva).

Provides CLI interface & launch options for Google Assistant Web Platform with:
- Man & Woman voice models
- English, Hindi (हिंदी), and Hinglish auto-language detection
- JSON Knowledge Base (passwords, daily routines, team Q&A)
"""

import sys
import os
import time
import webbrowser
from colorama import init, Fore, Style

from config import config
from audio_recorder import AudioRecorder
from transcriber import Transcriber
from assistant import VoiceAssistant
from tts_engine import TTSEngine
from knowledge_manager import KnowledgeManager

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Initialize Colorama for cross-platform ANSI terminal styling
init(autoreset=True)


class VoiceAssistantApp:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.assistant = VoiceAssistant()
        self.tts = TTSEngine()
        self.km = KnowledgeManager()

    def print_header(self):
        os.system("cls" if os.name == "nt" else "clear")
        voice_label = "Man (Male)" if self.tts.voice_gender in ["male", "man"] else "Woman (Female)"
        print(Fore.CYAN + Style.BRIGHT + "=" * 60)
        print(Fore.CYAN + Style.BRIGHT + "    [DEVA GOOGLE ASSISTANT VOICE AI & WEB PLATFORM]    ")
        print(Fore.CYAN + Style.BRIGHT + "=" * 60)
        print(
            Fore.YELLOW
            + f"  Provider: {config.API_PROVIDER.upper()} | Model: {config.LLM_MODEL}\n"
            + f"  Language: ✨ Auto-Detect | Voice: {voice_label} | JSON Q&A: {len(self.km.knowledge)} entries"
        )
        print(Fore.CYAN + "-" * 60)

    def print_menu(self):
        print("\nPlease select an option:")
        print(Fore.GREEN + "  [1]" + Fore.WHITE + " Push-to-Talk Voice Command (CLI)")
        print(Fore.GREEN + "  [2]" + Fore.WHITE + " Hands-Free Continuous Voice Mode (CLI)")
        print(Fore.GREEN + "  [3]" + Fore.WHITE + " Text Input Mode (CLI)")
        print(Fore.GREEN + "  [4]" + Fore.WHITE + " Assistant Settings & Team Knowledge Base (JSON)")
        print(Fore.GREEN + "  [5]" + Fore.WHITE + " Run System Component Diagnostics")
        print(Fore.CYAN + "  [6]" + Fore.WHITE + " 🌐 Launch Deva Web Assistant Platform (Browser)")
        print(Fore.RED + "  [7]" + Fore.WHITE + " Exit Application\n")

    def run_voice_turn(self, use_silence_detection: bool = False) -> bool:
        if not config.validate_api_key():
            print(
                Fore.RED
                + f"\n[ERROR] Missing {config.API_PROVIDER.upper()} API Key! Please configure GROQ_API_KEY in .env file."
            )
            self.tts.speak("API key missing. Please update your env file.")
            return False

        if not AudioRecorder.check_input_device():
            print(Fore.RED + "\n[ERROR] No microphone input device detected. Please connect a microphone.")
            self.tts.speak("No microphone detected.")
            return False

        try:
            if use_silence_detection:
                audio_path = self.recorder.record_until_silence()
            else:
                audio_path = self.recorder.record_fixed(config.AUDIO_DURATION)

            print(Fore.CYAN + f"\n[Transcribing voice (Auto-Detect)...]")
            user_text = self.transcriber.transcribe(audio_path)

            if not user_text.strip():
                print(Fore.YELLOW + "[WARNING] Could not detect any speech. Please try speaking again.")
                self.tts.speak("I didn't hear anything. Please try again.")
                return True

            print(Fore.GREEN + f"\nUser Said: " + Fore.WHITE + f'"{user_text}"')

            if user_text.lower().strip() in ["exit", "quit", "goodbye", "stop"]:
                print(Fore.YELLOW + "\nGoodbye! Have a great day.")
                self.tts.speak("Goodbye!")
                return False

            print(Fore.CYAN + f"\n[Generating response via {config.API_PROVIDER.upper()} ({config.LLM_MODEL})...]")
            reply = self.assistant.get_response(user_text)

            voice_label = "Man Voice" if self.tts.voice_gender in ["male", "man"] else "Woman Voice"
            print(Fore.MAGENTA + Style.BRIGHT + f"\nDeva ({voice_label}): " + Fore.WHITE + reply)
            self.tts.speak(reply)
            return True

        except Exception as e:
            print(Fore.RED + f"\n[ERROR] Error during voice interaction: {e}")
            return True

    def run_continuous_voice_mode(self):
        print(Fore.CYAN + "\n=== Hands-Free Continuous Voice Mode ===")
        print(Fore.YELLOW + "Press Ctrl+C or say 'exit' / 'stop' at any time to return to main menu.\n")
        self.tts.speak("Continuous voice mode activated. Speak after the prompt.")

        try:
            while True:
                success = self.run_voice_turn(use_silence_detection=True)
                if not success:
                    break
                print(Fore.CYAN + "\n" + "-" * 40)
                time.sleep(1)
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nExiting Continuous Voice Mode...")

    def run_text_mode(self):
        print(Fore.CYAN + "\n=== Text Input Mode ===")
        print(Fore.YELLOW + "Type 'wifi password', 'daily routine', or your questions below. Type 'exit' to return.\n")

        while True:
            try:
                user_input = input(Fore.GREEN + "User: " + Fore.WHITE).strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "back"]:
                    break

                reply = self.assistant.get_response(user_input)
                voice_label = "Man Voice" if self.tts.voice_gender in ["male", "man"] else "Woman Voice"
                print(Fore.MAGENTA + Style.BRIGHT + f"\nDeva ({voice_label}): " + Fore.WHITE + reply)
                self.tts.speak(reply)
                print()
            except KeyboardInterrupt:
                break

    def show_knowledge_base_menu(self):
        while True:
            print(Fore.CYAN + "\n=== Team Knowledge Base (knowledge_base.json) ===")
            entries = self.km.load_knowledge()
            if not entries:
                print(Fore.YELLOW + "  (No entries in JSON knowledge base)")
            else:
                for idx, (q, a) in enumerate(entries.items(), 1):
                    print(f"  {idx}. Question/Key: {Fore.GREEN}{q.title()}{Style.RESET_ALL}")
                    print(f"     Answer:       {a}")

            print(Fore.GREEN + "\nOptions:")
            print("  [a] Add / Update Entry")
            print("  [d] Delete Entry")
            print("  [b] Back")

            choice = input("\nEnter choice: ").strip().lower()
            if choice == "a":
                q = input("Enter Question / Key (e.g. 'wifi password'): ").strip()
                a = input("Enter Answer (e.g. 'DevaSecret2026'): ").strip()
                if q and a:
                    self.km.add_entry(q, a)
                    self.assistant.refresh_knowledge()
                    print(Fore.GREEN + f"[SUCCESS] Entry for '{q}' saved to knowledge_base.json!")
            elif choice == "d":
                q = input("Enter Question / Key to delete: ").strip()
                if q:
                    if self.km.delete_entry(q):
                        self.assistant.refresh_knowledge()
                        print(Fore.GREEN + f"[SUCCESS] Deleted '{q}'!")
                    else:
                        print(Fore.RED + "Entry not found.")
            elif choice == "b":
                break

    def show_settings_menu(self):
        while True:
            voice_label = "Man Voice (Male)" if self.tts.voice_gender in ["male", "man"] else "Woman Voice (Female)"
            print(Fore.CYAN + "\n=== Settings & System Status ===")
            print(f"  1. API Provider:       {config.API_PROVIDER.upper()}")
            print(f"  2. LLM Model:           {config.LLM_MODEL}")
            print(f"  3. Active Language:     ✨ Auto-Detect (English/Hindi/Hinglish)")
            print(f"  4. Active Voice:        {voice_label}")
            print(f"  5. JSON Knowledge Q&A: {len(self.km.knowledge)} entries")
            print(Fore.GREEN + "\nOptions:")
            print("  [k] Manage Team Knowledge Base (JSON)")
            print("  [v] Switch Voice Model (Woman / Man)")
            print("  [r] Reset Conversation Memory")
            print("  [b] Back to Main Menu")

            choice = input("\nEnter choice: ").strip().lower()
            if choice == "k":
                self.show_knowledge_base_menu()
            elif choice == "v":
                new_gender = "man" if self.tts.voice_gender == "female" else "woman"
                voice_name = self.tts.set_voice_gender(new_gender)
                label = "Man Voice" if new_gender == "man" else "Woman Voice"
                print(Fore.GREEN + f"[SUCCESS] Voice switched to {label} ({voice_name})!")
                self.tts.speak(f"{label} activated.")
            elif choice == "r":
                self.assistant.reset_conversation()
                print(Fore.GREEN + "[SUCCESS] Conversation memory cleared!")
                self.tts.speak("Conversation memory has been reset.")
            elif choice == "b":
                break

    def launch_web_platform(self):
        print(Fore.CYAN + "\n=== Launching Deva Web Assistant Platform ===")
        print(Fore.GREEN + "Opening browser at http://127.0.0.1:5000 ...")
        webbrowser.open("http://127.0.0.1:5000")
        from server import start_server
        start_server(port=5000, host="127.0.0.1")

    def start(self):
        while True:
            self.print_header()
            self.print_menu()
            try:
                choice = input(Fore.YELLOW + "Select [1-7]: " + Fore.WHITE).strip()

                if choice == "1":
                    self.run_voice_turn(use_silence_detection=False)
                    input(Fore.CYAN + "\nPress Enter to return to menu...")
                elif choice == "2":
                    self.run_continuous_voice_mode()
                elif choice == "3":
                    self.run_text_mode()
                elif choice == "4":
                    self.show_settings_menu()
                elif choice == "5":
                    from test_components import main as run_diagnostics
                    run_diagnostics()
                    input(Fore.CYAN + "\nPress Enter to return to menu...")
                elif choice == "6":
                    self.launch_web_platform()
                elif choice == "7":
                    print(Fore.CYAN + "\nThank you for using Deva Voice AI. Goodbye!")
                    break
                else:
                    print(Fore.RED + "Invalid choice! Please select 1 to 7.")
                    time.sleep(1)
            except KeyboardInterrupt:
                print(Fore.CYAN + "\nExiting application. Goodbye!")
                break


if __name__ == "__main__":
    app = VoiceAssistantApp()
    app.start()
