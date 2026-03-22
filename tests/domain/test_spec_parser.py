from rpm_spec_editor.domain.spec_document import SpecParser

def test_parse_basic_spec():
    content = """
Name: test
Version: 1.0.0

%description
Test package

%prep
echo prep

%build
echo build
"""

    parser = SpecParser()
    result = parser.parse(content)

    assert "%description" in result.sections
    assert result.sections["%description"].strip() == "Test package"
    assert "%build" in result.sections