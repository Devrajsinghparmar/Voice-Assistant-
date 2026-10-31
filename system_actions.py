"""
System Actions Manager for Deva Voice Assistant.
Handles opening system apps (Camera, Notepad, Calculator, Explorer, etc.)
and browser tabs / web searches.
"""

import os
import sys
import subprocess
import webbrowser
from typing import Tuple, Dict, Optional


def _safe_open_url(url: str):
    """Safely opens URL in desktop browser if running locally."""
    try:
        webbrowser.open(url)
    except Exception:
        pass


class SystemActionsManager:
    """Detects and executes system commands like camera, apps, and browser tabs."""

    @staticmethod
    def execute_action(user_text: str) -> Tuple[bool, str, Optional[Dict[str, str]]]:
        """
        Checks if user_text contains a command to open camera, app, or browser tab.
        
        Returns:
            (handled: bool, reply_text: str, action_data: dict)
        """
        text = user_text.strip().lower()

        # 1. System Camera
        if any(cmd in text for cmd in ["open camera", "camera open", "open webcam", "start camera", "system camera", "launch camera"]):
            try:
                if sys.platform == "win32":
                    subprocess.Popen("start microsoft.windows.camera:", shell=True)
                return True, "Opening system camera...", {"type": "open_app", "target": "camera"}
            except Exception as e:
                return True, f"Could not open camera: {e}", None
            
      
        # 2. Notepad
        if any(cmd in text for cmd in ["open notepad", "start notepad", "launch notepad"]):
            try:
                subprocess.Popen(["notepad.exe"])
                return True, "Opening Notepad...", {"type": "open_app", "target": "notepad"}
            except Exception as e:
                return True, f"Failed to open Notepad: {e}", None

        # 3. Calculator
        if any(cmd in text for cmd in ["open calculator", "start calculator", "open calc", "launch calc"]):
            try:
                subprocess.Popen(["calc.exe"])
                return True, "Opening Calculator...", {"type": "open_app", "target": "calculator"}
            except Exception as e:
                return True, f"Failed to open Calculator: {e}", None

        # 4. Command Prompt / Terminal
        if any(cmd in text for cmd in ["open cmd", "open command prompt", "open terminal"]):
            try:
                subprocess.Popen("start cmd.exe", shell=True)
                return True, "Opening Command Prompt...", {"type": "open_app", "target": "cmd"}
            except Exception as e:
                return True, f"Failed to open Command Prompt: {e}", None

        # 5. File Explorer
        if any(cmd in text for cmd in ["open file explorer", "open explorer", "open files", "open my computer"]):
            try:
                subprocess.Popen(["explorer.exe"])
                return True, "Opening File Explorer...", {"type": "open_app", "target": "explorer"}
            except Exception as e:
                return True, f"Failed to open File Explorer: {e}", None

        # 6. Paint
        if any(cmd in text for cmd in ["open paint", "start paint", "open mspaint"]):
            try:
                subprocess.Popen(["mspaint.exe"])
                return True, "Opening Paint...", {"type": "open_app", "target": "paint"}
            except Exception as e:
                return True, f"Failed to open Paint: {e}", None

        # 7. System Settings
        if any(cmd in text for cmd in ["open settings", "system settings", "open control panel"]):
            try:
                subprocess.Popen("start ms-settings:", shell=True)
                return True, "Opening System Settings...", {"type": "open_app", "target": "settings"}
            except Exception as e:
                return True, f"Failed to open Settings: {e}", None

        # 8. VS Code
        if any(cmd in text for cmd in ["open vscode", "open vs code", "open code editor"]):
            try:
                subprocess.Popen("start code", shell=True)
                return True, "Opening Visual Studio Code...", {"type": "open_app", "target": "vscode"}
            except Exception as e:
                return True, f"Failed to open VS Code: {e}", None

        # 9. Web Search & Browser Tabs
        if any(cmd in text for cmd in ["open new tab", "open tab", "new tab"]):
            url = "https://www.google.com"
            _safe_open_url(url)
            return True, "Opening a new browser tab...", {"type": "open_url", "url": url}

        if "open youtube" in text or "start youtube" in text:
            url = "https://www.youtube.com"
            _safe_open_url(url)
            return True, "Opening YouTube...", {"type": "open_url", "url": url}

        if "open google" in text:
            url = "https://www.google.com"
            _safe_open_url(url)
            return True, "Opening Google...", {"type": "open_url", "url": url}

        if "open whatsapp" in text:
            url = "https://web.whatsapp.com"
            _safe_open_url(url)
            return True, "Opening WhatsApp Web...", {"type": "open_url", "url": url}

        if "open github" in text:
            url = "https://github.com"
            _safe_open_url(url)
            return True, "Opening GitHub...", {"type": "open_url", "url": url}

        if "open gmail" in text or "open mail" in text:
            url = "https://mail.google.com"
            _safe_open_url(url)
            return True, "Opening Gmail...", {"type": "open_url", "url": url}

        # Search on Youtube
        if "youtube" in text and ("search" in text or "play" in text or "find" in text):
            query = text.replace("search youtube for ", "").replace("search on youtube for ", "").replace("search on youtube ", "").replace("search youtube ", "").replace("play ", "").replace("on youtube", "").replace("search ", "").strip()
            url = f"https://www.youtube.com/results?search_query={query}"
            _safe_open_url(url)
            return True, f"Searching YouTube for '{query}'...", {"type": "open_url", "url": url}

        # General Google Search
        if "search" in text or text.startswith("google ") or text.startswith("find "):
            query = text.replace("search google for ", "").replace("search on google for ", "").replace("search on google ", "").replace("search google ", "").replace("google search ", "").replace("search for ", "").replace("search ", "").replace("google ", "").replace("find ", "").replace(" on google", "").strip()
            url = f"https://www.google.com/search?q={query}"
            _safe_open_url(url)
            return True, f"Searching Google for '{query}'...", {"type": "open_url", "url": url}

        # Dynamic website opening e.g., "open instagram", "open amazon.in", "open facebook"
        if text.startswith("open ") and len(text.split()) <= 3:
            target = text.replace("open ", "").strip()
            if target and target not in ["deva", "menu", "history", "chat"]:
                url = target if target.startswith("http") else "https://" + (target if "." in target else f"www.{target}.com")
                _safe_open_url(url)
                return True, f"Opening {target} in browser...", {"type": "open_url", "url": url}

        return False, "", None
