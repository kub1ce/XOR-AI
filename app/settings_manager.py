import json
import os
from typing import Dict, Any

class SettingsManager:
    def __init__(self, settings_file: str = "user_settings.json"):
        self.settings_file = settings_file
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from JSON file or create if not exists"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            self.settings = {}
            self._save_settings()

    def _save_settings(self) -> None:
        """Save settings to JSON file"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user settings with defaults if not set"""
        user_id = str(user_id)
        return {
            "ai_model": self.settings.get(user_id, {}).get("ai_model", "qwen"),
            "output_type": self.settings.get(user_id, {}).get("output_type", "pdf"),
            "improve_level": self.settings.get(user_id, {}).get("improve_level", 0),
            "latex_enabled": self.settings.get(user_id, {}).get("latex_enabled", False)
        }

    def update_user_settings(self, user_id: int, setting_type: str, value: str) -> bool:
        """Update specific user setting"""
        try:
            user_id = str(user_id)
            
            if user_id not in self.settings:
                self.settings[user_id] = {}

            key_map = {
                "ai": "ai_model",
                "tp": "output_type",
                "im": "improve_level",
                "lt": "latex_enabled"
            }

            if setting_type not in key_map:
                return False

            key = key_map[setting_type]

            if key == "latex_enabled":
                value = value == "yes"
            elif key == "improve_level":
                value = int(value)

            self.settings[user_id][key] = value
            self._save_settings()
            return True

        except Exception as e:
            print(f"Error updating settings: {e}")
            return False

settings_manager = SettingsManager() 