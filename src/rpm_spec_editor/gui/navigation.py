class NavigationService:
    def __init__(self, model):
        self._model = model

    def _section_lines(self) -> list[int]:
        return sorted(
            s.line_no
            for s in self._model.iter_sections()
            if s.line_no is not None
        )

    def find_section_by_name(self, name: str) -> int | None:
        item = self._model.find_section_by_name(name)
        return item.line_no if item else None

    def find_section_for_line(self, line_no: int) -> int | None:
        prev = None
        for line in self._section_lines():
            if line > line_no:
                break
            prev = line
        return prev

    def _issue_lines(self) -> list[int]:
        return sorted(
            i.line_no
            for i in self._model.iter_issues()
            if i.line_no is not None
        )

    def find_next_section(self, current_line: int) -> int | None:
        for line in self._section_lines():
            if line > current_line:
                return line
        return None

    def find_prev_section(self, current_line: int) -> int | None:
        prev = None
        for line in self._section_lines():
            if line >= current_line:
                break
            prev = line
        return prev

    def find_first_section(self) -> int | None:
        lines = self._section_lines()
        return lines[0] if lines else None

    def find_last_section(self) -> int | None:
        lines = self._section_lines()
        return lines[-1] if lines else None