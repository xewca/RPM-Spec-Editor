from pathlib import Path

from rpm_spec_editor.domain.spec_document import SpecDocument

def test_spec_document_parsed_on_create():
    content = """
Name: test-pkg
Version: 1.0.1

%description
Test package
"""

    doc = SpecDocument(Path("test.spec"), content)

    assert doc.parsed_spec is not None
    assert "description" in doc.parsed_spec.sections