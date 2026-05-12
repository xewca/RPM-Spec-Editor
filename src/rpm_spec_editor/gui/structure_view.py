from PyQt5.QtWidgets import QTreeView, QMenu
from PyQt5.QtCore import pyqtSignal, QModelIndex, QItemSelectionModel, Qt, QPoint


class StructureView(QTreeView):
    jumpRequested = pyqtSignal(int)
    #collapseRequested = pyqtSignal(QModelIndex)
    #expandRequested = pyqtSignal(QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._commands = None

        self.setRootIsDecorated(False)
        self.setItemsExpandable(False)
        self.setUniformRowHeights(True)
        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)

        self.doubleClicked.connect(self._on_item_activated)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def set_commands(self, commands):
        self._commands = commands

    def _on_item_activated(self, index: QModelIndex):
        item = index.internalPointer()
        if item and item.line_no is not None:
            self.jumpRequested.emit(item.line_no)

    def _show_context_menu(self, pos: QPoint):
        index = self.indexAt(pos)
        if not index.isValid():
            return

        item = index.internalPointer()
        menu = QMenu(self)

        self._populate_menu(menu, item, index)

        if not menu.isEmpty():
            menu.exec_(self.viewport().mapToGlobal(pos))

    def _populate_menu(self, menu: QMenu, item, index):
        if item.is_issue:
            jump = menu.addAction("Перейти к ...")
            jump.triggered.connect(lambda: self.jumpRequested.emit(item.line_no))
            return

        if item.line_no is not None:
            jump = menu.addAction("Перейти к секции")
            jump.triggered.connect(lambda: self.jumpRequested.emit(item.line_no))
            select = menu.addAction("Выделить секцию")

            if self._commands:
                select.triggered.connect(lambda: self._commands.select_current_section())