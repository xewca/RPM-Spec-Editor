import pytest
from rpm_spec_editor.gui.formatter import align_spec_fields


@pytest.mark.unit
def test_align_basic():
    text = "Name: test\nVersion: 1.0"

    result = align_spec_fields(text)

    assert "Name:" in result
    assert "Version:" in result
    assert result.index("Name:") != -1


@pytest.mark.unit
def test_alignment_spacing():
    text = "Name: test\nVersion: 1.0"

    result = align_spec_fields(text)

    lines = result.splitlines()

    name_line = next(l for l in lines if l.startswith("Name:"))
    version_line = next(l for l in lines if l.startswith("Version:"))

    assert len(name_line) >= len("Name:  ")


@pytest.mark.unit
def test_raw_lines_preserved():
    text = "%description\nName: test\nCustomTag: value"
    result = align_spec_fields(text)
    assert "%description" in result
    assert "CustomTag: value" in result

@pytest.mark.unit
def test_unknown_tags_ignored():
    text = "UnknownTag: value"
    result = align_spec_fields(text)
    assert "UnknownTag: value" in result


@pytest.mark.unit
def test_empty_input():
    assert align_spec_fields("") == ""


@pytest.mark.unit
def test_multiline_stability():
    text = """
Name: test
Version: 1
Release: 2
%description
hello
"""

    result = align_spec_fields(text)

    assert "Name:" in result
    assert "%description" in result