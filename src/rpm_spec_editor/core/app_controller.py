from pathlib import Path

from rpm_spec_editor.storage.file_manager import FileManager, FileAccessError
from rpm_spec_editor.domain.spec_document import SpecDocument
from rpm_spec_editor.domain.spec_validator import SpecValidator

class AppController:
    def __init__(self):
        self.file_manager = FileManager()
        self.current_document: SpecDocument | None = None

        self.validator = SpecValidator()
        self.validation_issues = []

    def open_file(self, path: str) -> SpecDocument:
        content = self.file_manager.open_file(path)

        self.current_document = SpecDocument(Path(path), content)

        self.validation_issues = self.validator.validate(self.current_document.parsed)

        return self.current_document

    def save_current(self) -> None:
        if not self.current_document:
            raise FileAccessError("Ошибка: файл не выбран для сохранения.")

        self.file_manager.save_file(
            self.current_document.path,
            self.current_document.content
        )
        self.current_document.mark_saved()