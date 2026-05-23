import pytest

from rpm_spec_editor.domain.spec_validator import SpecValidator
from rpm_spec_editor.domain.rpm_validator import RPMValidator
from rpm_spec_editor.domain.validation import ValidationLevel
from rpm_spec_editor.parsing.spec_parser import SpecParser


@pytest.fixture
def valid_spec(parser):
    content = """
Name: test
Version: 1.0
Release: 1
BuildRequires: gcc
Summary: test
License: MIT

%description
Test package

%prep
echo prep

%build
echo build

%install
echo install

%check
echo check

%files
/usr/bin/test
"""
    return parser.parse(content)


@pytest.mark.unit
def test_valid_spec(validator, valid_spec):
    issues = validator.validate(valid_spec)

    # допускаем WARNING (optional headers)
    errors = [i for i in issues if i.level == ValidationLevel.ERROR]

    assert len(errors) == 0


@pytest.mark.unit
def test_missing_required_headers(parser, validator):
    spec = parser.parse("""
Version: 1.0
""")

    issues = validator.validate(spec)

    messages = [i.message for i in issues]

    assert any("Name" in m for m in messages)
    assert any("Release" in m for m in messages)


@pytest.mark.unit
def test_missing_sections(parser, validator):
    spec = parser.parse("""
Name: test
Version: 1.0
Release: 1
""")

    issues = validator.validate(spec)

    messages = [i.message for i in issues]

    assert any("%description" in m for m in messages)
    assert any("%prep" in m for m in messages)


@pytest.mark.unit
def test_optional_headers_warning(parser, validator):
    spec = parser.parse("""
Name: test
Version: 1.0
Release: 1
""")

    issues = validator.validate(spec)

    warnings = [
        i for i in issues
        if i.level == ValidationLevel.WARNING
    ]

    assert any("Summary" in w.message for w in warnings)


@pytest.mark.unit
def test_rpmvalidator_missing_rpmbuild(monkeypatch):
    def fake_run(*args, **kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr("subprocess.run", fake_run)

    validator = RPMValidator()

    issues = validator.validate("Name: test")

    assert any("rpmbuild не найден" in i.message for i in issues)


@pytest.mark.unit
def test_rpmvalidator_error_parsing(monkeypatch):
    class FakeResult:
        stderr = "line 3: missing Name tag"

    def fake_run(*args, **kwargs):
        return FakeResult()

    monkeypatch.setattr("subprocess.run", fake_run)

    validator = RPMValidator()

    issues = validator.validate("broken")

    assert len(issues) == 1
    assert issues[0].level == ValidationLevel.ERROR
    assert "missing Name tag" in issues[0].message

@pytest.mark.unit
def test_empty_required_header(parser, validator):
    spec = parser.parse("""
Name:
Version: 1.0
Release: 1
""")

    issues = validator.validate(spec)

    assert any("Name" in i.message for i in issues)


@pytest.mark.unit
def test_duplicate_required_headers(parser, validator):
    spec = parser.parse("""
Name: first
Name: second

Version: 1.0
Release: 1

%description
test
""")

    issues = validator.validate(spec)

    assert isinstance(issues, list)


@pytest.mark.unit
def test_invalid_requires_format(parser, validator):
    spec = parser.parse("""
Name: test
Version: 1.0
Release: 1

Requires:

%description
test
""")

    issues = validator.validate(spec)

    assert isinstance(issues, list)


@pytest.mark.unit
def test_missing_files_section(parser, validator):
    spec = parser.parse("""
Name: test
Version: 1.0
Release: 1

%description
test

%prep

%build

%install
""")

    issues = validator.validate(spec)

    messages = [i.message for i in issues]

    assert any("%files" in m for m in messages)


@pytest.mark.unit
def test_validator_with_broken_macro(parser, validator):
    spec = parser.parse(r"""
%define broken %{undefined

Name: test
Version: 1.0
Release: 1

%description
test
""")

    issues = validator.validate(spec)
    assert isinstance(issues, list)