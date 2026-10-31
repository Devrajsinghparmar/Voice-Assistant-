"""
Conversational AI Assistant Module (Deva) using Groq and OpenAI LLM Models.

Supports 'clear' command to wipe conversation history memory,
system app execution (Camera, Notepad, Calc, Explorer, etc.),
browser tabs, and flags sensitive JSON Knowledge Base responses for text-only rendering.
"""

import os
from typing import List, Dict, Tuple, Optional
from config import config
from knowledge_manager import KnowledgeManager
from system_actions import SystemActionsManager


class VoiceAssistant:
    def __init__(self):
        self.provider = config.API_PROVIDER
        self.km = KnowledgeManager()
        self.system_prompt = config.get_system_prompt(self.km.get_knowledge_context())
        self.client = None
        self._current_key = None
        self._get_client()

        self.conversation_history: List[Dict[str, str]] = []
        self.reset_conversation()

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
                    print(f"[Assistant Init Warning] Could not init client: {e}")
        return self.client

    def refresh_knowledge(self):
        """Reloads knowledge_base.json data into prompt context."""
        self.km.load_knowledge()
        self.system_prompt = config.get_system_prompt(self.km.get_knowledge_context())
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            self.conversation_history[0]["content"] = self.system_prompt

    def reset_conversation(self) -> None:
        """Resets conversation history back to initial system prompt."""
        self.refresh_knowledge()
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def get_response_info(self, user_text: str) -> Tuple[str, bool, Optional[Dict[str, str]]]:
        """
        Processes user query and returns (assistant_reply, is_knowledge_base, action_dict).
        
        :return: Tuple (reply_text, is_from_json_knowledge_base, action_dict)
        """
        clean_input = user_text.strip().lower()

        # 1. Handle 'clear' command to reset history
        if clean_input in ["clear", "clear history", "clear chat", "reset", "reset memory"]:
            self.reset_conversation()
            return ("Conversation history cleared! Deva is ready for a new chat.", False, None)

        # 2. Wake phrase check
        if clean_input in ["open deva", "deva open", "hey deva", "hello deva", "deva"]:
            return ("Namaste! Main Deva hoon. Deva open ho gaya hai, bataiye main aapki kya help kar sakta hoon?", False, None)

        if not user_text.strip():
            return ("Mujhe kuch sunai nahi diya. Kripya firse boliye.", False, None)

        # 3. Check for System Actions (Camera, Notepad, Calculator, Explorer, Browser tabs/search)
        handled, action_reply, action_data = SystemActionsManager.execute_action(user_text)
        if handled:
            self.conversation_history.append({"role": "user", "content": user_text})
            self.conversation_history.append({"role": "assistant", "content": action_reply})
            return (action_reply, False, action_data)

        # 4. Check for direct match in JSON knowledge base (passwords, daily routines, etc.)
        direct_match = self.km.search_exact(clean_input)
        if direct_match:
            self.conversation_history.append({"role": "user", "content": user_text})
            self.conversation_history.append({"role": "assistant", "content": direct_match})
            return (direct_match, True, None)  # Flagged as JSON Knowledge Base -> Text ONLY (No speech)

        client = self._get_client()
        if not client:
            return (f"API key for '{self.provider.upper()}' is missing or invalid. Please add GROQ_API_KEY under Vercel Project Settings -> Environment Variables, then click Redeploy.", False, None)

        self.refresh_knowledge()
        self.conversation_history.append({"role": "user", "content": user_text})

        try:
            model_name = config.LLM_MODEL
            response = client.chat.completions.create(
                model=model_name,
                messages=self.conversation_history,
                max_tokens=300,
                temperature=0.7,
                timeout=25.0,
            )

            assistant_reply = response.choices[0].message.content.strip()
            clean_reply = self._clean_for_speech(assistant_reply)

            self.conversation_history.append({"role": "assistant", "content": assistant_reply})

            if len(self.conversation_history) > 21:
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-20:]

            is_json_related = any(k.lower() in clean_input for k in self.km.knowledge.keys())
            return (clean_reply, is_json_related, None)

        except Exception as e:
            error_msg = f"Sorry, I encountered an error communicating with {self.provider.upper()}: {str(e)}"
            print(f"[Assistant Error] {e}")
            return (error_msg, False, None)

    def get_response(self, user_text: str) -> str:
        """Helper method returning string response."""
        reply, _, _ = self.get_response_info(user_text)
        return reply

    @staticmethod
    def _clean_for_speech(text: str) -> str:
        """Removes markdown symbols for speech synthesis."""
        cleaned = text.replace("**", "").replace("__", "").replace("```", "").replace("#", "")
        return cleaned.strip()


if __name__ == "__main__":
    bot = VoiceAssistant()
    print(f"Deva Voice Assistant initialized ({config.API_PROVIDER})")
