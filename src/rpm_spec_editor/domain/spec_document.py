from pathlib import Path

from rpm_spec_editor.parsing.spec_parser import SpecParser
from rpm_spec_editor.parsing.models import SpecFile

class SpecDocument:
    def __init__(self, path: Path, content: str):
        self.path = Path(path)
        self._original_content = content
        self._content = content

        self._parser = SpecParser()
        self._parsed: SpecFile | None = None

        self.parse()

    def parse(self) -> SpecFile:
        self._parsed = self._parser.parse(self._content)
        return self._parsed

    @property
    def parsed(self) -> SpecFile | None:
        return self._parsed

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value
        self.parse()

    @property
    def is_modified(self) -> bool:
        return self._content != self._original_content

    def mark_saved(self) -> None:
        self._original_content = self._content