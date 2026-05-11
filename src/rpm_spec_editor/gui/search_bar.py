from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel
)
from PyQt5.QtCore import pyqtSignal

class SearchBar(QWidget):
    searchRequested = pyqtSignal(str)
    nextRequested = pyqtSignal()
    previousRequested = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)

        layout = QHBoxLayout(self)
        self.label = QLabel("Поиск:")
        self.search_input = QLineEdit()
        self.next_button = QPushButton("↓")
        self.prev_button = QPushButton("↑")
        self.close_button = QPushButton("x")

        layout.addWidget(self.label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.next_button)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.close_button)

        self.search_input.textChanged.connect(self.searchRequested.emit)
        self.next_button.clicked.connect(self.nextRequested.emit)
        self.prev_button.clicked.connect(self.previousRequested.emit)
        self.close_button.clicked.connect(self._close)


    def _close(self):
        self.setVisible(False)
        self.closed.emit()

    def open(self):
        self.setVisible(True)
        self.search_input.setFocus()
        self.search_input.selectAll()

    def text(self):
        return self.search_input.text()