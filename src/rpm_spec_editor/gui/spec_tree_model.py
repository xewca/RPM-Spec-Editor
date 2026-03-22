from typing import List, Optional
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QColor, QFont, QBrush

from rpm_spec_editor.parsing.models import SpecFile
from rpm_spec_editor.domain.validation import ValidationIssue
from dataclasses import dataclass

@dataclass
class SpecSection:
    name: str
    line_no: int
    end_line: int | None = None


class TreeItem:
    def __init__(
            self,
            text: str,
            parent: "TreeItem | None" = None,
            line_no: int | None = None,
            is_issue: bool = False,
            start_line: int | None = None,
            end_line: int | None = None
    ):
        self.text = text
        self.parent = parent

        self.line_no = line_no

        self.start_line = start_line if start_line is not None else line_no
        self.end_line = end_line

        self.is_issue = is_issue
        self.children: list[TreeItem] = []
        self.issues: list[ValidationIssue] = []

        self.start_line: int | None
        self.end_line: int | None

    def add_child(self, item: "TreeItem") -> None:
        self.children.append(item)

    def child(self, row: int) -> "TreeItem | None":
        if 0 <= row < len(self.children):
            return self.children[row]

    def child_count(self) -> int:
        return len(self.children)

    def row(self) -> int:
        if self.parent:
            return self.parent.children.index(self)
        return 0

    @property
    def max_line_no(self) -> int:
        lines = [self.line_no] if self.line_no else []
        for child in self.children:
            lines.append(child.max_line_no)
        return max(lines) if lines else 1

class SpecTreeModel(QAbstractItemModel):
    def __init__(
            self,
            spec: SpecFile | None = None,
            issues: Optional[List[ValidationIssue]] = None,
            parent=None
    ):
        super().__init__(parent)

        self._root = TreeItem("Spec file")
        self._issues = issues or []

        self._active_section_line: int | None = None

        self._issues_root: TreeItem | None = None

        if spec:
            self.build_from_spec(spec)

    @property
    def root(self) -> TreeItem:
        return self._root

    def rowCount(self, parent: QModelIndex) -> int:
        item = self._get_item(parent)
        return item.child_count()

    def columnCount(self, parent: QModelIndex) -> int:
        return 1

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return None

        item: TreeItem = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.text

        if item.parent == self._issues_root:
            if role == Qt.ForegroundRole:
                if item.text.startswith("x"):
                    return QColor("#c62828")
                return QColor("#ef6c00")

            if role == Qt.FontRole:
                font = QFont()
                if item.text.startswith("x"):
                    font.setBold(True)
                return font

        if item.is_issue:
            if role == Qt.ForegroundRole:
                if item.text.startswith("x"):
                    return QColor("#c62828")
                return QColor("#ef6c00")

            if role == Qt.FontRole:
                font = QFont()
                font.setItalic(True)
                return font

        if role == Qt.BackgroundRole:
            if (
                    self._active_section_line is not None
                    and item.line_no is not None
                    and item.parent
                    and item.parent.text == "Секции"
                    and item.line_no <= self._active_section_line
            ):
                return QBrush(QColor("#e3f2fd"))

        if role == Qt.FontRole:
            if (
                    self._active_section_line is not None
                    and item.line_no is not None
                    and item.parent
                    and item.parent.text == "Секции"
                    and item.line_no <= self._active_section_line
            ):
                font = QFont()
                font.setBold(True)
                return font

        if role == Qt.ForegroundRole:
            if item.issues:
                if any(i.level.name == "ERROR" for i in item.issues):
                    return QColor("#c62828")
                return QColor("#ef6c00")

        if role == Qt.ToolTipRole and item.issues:
            return "\n".join(i.message for i in item.issues)

        return None

    def get_issues_root_index(self) -> QModelIndex | None:
        if not self._issues_root:
            return None

        return self.createIndex(
            self._issues_root.row(),
            0,
            self._issues_root
        )

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_item = self._get_item(parent)
        child_item = parent_item.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)

        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        parent_item = item.parent

        if parent_item is None or parent_item == self._root:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def build_from_spec(self, spec: SpecFile) -> None:
        self.beginResetModel()

        self._root = TreeItem("Spec File")

        headers_root = TreeItem("Метаданные", self._root)
        self._root.add_child(headers_root)

        for key, value in spec.headers.items():
            headers_root.add_child(
                TreeItem(f"{key}: {value}", headers_root)
            )

        sections_root = TreeItem("Секции", self._root)
        self._root.add_child(sections_root)


        section_items = []

        for section_name in spec.section_order:
            section = spec.sections[section_name]

            item = TreeItem(
                f"{section.name}",
                sections_root,
                line_no=section.start_line,
                start_line=section.start_line
            )

            section_items.append(item)
            sections_root.add_child(item)
        '''
        for issue in self._issues:
            prefix = "x" if issue.level.name == "ERROR" else "!"
            self._issues_root.add_child(
                TreeItem(
                    f"{prefix} {issue.message}",
                    self._issues_root,
                    line_no=issue.line_no
                )
            )
        '''

        for i, item in enumerate(section_items):
            if i + 1 < len(section_items):
                next_item = section_items[i + 1]
                item.end_line = next_item.start_line - 1
            else:
                item.end_line = spec.total_lines

        self.endResetModel()
        self._issues_root = TreeItem("Ошибки и предупреждения", self._root)
        self._root.add_child(self._issues_root)

