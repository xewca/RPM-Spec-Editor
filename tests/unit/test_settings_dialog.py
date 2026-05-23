import pytest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QDialogButtonBox

from rpm_spec_editor.gui.dialogs.settings_dialog import SettingsDialog


@pytest.mark.unit
def test_dialog_initial_values(qtbot):
    settings = MagicMock()

    settings.theme = "Темная"
    settings.font_size = 12
    settings.tab_size = 4
    settings.word_wrap = True
    settings.autosave_enabled = True
    settings.autosave_interval = 30
    settings.backup_enabled = True
    settings.backup_count = 10

    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)

    assert dialog.theme_combo.currentText() == "Темная"
    assert dialog.font_size_spin.value() == 12
    assert dialog.tab_size_spin.value() == 4
    assert dialog.word_wrap_check.isChecked() is True


@pytest.mark.unit
def test_apply_settings_calls_set(qtbot):
    settings = MagicMock()

    settings.theme = "Темная"
    settings.font_size = 10
    settings.tab_size = 4
    settings.word_wrap = False
    settings.autosave_enabled = True
    settings.autosave_interval = 30
    settings.backup_enabled = True
    settings.backup_count = 10

    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)

    dialog.theme_combo.setCurrentText("Светлая")
    dialog.font_size_spin.setValue(14)

    dialog.apply_settings()

    settings.set.assert_any_call("theme", "Светлая")
    settings.set.assert_any_call("font_size", 14)

@pytest.mark.unit
def test_tab_and_wrap(qtbot):
    settings = MagicMock()

    settings.theme = "Темная"
    settings.font_size = 10
    settings.tab_size = 4
    settings.word_wrap = False
    settings.autosave_enabled = True
    settings.autosave_interval = 30
    settings.backup_enabled = True
    settings.backup_count = 10

    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)

    dialog.tab_size_spin.setValue(8)
    dialog.word_wrap_check.setChecked(True)

    dialog.apply_settings()

    settings.set.assert_any_call("tab_size", 8)
    settings.set.assert_any_call("word_wrap", True)


@pytest.mark.unit
def test_autosave_backup(qtbot):
    settings = MagicMock()

    settings.theme = "Темная"
    settings.font_size = 10
    settings.tab_size = 4
    settings.word_wrap = False
    settings.autosave_enabled = True
    settings.autosave_interval = 30
    settings.backup_enabled = True
    settings.backup_count = 10

    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)

    dialog.autosave_check.setChecked(False)
    dialog.backup_count_spin.setValue(50)

    dialog.apply_settings()

    settings.set.assert_any_call("autosave_enabled", False)
    settings.set.assert_any_call("backup_count", 50)


@pytest.mark.unit
def test_buttons_exist(qtbot):
    settings = MagicMock()

    settings.theme = "Темная"
    settings.font_size = 10
    settings.tab_size = 4
    settings.word_wrap = False
    settings.autosave_enabled = True
    settings.autosave_interval = 30
    settings.backup_enabled = True
    settings.backup_count = 10

    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)

    buttons = dialog.findChild(QDialogButtonBox)
    assert buttons is not None

