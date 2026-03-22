from typing import List

from rpm_spec_editor.parsing.models import SpecFile
from rpm_spec_editor.domain.validation import ValidationIssue, ValidationLevel

class SpecValidator:
    REQUIRED_HEADERS = {"Name", "Version", "Release"}
    OPTIONAL_HEADERS = {"Summary", "License"}
    REQUIRED_SECTIONS = {"prep", "build", "install", "files"}

    def validate(self, spec: SpecFile) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        line_no = next(
            (s.start_line for s in spec.sections.values()),
            0
        )

        for header in self.REQUIRED_HEADERS:
            if header not in spec.headers:
                issues.append(
                    ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message=f"Отсутствует обязательный заголовок: {header}",
                        line_no=line_no
                    )
                )

        for header in self.OPTIONAL_HEADERS:
            if header not in spec.headers:
                issues.append(
                    ValidationIssue(
                        level=ValidationLevel.WARNING,
                        message=f"Рекомендуется указать заголовок: {header}",
                        line_no=line_no
                    )
                )

        existing_sections = {name.lower() for name in spec.sections.keys()}

        for section in self.REQUIRED_SECTIONS:
            if section not in existing_sections:
                issues.append(
                    ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message=f"Отсутствует обязательная секция: %{section}",
                        line_no=line_no
                    )
                )

        return issues