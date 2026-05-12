import json
import hashlib
from pathlib import Path
from datetime import datetime


class BackupManager:
    def __init__(self, backup_dir, max_backups=10):
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, file_path, content):
        folder = self._backup_folder(file_path)
        folder.mkdir(exist_ok=True)

        content_file = folder / "content.spec"
        metadata_file = folder / "metadata.json"

        with open(content_file, "w", encoding="utf-8") as file:
            file.write(content)

        metadata = {
            "original_file": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "size": len(content)
        }

        with open(metadata_file, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)

    def _cleanup_old_backups(self, stem):
        backups = sorted(self.backup_dir.glob(f"{stem}_*.spec.bak"), key=lambda p: p.stat().st_mtime, reverse=True)

        for backup in backups[self.max_backups:]:
            try:
                backup.unlink()
            except Exception:
                pass

    def find_backups(self):
        backups = []

        for folder in self.backup_dir.iterdir():
            if not folder.is_dir():
                continue

            metadata_file = folder / "metadata.json"
            content_file = folder / "content.spec"

            if not metadata_file.exists():
                continue
            if not content_file.exists():
                continue

            try:
                with open(metadata_file, "r", encoding="utf-8") as file:
                    metadata = json.load(file)
                metadata["folder"] = folder
                metadata["content_file"] = content_file
                backups.append(metadata)
            except Exception:
                continue

        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)

    def read_backup(self, backup):
        with open(backup["content_file"], "r", encoding="utf-8") as file:
            return file.read()

    def remove_backup(self, backup):
        folder = backup["folder"]
        for child in folder.iterdir():
            child.unlink()
        folder.rmdir()

    def _file_id(self, file_path):
        return hashlib.md5(str(file_path).encode()).hexdigest()

    def _backup_folder(self, file_path):
        return (self.backup_dir / self._file_id(file_path))

