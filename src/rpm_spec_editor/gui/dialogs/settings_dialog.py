from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QHBoxLayout
)


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)

        self.settings = settings
        self.setWindowTitle("Настройки редактора")
        self.resize(400, 250)

        self.layout = QVBoxLayout(self)
        form = QFormLayout()
        self.font_family = QComboBox()
        self.font_family.addItems([
            "JetBrains Mono",
            "Consolas",
            "Courier New",
            "Monaco"
        ])
        self.font_family.setCurrentText(self.settings.get("font_family"))

        form.addRow("Шрифт:", self.font_family)
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 40)
        self.font_size.setValue(self.settings.get("font_size"))
        form.addRow("Размер шрифта:", self.font_size)

        self.tab_size = QSpinBox()
        self.tab_size.setRange(2, 12)
        self.tab_size.setValue(self.settings.get("tab_size"))
        form.addRow("Табуляция:", self.tab_size)

        self.word_wrap = QCheckBox()
        self.word_wrap.setChecked(self.settings.get("word_wrap"))
        form.addRow("Перенос слов:", self.word_wrap)

        self.layout.addLayout(form)
        buttons_layout = QHBoxLayout()

        self.save_button = QPushButton("Сохранить")
        self.cancel_button = QPushButton("Отмена")

        buttons_layout.addStretch()

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(buttons_layout)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_settings(self):
        return {
            "font_family": self.font_family.currentText(),
            "font_size": self.font_size.value(),
            "tab_size": self.tab_size.value(),
            "word_wrap": self.word_wrap.isChecked()
        }