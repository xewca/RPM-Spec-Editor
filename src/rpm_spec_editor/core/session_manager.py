import json
from pathlib import Path


class SessionManager:
    def __init__(self):
        self.session_dir = (Path.home() / ".rpm_spec_editor")
        self.session_file = (self.session_dir / "session.json")

    def save_session(self, data):
        self.session_dir.mkdir(exist_ok=True)
        with open(self.session_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


    def load_session(self):
        if not self.session_file.exists():
            return None

        try:
            with open(self.session_file,"r",encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return None