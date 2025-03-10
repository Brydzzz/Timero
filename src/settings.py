import json
from pathlib import Path
from typing import Any


class Settings:
    DEFAULT_SETTINGS = {
        "show_breaks": True,
        "auto_start_breaks": True,
        "auto_start_exercises": True,
        "break_duration": 10,
    }

    def __init__(self, config_path: str):
        self.config_file = Path(config_path)
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._load_settings()

    def _load_settings(self) -> None:
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings: {e}")

    def save_settings(self) -> None:
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.save_settings()

    def reset_to_defaults(self) -> None:
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()
