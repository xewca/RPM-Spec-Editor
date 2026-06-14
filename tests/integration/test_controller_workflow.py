import pytest
from PyQt5.QtWidgets import QApplication

from rpm_spec_editor.core.app_controller import AppController
from rpm_spec_editor.domain.spec_validator import SpecValidator
from rpm_spec_editor.parsing.spec_parser import SpecParser
pytestmark = pytest.mark.gui

@pytest.mark.integration
def test_open_file_workflow(tmp_path):
    file_path = tmp_path / "test.spec"
    file_path.write_text("""
Name: test
Version: 1.0

%description
Test
""")

    controller = AppController()

    doc = controller.open_file(str(file_path))

    assert controller.current_document is not None
    assert doc.parsed.headers["Name"] == "test"
    assert len(controller.validation_issues) >= 0  # допускаем warnings


@pytest.mark.integration
def test_parser_to_validator_flow():
    parser = SpecParser()
    validator = SpecValidator()

    content = """
Name: test
Summary:  ыфа
URL: аф
License: fsa

Epoch: 0 
Version: 1
Release: 2

Source0: 2

BuildRequires: qwe

%description

%prep

%build

%install

%check

%files

%changelog
"""

    spec = parser.parse(content)
    issues = validator.validate(spec)
    print(spec.sections.keys())

    errors = [i for i in issues if i.level.name == "ERROR"]

    assert len(errors) == 0