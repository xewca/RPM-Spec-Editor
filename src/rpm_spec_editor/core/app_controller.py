from pathlib import Path

from rpm_spec_editor.storage.file_manager import FileManager, FileAccessError
from rpm_spec_editor.domain.spec_document import SpecDocument
from rpm_spec_editor.domain.spec_validator import SpecValidator
from rpm_spec_editor.domain.rpm_validator import RPMValidator
from rpm_spec_editor.domain.rpm_builder import RPMBuilder
from rpm_spec_editor.core.backup_manager import BackupManager

class AppController:
    def __init__(self):
        self.file_manager = FileManager()
        self.current_document: SpecDocument | None = None

        self.validator = SpecValidator()
        self.builder = RPMBuilder()

        backup_dir = (Path.home() / ".rpm_spec_editor" / "backups")
        self.backup_manager = BackupManager(backup_dir=backup_dir, max_backups=10)

        self.validation_issues = []
        self.rpm_validator = RPMValidator()

    def open_file(self, path: str) -> SpecDocument:
        content = self.file_manager.open_file(path)
        self.current_document = SpecDocument(Path(path), content)
        #self.validation_issues = self.validator.validate(self.current_document.parsed)
        base_issues = self.validator.validate(self.current_document.parsed)
        rpm_issues = self.rpm_validator.validate(self.current_document.content)
        self.validation_issues = (base_issues + rpm_issues)
        return self.current_document

    def save_current(self) -> None:
        if not self.current_document:
            raise FileAccessError("Ошибка: файл не выбран для сохранения.")

        if (self.settings and self.settings.backup_enabled):
            self.backup_manager.create_backup(self.current_document.path, self.current_document.content)

        self.file_manager.save_file(self.current_document.path, self.current_document.content)
        self.current_document.mark_saved()

    def build_current(self):
        if not self.current_document:
            raise FileAccessError("Файл не открыт")

        return self.builder.build(self.current_document.path)