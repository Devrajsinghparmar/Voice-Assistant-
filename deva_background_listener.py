"""
Desktop Background Wake-Word Listener Service for Deva.

Runs continuously in the background (like Siri / Google Assistant).
When the user speaks "open deva" or "hey deva" anywhere on the PC
(while using WhatsApp, LinkedIn, Chrome, etc.), it pops up Deva over all apps!
"""

import sys
import time
import os
import tempfile
import webbrowser
import subprocess
import ctypes
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from config import config
from transcriber import Transcriber

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def bring_or_open_popup():
    """
    Pops up the Deva Assistant window on top of all desktop apps (WhatsApp, LinkedIn, etc.).
    Uses Windows API to restore and bring window to front, or launches Edge/Chrome app mode.
    """
    url = "http://127.0.0.1:5000/?wake=true"
    window_found = False

    if sys.platform == "win32":
        try:
            user32 = ctypes.windll.user32
            top_hwnds = []

            def enum_windows_cb(hwnd, extra):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        title = buff.value.lower()
                        if "deva" in title or "127.0.0.1:5000" in title or "localhost:5000" in title:
                            top_hwnds.append(hwnd)
                return True

            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
            user32.EnumWindows(WNDENUMPROC(enum_windows_cb), 0)

            if top_hwnds:
                hwnd = top_hwnds[0]
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE / SW_SHOWNORMAL
                user32.SetForegroundWindow(hwnd)
                window_found = True
        except Exception as e:
            print(f"[Focus Window Warning] {e}")

    if not window_found:
        # Launch standalone App Mode pop-up window in Microsoft Edge or Chrome
        try:
            subprocess.Popen("start msedge --app=http://127.0.0.1:5000/?wake=true", shell=True)
        except Exception:
            webbrowser.open(url)


class BackgroundWakeListener:
    def __init__(self, sample_rate=16000, chunk_duration=3.0, energy_threshold=100):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.energy_threshold = energy_threshold  # Lower threshold for high mic sensitivity
        self.transcriber = Transcriber()
        self.running = False

    def listen_loop(self):
        """Continuously monitors microphone in background like Siri / Google Assistant."""
        print(f"\n==================================================")
        print(f"  🎙️ DEVA SYSTEM-WIDE BACKGROUND LISTENER ACTIVE")
        print(f"  Listening 24/7 anywhere on PC (WhatsApp, LinkedIn, Desktop)...")
        print(f"  Say: 'open deva', 'hey deva', or 'deva' to pop up!")
        print(f"==================================================\n")

        self.running = True
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "background_wake_chunk.wav")

        chunk_samples = int(self.sample_rate * self.chunk_duration)
        wake_words = [
            "open deva", "deva open", "hey deva", "hello deva", 
            "ok deva", "deva", "deba open", "open deba", "open deva assistant"
        ]

        while self.running:
            try:
                # Record background audio buffer
                audio_data = sd.rec(
                    chunk_samples,
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype="int16",
                )
                sd.wait()

                # Calculate volume energy (RMS)
                rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))

                # If voice activity detected above noise threshold
                if rms > self.energy_threshold:
                    sys.stdout.write(f"\r👂 [Speech detected (RMS: {int(rms)}) -> Checking wake phrase...]   ")
                    sys.stdout.flush()

                    wavfile.write(temp_file, self.sample_rate, audio_data)
                    transcript = self.transcriber.transcribe(temp_file).lower().strip()

                    sys.stdout.write(f"\r[Heard: '{transcript}']                                             \n")
                    sys.stdout.flush()

                    if any(w in transcript for w in wake_words):
                        print(f"\n✨ [WAKE PHRASE MATCHED!] Popping up Deva Assistant Window over all apps...\n")
                        bring_or_open_popup()
                        time.sleep(3.0)  # Cool-down to avoid double trigger

            except KeyboardInterrupt:
                print("\n[Background Listener Stopped]")
                self.running = False
                break
            except Exception as e:
                time.sleep(1)

        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass


if __name__ == "__main__":
    listener = BackgroundWakeListener()
    listener.listen_loop()
