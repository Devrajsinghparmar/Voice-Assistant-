"""
Flask Web Server & API Backend for Personal Voice Assistant (Deva).

Supports system actions (opening camera, desktop apps, new browser tabs),
system-wide background wake word listener, and flags JSON Knowledge Base responses.
"""

import os
import sys
import tempfile
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from config import config
from transcriber import Transcriber
from assistant import VoiceAssistant
from tts_engine import TTSEngine
from knowledge_manager import KnowledgeManager
from deva_background_listener import BackgroundWakeListener

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = Flask(__name__, static_folder="static")
CORS(app)

# Initialize core services
transcriber = Transcriber()
assistant = VoiceAssistant()
tts = TTSEngine()
km = KnowledgeManager()


def start_background_wake_service():
    """Runs BackgroundWakeListener in a background daemon thread."""
    try:
        listener = BackgroundWakeListener()
        listener.listen_loop()
    except Exception as e:
        print(f"[Background Listener Service Warning] {e}")


@app.route("/")
def index():
    """Serves the Deva Google Assistant web interface."""
    return send_from_directory("static", "index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    """Returns system status and current configuration."""
    return jsonify({
        "assistant_name": config.ASSISTANT_NAME,
        "provider": config.API_PROVIDER.upper(),
        "llm_model": config.LLM_MODEL,
        "stt_model": config.STT_MODEL,
        "tts_engine": config.TTS_ENGINE,
        "voice_gender": tts.voice_gender,
        "voice_pitch": tts.pitch,
        "voice_rate": tts.rate,
        "language": "auto-detect",
        "knowledge_count": len(km.knowledge),
        "api_key_configured": config.validate_api_key(),
        "memory_count": len(assistant.conversation_history) - 1
    })


@app.route("/api/knowledge", methods=["GET", "POST", "DELETE"])
def handle_knowledge():
    """API Endpoint to view, add, or delete entries in knowledge_base.json."""
    if request.method == "GET":
        km.load_knowledge()
        return jsonify({"knowledge": km.knowledge, "status": "success"})

    elif request.method == "POST":
        data = request.json or {}
        question = data.get("question", "").strip()
        answer = data.get("answer", "").strip()

        if not question or not answer:
            return jsonify({"error": "Both question and answer are required"}), 400

        success = km.add_entry(question, answer)
        assistant.refresh_knowledge()

        if success:
            return jsonify({"message": f"Successfully added entry for '{question}'", "status": "success"})
        return jsonify({"error": "Failed to save entry to JSON"}), 500

    elif request.method == "DELETE":
        data = request.json or {}
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"error": "Question parameter required"}), 400

        success = km.delete_entry(question)
        assistant.refresh_knowledge()

        if success:
            return jsonify({"message": f"Deleted entry for '{question}'", "status": "success"})
        return jsonify({"error": "Entry not found"}), 404


@app.route("/api/process-audio", methods=["POST"])
def process_audio():
    """Processes recorded audio blobs with JSON Knowledge Base detection and system actions."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "Empty audio file"}), 400

    voice_gender = request.form.get("voice_gender", "woman").lower()
    pitch = float(request.form.get("pitch", 1.0))
    speed = float(request.form.get("speed", 1.0))

    wpm_rate = int(175 * speed)

    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "web_input_audio.wav")
    audio_file.save(temp_path)

    try:
        user_text = transcriber.transcribe(temp_path)
        if not user_text.strip():
            return jsonify({
                "user_text": "",
                "assistant_reply": "I couldn't hear any speech. Please try speaking again.",
                "voice_gender": voice_gender,
                "is_knowledge_base": False,
                "action": None,
                "status": "empty_speech"
            })

        assistant_reply, is_kb, action = assistant.get_response_info(user_text)

        # Only speak out loud if NOT from confidential JSON Knowledge Base
        if not is_kb and request.form.get("play_local_tts", "false").lower() == "true":
            tts.speak(assistant_reply, gender=voice_gender, rate=wpm_rate, pitch=pitch)

        return jsonify({
            "user_text": user_text,
            "assistant_reply": assistant_reply,
            "voice_gender": voice_gender,
            "pitch": pitch,
            "speed": speed,
            "is_knowledge_base": is_kb,
            "action": action,
            "status": "success"
        })

    except Exception as e:
        print(f"[Web API Error] {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@app.route("/api/chat", methods=["POST"])
def text_chat():
    """Endpoint for text-based queries with JSON Knowledge Base detection and system actions."""
    data = request.json or {}
    user_text = data.get("message", "").strip()
    voice_gender = data.get("voice_gender", "woman").lower()
    pitch = float(data.get("pitch", 1.0))
    speed = float(data.get("speed", 1.0))

    if not user_text:
        return jsonify({"error": "Empty message"}), 400

    try:
        assistant_reply, is_kb, action = assistant.get_response_info(user_text)
        return jsonify({
            "user_text": user_text,
            "assistant_reply": assistant_reply,
            "voice_gender": voice_gender,
            "pitch": pitch,
            "speed": speed,
            "is_knowledge_base": is_kb,
            "action": action,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wake-deva", methods=["POST"])
def wake_deva():
    """Endpoint triggered when user says 'open deva' or starts up."""
    greeting, is_kb, action = assistant.get_response_info("open deva")
    return jsonify({
        "user_text": "open deva",
        "assistant_reply": greeting,
        "is_knowledge_base": is_kb,
        "action": action,
        "status": "success"
    })


@app.route("/api/reset", methods=["POST"])
def reset_memory():
    """Resets conversation context history."""
    assistant.reset_conversation()
    return jsonify({"message": "Conversation memory reset successfully", "status": "success"})


def start_server(port=5000, host="127.0.0.1", debug=False):
    print(f"\n==================================================")
    print(f"  🎙️ DEVA GOOGLE ASSISTANT WEB PLATFORM IS RUNNING!")
    print(f"  URL: http://{host}:{port}")
    print(f"  Provider: {config.API_PROVIDER.upper()} ({config.LLM_MODEL})")
    print(f"  System-Wide Listener: Active (Say 'open deva' anywhere on PC)")
    print(f"==================================================\n")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    # Launch system-wide background wake listener in background thread
    bg_thread = threading.Thread(target=start_background_wake_service, daemon=True)
    bg_thread.start()

    start_server()
