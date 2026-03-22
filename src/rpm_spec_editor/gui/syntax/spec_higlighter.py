from PyQt5.QtGui import (
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QFont
)
from PyQt5.QtCore import QRegExp


class SpecSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a9955"))
        self.rules.append((QRegExp(r"#.*$"), comment_format))

        section_format = QTextCharFormat()
        section_format.setForeground(QColor("#569cd6"))
        section_format.setFontWeight(QFont.Bold)

        sections = [
            r"%description\b",
            r"%prep\b",
            r"%conf\b",
            r"%build\b",
            r"%install\b",
            r"%check\b",
            r"%files\b",
            r"%changelog\b"
        ]

        for section in sections:
            self.rules.append((QRegExp(section), section_format))

        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#4ec9b0"))
        header_format.setFontWeight(QFont.Bold)

        headers = [
            r"\bName:",
            r"\bSummary:",
            r"\bURL:",
            r"\bLicense:",
            r"\bEpoch:",
            r"\bVersion:",
            r"\bRelease:",
            r"\bSource:",
            r"\bVLS:",
        ]

        for header in headers:
            self.rules.append((QRegExp(header), header_format))

        macro_format = QTextCharFormat()
        macro_format.setForeground(QColor("#dcdcaa"))

        self.rules.append((QRegExp(r"%\{[^}]+\}"), macro_format))

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self.rules:
            index = pattern.indexIn(text, 0)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)