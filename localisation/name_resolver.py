import json
import os
import sys
from typing import Dict


class NameResolver:
    def __init__(self, language_code: str = "en"):
        self.language_code: str = language_code
        self.translations: Dict[str, str] = {}
        self.load_language(language_code)

    def load_language(self, language_code: str) -> None:
        """Loads the JSON file for the specified language."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if not getattr(sys, "frozen", False) else os.path.dirname(p=sys.executable)
        file_path = os.path.join(base_dir, "resources", "locales", f"{language_code}.json")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.translations = json.load(file)
            self.language_code = language_code
        except FileNotFoundError:
            self.translations = {}

    def get(self, key: str) -> str:
        """
        Fetches the translation for a key.
        """
        return self.translations.get(key, f"[{key}]")

    def get_enum(self, enum_member) -> str:
        """
        Fetches the translation for enum member.
        """
        class_name = enum_member.__class__.__name__.lower()
        member_name = enum_member.name.lower()
        key = f"enum_{class_name}_{member_name}"
        return self.get(key)

name_resolver = NameResolver("pl")