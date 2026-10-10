"""
Audio Recording Module using SoundDevice and SciPy.

Captures microphone audio input and saves it to a WAV file for speech processing.
"""

import sys
import time
import wave
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from config import config

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class AudioRecorder:
    def __init__(
        self,
        sample_rate: int = config.SAMPLE_RATE,
        channels: int = config.AUDIO_CHANNELS,
        filename: str = config.TEMP_AUDIO_FILE,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.filename = filename

    @staticmethod
    def list_microphones():
        """Lists available input audio devices."""
        devices = sd.query_devices()
        input_devices = []
        for i, dev in enumerate(devices):
            if dev["max_input_channels"] > 0:
                input_devices.append((i, dev["name"]))
        return input_devices

    @staticmethod
    def check_input_device() -> bool:
        """Checks if at least one audio input device (microphone) is available."""
        try:
            devices = sd.query_devices()
            for dev in devices:
                if dev["max_input_channels"] > 0:
                    return True
        except Exception:
            pass
        return False

    def record_fixed(self, duration: float = config.AUDIO_DURATION) -> str:
        """
        Records audio for a fixed duration in seconds.

        :param duration: Duration to record in seconds.
        :return: Path to saved WAV audio file.
        """
        print(f"\n[Listening for {duration} seconds... Speak now!]")
        
        # Record audio block
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
        )
        
        # Display progress countdown
        for remaining in range(int(duration), 0, -1):
            sys.stdout.write(f"\rListening... {remaining}s remaining ")
            sys.stdout.flush()
            time.sleep(1)
            
        sd.wait()  # Wait until recording is finished
        sys.stdout.write("\r[Recording complete! Processing...]    \n")
        sys.stdout.flush()

        # Save to WAV file
        wavfile.write(self.filename, self.sample_rate, audio_data)
        return self.filename

    def record_until_silence(
        self, silence_threshold: float = 500, max_silence_sec: float = 2.0, max_duration_sec: float = 15.0
    ) -> str:
        """
        Records audio dynamically until a silence threshold is maintained or max duration reached.

        :param silence_threshold: Amplitude RMS threshold to consider as silence.
        :param max_silence_sec: Seconds of silence after speech to stop recording.
        :param max_duration_sec: Maximum allowed recording duration in seconds.
        :return: Path to saved WAV audio file.
        """
        print("\n[Dynamic Listening... Speak now (Recording stops on silence)]")
        
        chunk_duration = 0.1  # 100ms chunks
        chunk_size = int(self.sample_rate * chunk_duration)
        silence_chunks_needed = int(max_silence_sec / chunk_duration)
        max_chunks = int(max_duration_sec / chunk_duration)

        frames = []
        silent_chunks = 0
        speech_started = False

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
        ) as stream:
            for chunk_idx in range(max_chunks):
                data, overflowed = stream.read(chunk_size)
                frames.append(data)
                
                # Calculate Root Mean Square (RMS) energy
                rms = np.sqrt(np.mean(data.astype(np.float32) ** 2))

                if rms > silence_threshold:
                    speech_started = True
                    silent_chunks = 0
                    sys.stdout.write(f"\r[Speaking... RMS: {int(rms)}]")
                    sys.stdout.flush()
                else:
                    if speech_started:
                        silent_chunks += 1
                        sys.stdout.write(f"\r[Silence detected: {silent_chunks * chunk_duration:.1f}s]")
                        sys.stdout.flush()
                        if silent_chunks >= silence_chunks_needed:
                            break
                    else:
                        sys.stdout.write(f"\r[Listening for voice... RMS: {int(rms)}]")
                        sys.stdout.flush()

        sys.stdout.write("\r[Recording finished! Processing...]         \n")
        sys.stdout.flush()

        # Combine all frames into a single numpy array
        if frames:
            recorded_audio = np.concatenate(frames, axis=0)
        else:
            recorded_audio = np.zeros((0, self.channels), dtype="int16")

        wavfile.write(self.filename, self.sample_rate, recorded_audio)
        return self.filename


if __name__ == "__main__":
    recorder = AudioRecorder()
    if recorder.check_input_device():
        print("Microphone found!")
        outfile = recorder.record_fixed(3)
        print(f"Recorded file saved to: {outfile}")
    else:
        print("No microphone input device detected.")
