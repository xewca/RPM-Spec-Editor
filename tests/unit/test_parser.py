import pytest

from rpm_spec_editor.parsing.spec_parser import SpecParser
from rpm_spec_editor.parsing.models import SpecFile, SpecSection


@pytest.mark.unit
def test_parse_empty_spec():
    parser = SpecParser()
    result = parser.parse("")
    assert isinstance(result, SpecFile)
    assert result.headers == {}
    assert result.sections == {}
    assert result.section_order == []


@pytest.mark.unit
def test_parse_headers():
    parser = SpecParser()

    content = """
Name: test-package
Version: 1.0
Release: 1
License: MIT
"""
    result = parser.parse(content)
    assert result.headers["Name"] == "test-package"
    assert result.headers["Version"] == "1.0"
    assert result.headers["Release"] == "1"
    assert result.headers["License"] == "MIT"


@pytest.mark.unit
def test_parse_description_section():
    parser = SpecParser()
    content = """
Name: test

%description
This is a test package
"""
    result = parser.parse(content)
    assert "description" in result.sections
    section = result.sections["description"]
    assert isinstance(section, SpecSection)
    assert section.name == "description"
    assert "This is a test package" in section.lines[0]


@pytest.mark.unit
def test_parse_multiple_sections():
    parser = SpecParser()
    content = """
Name: test

%prep
prep content

%build
build content

%install
install content
"""
    result = parser.parse(content)
    assert "prep" in result.sections
    assert "build" in result.sections
    assert "install" in result.sections
    assert result.section_order == [
        "prep",
        "build",
        "install"
    ]


@pytest.mark.unit
def test_parse_comments():
    parser = SpecParser()
    content = """
# global comment

Name: test

%description
# inside section
Package description
"""
    result = parser.parse(content)
    assert result.headers["Name"] == "test"
    section = result.sections["description"]
    assert "# inside section" in section.lines[0]
    assert "Package description" in section.lines[1]


@pytest.mark.unit
def test_parse_dependencies():
    parser = SpecParser()

    content = """
Name: test
Requires: python3
BuildRequires: gcc
"""

    result = parser.parse(content)
    assert result.headers["Requires"] == "python3"
    assert result.headers["BuildRequires"] == "gcc"


@pytest.mark.unit
def test_parse_macros():
    parser = SpecParser()
    content = """
%define debug_package %{nil}

Name: test

%description
Macro test
"""

    result = parser.parse(content)
    assert "define" in result.sections
    section = result.sections["define"]
    assert isinstance(section.lines, list)
    assert len(section.lines) > 0
    assert any("Name: test" in line for line in section.lines)
    assert "description" in result.sections


@pytest.mark.unit
def test_parse_unicode():
    parser = SpecParser()

    content = """
Name: тест

%description
Тестовый пакет
"""

    result = parser.parse(content)
    assert result.headers["Name"] == "тест"
    assert "Тестовый пакет" in (result.sections["description"].lines[0])


@pytest.mark.unit
def test_section_start_line():
    parser = SpecParser()
    content = """
Name: test

%description
Description text
"""

    result = parser.parse(content)
    section = result.sections["description"]
    assert section.start_line >= 0


@pytest.mark.unit
def test_ignore_invalid_header():
    parser = SpecParser()
    content = """
This is invalid header

Name: valid-package
"""
    result = parser.parse(content)
    assert "Name" in result.headers
    assert result.headers["Name"] == "valid-package"


@pytest.mark.unit
def test_parse_empty_section_body():
    parser = SpecParser()

    content = """
Name: test

%description

%prep
"""

    result = parser.parse(content)

    assert "description" in result.sections
    assert result.sections["description"].lines == [] or result.sections["description"].lines == [""]


@pytest.mark.unit
def test_parse_duplicate_sections():
    parser = SpecParser()

    content = """
Name: test

%description
first

%description
second
"""

    result = parser.parse(content)

    assert "description" in result.sections
    section = result.sections["description"]

    assert isinstance(section.lines, list)


@pytest.mark.unit
def test_parse_malformed_section():
    parser = SpecParser()

    content = """
Name: test

%
broken section
"""

    result = parser.parse(content)

    assert result.headers["Name"] == "test"


@pytest.mark.unit
def test_parse_nested_macros():
    parser = SpecParser()
    content = r"""
%define major 1
%define minor %{major}.0

Name: test

%description
Nested macro test
"""

    result = parser.parse(content)
    assert "define" in result.sections
    assert len(result.sections["define"].lines) > 0


@pytest.mark.unit
def test_parse_section_without_headers():
    parser = SpecParser()

    content = """
%description
text only
"""
    result = parser.parse(content)
    assert "description" in result.sections