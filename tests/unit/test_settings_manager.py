import json, pytest

from rpm_spec_editor.core.settings_manager import (
    SettingsManager,
    DEFAULT_SETTINGS,
)

@pytest.mark.unit
def test_settings_manager_initialization_creates_default(tmp_path, monkeypatch):
    # перенаправляем HOME, чтобы не трогать реальную систему
    monkeypatch.setenv("HOME", str(tmp_path))

    sm = SettingsManager()

    assert sm.settings["theme"] == DEFAULT_SETTINGS["theme"]

    assert sm.settings_dir.exists()
    assert sm.settings_file.exists()

@pytest.mark.unit
def test_save_writes_valid_json(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    sm = SettingsManager()
    sm.set("theme", "Светлая")

    with open(sm.settings_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["theme"] == "Светлая"


@pytest.mark.unit
def test_load_existing_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    sm = SettingsManager()
    sm.set("font_size", 20)

    sm2 = SettingsManager()

    assert sm2.get("font_size") == 20

@pytest.mark.unit
def test_load_creates_file_if_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    sm = SettingsManager()

    assert sm.settings_file.exists()


@pytest.mark.unit
def test_load_corrupted_json_falls_back_to_default(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    sm = SettingsManager()

    # ломаем файл
    sm.settings_file.write_text("{ broken json")
    sm2 = SettingsManager()
    assert sm2.get("theme") == DEFAULT_SETTINGS["theme"]


@pytest.mark.unit
def test_set_updates_and_persists(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    sm = SettingsManager()
    sm.set("tab_size", 8)

    sm2 = SettingsManager()

    assert sm2.get("tab_size") == 8


@pytest.mark.unit
def test_reset_restores_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    sm = SettingsManager()
    sm.set("theme", "Светлая")

    sm.reset()

    assert sm.theme == DEFAULT_SETTINGS["theme"]


@pytest.mark.unit
def test_get_with_default(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    sm = SettingsManager()

    assert sm.get("nonexistent", 123) == 123


@pytest.mark.unit
def test_properties(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    sm = SettingsManager()

    assert sm.theme == DEFAULT_SETTINGS["theme"]
    assert sm.autosave_enabled is True
    assert sm.autosave_interval == 30
    assert sm.backup_enabled is True
    assert sm.backup_count == 10
    assert sm.font_family == "Monospace"
    assert sm.font_size == 11
    assert sm.tab_size == 4
    assert sm.word_wrap is False

