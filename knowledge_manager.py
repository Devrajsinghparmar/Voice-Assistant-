"""
Knowledge Base Manager Module for Personal Voice Assistant (Deva).

Manages JSON storage (knowledge_base.json) for team Q&A, passwords, daily routines, and team information.
"""

import os
import json
from typing import Dict, Optional


class KnowledgeManager:
    def __init__(self, json_file: str = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if json_file is None:
            self.json_file = os.path.join(base_dir, "knowledge_base.json")
            self.example_file = os.path.join(base_dir, "knowledge_base.example.json")
        else:
            self.json_file = json_file
            self.example_file = None

        self.knowledge: Dict[str, str] = {}
        self.load_knowledge()

    def load_knowledge(self) -> Dict[str, str]:
        """Loads Q&A data from knowledge_base.json or fallback example."""
        target_file = None
        if os.path.exists(self.json_file):
            target_file = self.json_file
        elif self.example_file and os.path.exists(self.example_file):
            target_file = self.example_file

        if target_file:
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    self.knowledge = json.load(f)
            except Exception as e:
                print(f"[KnowledgeManager Error] Failed to load {target_file}: {e}")
                self.knowledge = {}
        else:
            self.knowledge = {}
        return self.knowledge

    def save_knowledge(self) -> bool:
        """Saves current Q&A dictionary to knowledge_base.json."""
        try:
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            # Handles read-only environments (such as Vercel serverless)
            print(f"[KnowledgeManager Notice] Cannot write to {self.json_file} (Read-only environment or error): {e}")
            return False

    def add_entry(self, question: str, answer: str) -> bool:
        """Adds or updates a Q&A entry in the JSON knowledge base."""
        key = question.strip().lower()
        if not key or not answer.strip():
            return False
        self.knowledge[key] = answer.strip()
        return self.save_knowledge()

    def delete_entry(self, question: str) -> bool:
        """Deletes a Q&A entry from the JSON knowledge base."""
        key = question.strip().lower()
        if key in self.knowledge:
            del self.knowledge[key]
            return self.save_knowledge()
        return False

    def search_exact(self, query: str) -> Optional[str]:
        """Searches for exact or keyword match in the JSON knowledge base."""
        q = query.strip().lower()
        # Direct match
        if q in self.knowledge:
            return self.knowledge[q]

        # Substring keyword match
        for key, ans in self.knowledge.items():
            if key in q or q in key:
                return ans
        return None

    def get_knowledge_context(self) -> str:
        """Formats the entire JSON knowledge base into a prompt context string for Deva AI."""
        if not self.knowledge:
            return ""

        context_lines = ["\n--- TEAM KNOWLEDGE BASE (JSON DATA) ---"]
        for q, a in self.knowledge.items():
            context_lines.append(f"Question/Topic: {q.title()}\nAnswer: {a}")
        context_lines.append("---------------------------------------\n")

        return "\n".join(context_lines)


if __name__ == "__main__":
    km = KnowledgeManager()
    print("Loaded Knowledge Base Entries:", len(km.knowledge))
    print(km.get_knowledge_context())
