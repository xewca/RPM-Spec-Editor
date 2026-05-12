import json
from pathlib import Path


DEFAULT_SETTINGS = {
    "theme": "dark",

    "font_family": "Monospace", # JetBrains Mono
    "font_size": 11,

    "tab_size": 4,
    "word_wrap": False,

    "autosave_enabled": True,
    "autosave_interval": 30,

    "backup_enabled": True,
    "backup_count": 10,
}


class SettingsManager:
    def __init__(self):
        self.settings_dir = Path.home() / ".rpm_spec_editor"
        self.settings_file = self.settings_dir / "settings.json"

        self.settings = DEFAULT_SETTINGS.copy()
        self.load()


    def load(self):
        self.settings_dir.mkdir(exist_ok=True)

        if not self.settings_file.exists():
            self.save()
            return

        try:
            with open(self.settings_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.settings.update(data)
        except Exception:
            self.settings = DEFAULT_SETTINGS.copy()

    def save(self):
        self.settings_dir.mkdir(exist_ok=True)
        with open(self.settings_file, "w", encoding="utf-8") as file:
            json.dump(self.settings, file, indent=4, ensure_ascii=False)



    def get(self, key, default=None):
        return self.settings.get(key, default)


    def set(self, key, value):
        self.settings[key] = value
        self.save()

    def reset(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.save()



    @property
    def theme(self):
        return self.get("theme", "dark")


    @property
    def autosave_enabled(self):
        return self.get("autosave_enabled", True)


    @property
    def autosave_interval(self):
        return self.get("autosave_interval", 30)


    @property
    def backup_enabled(self):
        return self.get("backup_enabled", True)


    @property
    def backup_count(self):
        return self.get("backup_count", 10)


    @property
    def font_family(self):
        return self.get("font_family", "JetBrains Mono")

    @property
    def font_size(self):
        return self.get("font_size", 11)

    @property
    def tab_size(self):
        return self.get("tab_size", 4)

    @property
    def word_wrap(self):
        return self.get("word_wrap", False)