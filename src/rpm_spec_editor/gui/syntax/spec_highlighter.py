from PyQt5.QtGui import (
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QFont
)
from PyQt5.QtCore import QRegularExpression


class SpecSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.colors = {}

        self.rules = []
        self._build_rules()

    def apply_theme(self, colors):
        self.colors = colors
        self._build_rules()

    def _build_rules(self):
        self.rules = []

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.colors.get("syntax_comment", "#6b8e6b")))
        self.rules.append((QRegularExpression(r"#.*$"), comment_format))


        section_format = QTextCharFormat()
        section_format.setForeground(QColor(self.colors.get("syntax_section", "#0057b7")))
        section_format.setFontWeight(QFont.Bold)

        sections = [
            r"%description\b",
            r"%prep\b",
            r"%conf\b",
            r"%build\b",
            r"%install\b",
            r"%check\b",
            r"%files\b",
            r"%changelog\b",
            r"%pre\b",
            r"%post\b",
            r"%postun\b",
            r"%preun\b",
        ]

        for pattern in sections:
            self.rules.append((QRegularExpression(pattern), section_format))


        header_format = QTextCharFormat()
        header_format.setForeground(QColor(self.colors.get("syntax_header", "#cc5500")))
        header_format.setFontWeight(QFont.Bold)

        headers = [
            r"\bName:",
            r"\bSummary:",
            r"\bSummary\(ru\):",
            r"\bURL:",
            r"\bLicense:",
            r"\bEpoch:",
            r"\bVersion:",
            r"\bRelease:",
            r"\bSource\d*:",
            r"\bPatch\d*:",
            r"\bBuildRequires:",
            r"\bRequires:",
            r"\bSuggests:",
            r"\bObsoletes:",
            r"\bVLS:",
        ]

        for pattern in headers:
            self.rules.append((QRegularExpression(pattern), header_format))

        macro_format = QTextCharFormat()
        macro_format.setForeground(QColor(self.colors.get("syntax_macro", "#8000ff")))

        self.rules.append((QRegularExpression(r"%\{[^}]+\}"), macro_format))
        self.rules.append((QRegularExpression(r"%define\s+\w+"), macro_format))
        self.rules.append((QRegularExpression(r"%global\s+\w+"), macro_format))

        conditional_format = QTextCharFormat()
        conditional_format.setForeground(QColor(self.colors.get("syntax_conditional", "#cc5500")))
        conditional_format.setFontWeight(QFont.Bold)

        conditionals = [
            r"%if\b",
            r"%else\b",
            r"%endif\b",
            r"%ifarch\b",
            r"%ifnarch\b",
        ]

        for pattern in conditionals:
            self.rules.append((QRegularExpression(pattern), conditional_format))

    def highlightBlock(self, text):
        for pattern, text_format in self.rules:
            match_iterator = pattern.globalMatch(text)

            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, text_format)
