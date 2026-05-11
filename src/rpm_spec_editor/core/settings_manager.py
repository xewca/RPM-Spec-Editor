import json
from email.policy import default
from pathlib import Path


DEFAULT_SETTINGS = {
    "theme": "dark",
    "font_family": "JetBrains Mono",
    "font_size": 11,
    "tab_size": 4,
    "word_wrap": False,
}


class SettingsManager:
    def __init__(self):
        self.settings_dir = (
            Path.home()
            / ".rpm_spec_editor"
        )
        self.settings_file = (
            self.settings_dir
            / "settings.json"
        )
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()


    def load(self):
        self.settings_dir.mkdir(
            exist_ok=True
        )
        if not self.settings_file.exists():
            self.save()
            return

        try:
            with open(
                self.settings_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)
                self.settings.update(data)

        except Exception:
            self.settings = (DEFAULT_SETTINGS.copy())

    def save(self):
        self.settings_dir.mkdir(exist_ok=True)

        with open(
            self.settings_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.settings,
                file,
                indent=4
            )


    def get(self, key, default=None):
        #DEFAULT_SETTINGS.get(key)
        return self.settings.get(key, default)


    def set(self, key, value):
        self.settings[key] = value
        self.save()