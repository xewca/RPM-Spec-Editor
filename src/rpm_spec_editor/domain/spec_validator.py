from typing import List

from rpm_spec_editor.parsing.models import SpecFile
from rpm_spec_editor.domain.validation import ValidationIssue, ValidationLevel

class SpecValidator:
    REQUIRED_HEADERS = {
        "Name",
        "Version",
        "Release",
        "BuildRequires"
    }
    OPTIONAL_HEADERS = {
        "Summary",
        "License"
    }
    REQUIRED_SECTIONS = {
        "description",
        "prep",
        "build",
        "install",
        "check",
        "files"
    }
    SECTION_ORDER = {
        "description": None,
        "prep": "description",
        "build": "prep",
        "install": "build",
        "check": "install",
        "files": "check"
    }

    def validate(self, spec: SpecFile) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        for header in self.REQUIRED_HEADERS:
            if header not in spec.headers:
                issues.append(
                    ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message=f"Отсутствует обязательный заголовок: {header}",
                        line_no=1
                    )
                )

        for header in self.OPTIONAL_HEADERS:
            if header not in spec.headers:
                issues.append(
                    ValidationIssue(
                        level=ValidationLevel.WARNING,
                        message=f"Рекомендуется указать заголовок: {header}",
                        line_no=1
                    )
                )

        existing_sections = {
            name.lower().strip(): section
            for name, section in spec.sections.items()
        }

        for section in self.REQUIRED_SECTIONS:
            if section in existing_sections:
                continue

            line_no = 1
            #previous = self.SECTION_ORDER.get(section)
            #if previous and previous in existing_sections:
            #    line_no = (existing_sections[previous].start_line + 1)
            #else:
            #    line_no = len(spec.headers) + 1

            issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=(f"Отсутствует обязательная "
                             f"секция: %{section}"),
                    line_no=line_no
                )
            )

        return issues