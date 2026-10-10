# 🎙️ Deva Google Assistant AI Platform (Groq, Whisper & JSON Knowledge Base)

A complete **Web Platform & Floating Pop-Up Widget** for your Personal Voice Assistant **Deva**, featuring:
- **Groq AI** (`openai/gpt-oss-120b`) for ultra-fast response generation.
- **Groq Whisper** (`whisper-large-v3-turbo`) for instant audio transcription.
- **JSON Knowledge Base (`knowledge_base.json`)** to store team passwords, daily routines, meeting links, and team Q&A.
- **Continuous Siri-like Background Listener** for the `"open deva"` wake phrase.
- **Man & Woman Speaking Voice Models**.
- **Voice Frequency Tone & Speed Controls**.

---

## 🌟 Key Features

- **📖 Team JSON Knowledge Base (`knowledge_base.json`):** Store and manage custom questions and answers (e.g., passwords, daily routines, team schedules, meeting links). Anyone on your team can view, add, or delete entries directly from the Web UI modal!
- **🌐 Deva Web Platform & Pop-Up Widget:** Google Assistant 4-color glowing dots UI with a floating pop-up drawer widget.
- **🎙️ Siri-Style Background Listener:** Continuously listens for `"open deva"` or `"hey deva"` in the background and pops up automatically.
- **✨ Automatic Language Detection:** Detects English, Hindi (हिंदी), and Hinglish automatically and answers in the matching language.
- **🎛️ Collapsible Voice Frequency Panel:** Hidden/held by default; expand to adjust sound tone pitch and talking speed.

---

## 📁 Project Structure

```text
d:/G_AI/
├── knowledge_base.json   # JSON file storing team Q&A, passwords & routines
├── knowledge_manager.py  # Knowledge Base CRUD manager module
├── server.py             # Flask Web Server & REST API backend (http://127.0.0.1:5000)
├── static/
│   └── index.html        # Google Assistant Web App & JSON Knowledge Base UI Modal
├── deva_background_listener.py # Desktop background wake-word listener (Siri style)
├── .env                  # Environment file pre-configured with your Groq API key
├── config.py             # Global system configuration manager
├── audio_recorder.py     # SoundDevice microphone recording module
├── transcriber.py        # Groq Whisper Speech-to-Text module
├── assistant.py          # Groq LLM assistant with JSON Knowledge Base context
├── tts_engine.py         # Text-to-speech synthesis module (pyttsx3)
├── main.py               # Combined CLI & Web Application launcher
├── test_components.py    # Automated system diagnostics script
└── README.md             # Project documentation
```

---

## 📖 Managing Team Knowledge Base (JSON)

### 1. From the Web UI:
1. Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)**.
2. Click **`Team Q&A (JSON)`** in the top navigation header.
3. View stored Q&A entries, add new entries (e.g. Question: `"database password"`, Answer: `"DB_PASS_2026"`), or delete entries.
4. Speak or type your question to Deva (e.g. *"What is my daily routine?"* or *"What is the wifi password?"*), and Deva will fetch the answer directly from `knowledge_base.json`!

### 2. From `knowledge_base.json` Directly:
You can also edit `knowledge_base.json` in any text editor:
```json
{
  "daily routine": "Team standup at 9:30 AM, code review at 11:00 AM, lunch at 1:00 PM.",
  "wifi password": "The WiFi network is Deva_Office_5G and password is DevaSecret@2026!"
}
```

---

## 🚀 How to Run

Start the web server:
```bash
python server.py
```
Or use the launcher:
```bash
python main.py
```
*(Select Option `[6]`)*