'''
Ты знаешь на каком этапе сейчас идет разработка 
в проекте "Диплом" - чат "Проект редактора RPM".
Какие следующие этапы в этом чате?
Просмотри весь проект "Диплом", затем просмотри
и проанализируй репозиторий гитхаба:
https://github.com/devtape/RPM-Spec-Editor
'''

    def get_active_section_range(self) -> tuple[int, int] | None:
        if self._active_section_line is None:
            return None

        sections = [
            s for s in self.iter_sections()
            if s.line_no is not None
        ]

        if not sections:
            return None

        active_line = self._active_section_line

        for i, section in enumerate(sections):
            start = section.line_no

            if active_line < start:
                return None

            if i == len(sections) - 1:
                if active_line >= start:
                    return (start, self._document_last_line())
                return None

            next_start = sections[i + 1].line_no

            if start <= active_line < next_start:
                return (start, next_start - 1)

        return None

    def _document_last_line(self) -> int:
        return self._root.max_line_no

    def update_issues(self, issues: list[ValidationIssue]) -> None:
        if self._issues_root is None:
            return

        parent_index = self.createIndex(
            self._issues_root.row(),
            0,
            self._issues_root
        )

        if self._issues_root.children:
            self.beginRemoveRows(
                parent_index,
                0,
                len(self._issues_root.children) - 1
            )
            self._issues_root.children.clear()
            self.endRemoveRows()

        if issues:
            self.beginInsertRows(
                parent_index,
                0,
                len(issues) - 1
            )

            for issue in issues:
                prefix = "x" if issue.level.name == "ERROR" else "!"
                self._issues_root.add_child(
                    TreeItem(
                        f"{prefix} {issue.message}",
                        self._issues_root,
                        line_no=issue.line_no
                    )
                )

            self.endInsertRows()

        self.clear_item_issues()
        self.assign_issues_to_sections(issues)
        self.attach_issue_nodes()
        # self.layoutChanged.emit()
        self.dataChanged.emit(
            QModelIndex(),
            QModelIndex(),
            [Qt.BackgroundRole, Qt.FontRole]
        )

    def attach_issue_nodes(self):
        sections_root = None

        for child in self._root.children:
            if child.text == "Секции":
                sections_root = child
                break

        if not sections_root:
            return

        for section in sections_root.children:
            section.children = [
                c for c in section.children if not c.is_issue
            ]

            for issue in section.issues:
                prefix = "x" if issue.level.name == "ERROR" else "!"
                section.add_child(
                    TreeItem(
                        f"{prefix} {issue.message}",
                        parent=section,
                        line_no=issue.line_no,
                        is_issue=True
                    )
                )

    def rebuild(self, spec: SpecFile) -> None:
        self.beginResetModel()
        self.build_from_spec(spec)
        self.endResetModel()

    def _get_item(self, index: QModelIndex) -> TreeItem:
        if index.isValid():
            return index.internalPointer()
        return self._root

    def find_index_by_line(self, line_no: int) -> QModelIndex | None:
        """
        def walk(item: TreeItem):
            if item.line_no == line_no:
                return item

            for child in item.children:
                found = walk(child)
                if found:
                    return found
            return None

        found_item = walk(self._root)
        if not found_item:
            return None



        # return self.createIndex(found_item.row(), 0, found_item)
        return self._find_index_recursive(
            self.index(0, 0, QModelIndex()),
            line_no
        )
        """
        return self.find_section_for_line(line_no)

    def _find_index_recursive(
            self,
            parent: QModelIndex,
            line_no: int
    ) -> QModelIndex | None:
        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            item = index.internalPointer()

            if item.start_line <= line_no <= item.end_line:
                child = self._find_index_recursive(index, line_no)
                return child if child else index

        return None

    def set_active_line(self, line_no: int | None) -> None:
        self._active_section_line = line_no
        # self.layoutChanged.emit()
        self.dataChanged.emit(
            QModelIndex(),
            QModelIndex(),
            [Qt.BackgroundRole, Qt.FontRole]
        )

    def clear_item_issues(self):
        def walk(item: TreeItem):
            item.issues.clear()
            for child in item.children:
                walk(child)

        walk(self._root)

    def find_section_for_line(self, line_no: int) -> QModelIndex | None:
        sections_root = None

        for child in self._root.children:
            if child.text == "Секции":
                sections_root = child
                break

        if not sections_root:
            return None

        current_item = None

        for section in sections_root.children:
            if section.line_no is not None and section.line_no <= line_no:
                current_item = section
            else:
                break

        if not current_item:
            return None

        return self.createIndex(
            current_item.row(),
            0,
            current_item
        )

    def iter_sections(self):
        root = self.root
        for child in root.children:
            if child.text == "Секции":
                for section in child.children:
                    yield section

    def find_section_by_name(self, name: str):
        name = name.lower().lstrip('%')

        for section in self.iter_sections():
            section_name = section.text.lower().lstrip('%')
            if section_name == name:
                return section

        return None

    def get_active_section_index(self) -> QModelIndex | None:
        if self._active_section_line is None:
            return None

        index = self.find_section_for_line(self._active_line)
        if index and index.isValid():
            return index

        return None

    def iter_issues(self):
        if not self._issues_root:
            return
        for issue in self._issues_root.children:
            if issue.line_no is not None:
                yield issue

    def _is_active_section(self, item: TreeItem) -> bool:
        return (
                self._active_section_line is not None
                and item.line_no is not None
                and item.parent
                and item.parent.text == "Секции"
                and item.line_no <= self._active_section_line
        )