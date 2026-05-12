from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)

from pathlib import Path


class RecoveryDialog(QDialog):
    def __init__(self, backups, backup_manager, parent=None):
        super().__init__(parent)

        self.backups = backups
        self.selected_backup = None
        self.backup_manager = backup_manager

        self.setWindowTitle("Backup Recovery")
        self.resize(700, 300)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Файл",
            "Дата",
            "Размер"
        ])

        self.table.setRowCount(len(backups))
        for row, backup in enumerate(backups):
            file_name = Path(backup["original_file"]).name
            size_kb = (backup["size"] // 1024)

            self.table.setItem(row, 0, QTableWidgetItem(file_name))
            self.table.setItem(row, 1, QTableWidgetItem(backup["timestamp"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{size_kb} KB"))

        layout.addWidget(self.table)
        button_layout = QHBoxLayout()
        self.restore_button = QPushButton("Восстановить")
        self.delete_button = QPushButton("Удалить")
        self.ignore_button = QPushButton("Игнорировать")

        button_layout.addWidget(self.restore_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        button_layout.addWidget(self.ignore_button)
        layout.addLayout(button_layout)
        self.restore_button.clicked.connect(self.restore_selected)
        self.delete_button.clicked.connect(self.delete_selected)
        self.ignore_button.clicked.connect(self.reject)

    def restore_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return

        self.selected_backup = (self.backups[row])
        self.accept()


    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.backups.pop(row)
        self.table.removeRow(row)