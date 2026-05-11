import re
import subprocess
import tempfile
from pathlib import Path

from rpm_spec_editor.domain.validation import (
    ValidationIssue,
    ValidationLevel
)


class RPMValidator:

    ERROR_PATTERN = re.compile(
        r"line\s+(\d+):\s+(.*)",
        re.IGNORECASE
    )

    def validate(self, content):
        issues = []

        with tempfile.NamedTemporaryFile(
            suffix=".spec",
            delete=False,
            mode="w",
            encoding="utf-8"
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            result = subprocess.run(
                [
                    "rpmbuild",
                    "-bs",
                    temp_path
                ],
                capture_output=True,
                text=True
            )
            output = result.stderr

            for line in output.splitlines():
                match = self.ERROR_PATTERN.search(line)

                if not match:
                    continue

                line_no = int(match.group(1))
                message = match.group(2)

                issues.append(
                    ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message=message,
                        line_no=line_no
                    )
                )

        except FileNotFoundError:
            issues.append(
                ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="rpmbuild не найден в системе",
                    line_no=1
                )
            )

        finally:
            Path(temp_path).unlink(missing_ok=True)

        return issues