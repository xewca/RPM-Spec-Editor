import pytest

from rpm_spec_editor.parsing.spec_parser import SpecParser
from rpm_spec_editor.domain.spec_validator import SpecValidator


@pytest.mark.integration
def test_parser_to_validator_missing_fields():
    parser = SpecParser()
    validator = SpecValidator()

    content = """
Version: 1.0
"""

    spec = parser.parse(content)
    issues = validator.validate(spec)

    assert any("Name" in i.message for i in issues)


