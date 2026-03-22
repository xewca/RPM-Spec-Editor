import re

from rpm_spec_editor.parsing.models import SpecFile, SpecSection

class SpecParser:
    HEADER_RE = re.compile(r"^(?P<key>[A-Za-z0-9_]+)\s*:\s*(?P<value>.+)$")
    SECTION_RE = re.compile(r"^%(?P<name>[a-zA-Z0-9_]+)\b")

    def parse(self, text: str) -> SpecFile:
        spec = SpecFile()
        current_section = None

        for line_no, line in enumerate(text.splitlines()):
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                if current_section:
                    current_section.lines.append(line)
                continue

            section_match = self.SECTION_RE.match(stripped)
            if section_match:
                name = section_match.group("name")
                current_section = SpecSection(
                    name=name,
                    start_line=line_no
                )
                spec.sections[name] = current_section
                spec.section_order.append(name)
                continue

            if current_section is None:
                header_match = self.HEADER_RE.match(stripped)
                if header_match:
                    spec.headers[
                        header_match.group("key")
                    ] = header_match.group("value")
                continue

            current_section.lines.append(line)

        return spec