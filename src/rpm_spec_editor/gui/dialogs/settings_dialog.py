from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QDialogButtonBox,
    QFormLayout,
)

from rpm_spec_editor.core.settings_manager import SettingsManager


class SettingsDialog(QDialog):
    def __init__(self, settings: SettingsManager, parent=None):
        super().__init__(parent)

        self.settings = settings

        self.setWindowTitle("Настройки")
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        form = QFormLayout()


        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings.theme)
        form.addRow("Тема:", self.theme_combo)


        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 40)
        self.font_size_spin.setValue(self.settings.font_size)
        form.addRow("Размер шрифта:", self.font_size_spin)


        self.tab_size_spin = QSpinBox()
        self.tab_size_spin.setRange(2, 12)
        self.tab_size_spin.setValue(self.settings.tab_size)
        form.addRow("Размер табуляции:", self.tab_size_spin)


        self.word_wrap_check = QCheckBox()
        self.word_wrap_check.setChecked(self.settings.word_wrap)
        form.addRow("Перенос строк:", self.word_wrap_check)


        self.autosave_check = QCheckBox()
        self.autosave_check.setChecked(self.settings.autosave_enabled)
        form.addRow("Автосохранение:", self.autosave_check)
        self.autosave_interval_spin = QSpinBox()
        self.autosave_interval_spin.setRange(5, 600)
        self.autosave_interval_spin.setValue(self.settings.autosave_interval)
        form.addRow("Интервал автосохранения (сек):", self.autosave_interval_spin)


        self.backup_check = QCheckBox()
        self.backup_check.setChecked(self.settings.backup_enabled)
        form.addRow("Backup копии:", self.backup_check)
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setRange(1, 100)
        self.backup_count_spin.setValue(self.settings.backup_count)
        form.addRow("Количество backup:", self.backup_count_spin)


        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def apply_settings(self):
        self.settings.set("theme", self.theme_combo.currentText())

        self.settings.set("font_size", self.font_size_spin.value())

        self.settings.set("tab_size", self.tab_size_spin.value())

        self.settings.set("word_wrap", self.word_wrap_check.isChecked())

        self.settings.set("autosave_enabled", self.autosave_check.isChecked())
        self.settings.set("autosave_interval", self.autosave_interval_spin.value())

        self.settings.set("backup_enabled", self.backup_check.isChecked())
        self.settings.set("backup_count", self.backup_count_spin.value())