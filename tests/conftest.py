import pytest

from rpm_spec_editor.parsing.spec_parser import SpecParser
from rpm_spec_editor.domain.spec_validator import SpecValidator

pytestmark = pytest.mark.gui

@pytest.fixture
def parser():
    return SpecParser()


@pytest.fixture
def validator():
    return SpecValidator()

@pytest.fixture
def valid_spec_content():
    return """
Name: test-package
Version: 1.0
Release: 1
Summary: Test package
License: MIT

%description
Test description
"""


@pytest.fixture
def invalid_spec_content():
    return """
Version: 1.0

%description
Broken spec
"""

