import pytest
from rpm_spec_editor.gui.navigation import NavigationService

class Section:
    def __init__(self, line_no):
        self.line_no = line_no


class Issue:
    def __init__(self, line_no):
        self.line_no = line_no


class FakeModel:
    def __init__(self):
        self.sections = []
        self.issues = []

    def iter_sections(self):
        return self.sections

    def iter_issues(self):
        return self.issues

    def find_section_by_name(self, name):
        return self.sections[0] if self.sections else None

@pytest.mark.unit
def test_section_lines():
    model = FakeModel()
    model.sections = [Section(30), Section(10), Section(20)]

    nav = NavigationService(model)

    assert nav._section_lines() == [10, 20, 30]

@pytest.mark.unit
def test_find_section_for_line():
    model = FakeModel()
    model.sections = [Section(10), Section(20), Section(40)]

    nav = NavigationService(model)

    assert nav.find_section_for_line(25) == 20
    assert nav.find_section_for_line(5) is None

@pytest.mark.unit
def test_find_next_section():
    model = FakeModel()
    model.sections = [Section(10), Section(20), Section(40)]

    nav = NavigationService(model)

    assert nav.find_next_section(15) == 20
    assert nav.find_next_section(40) is None

@pytest.mark.unit
def test_find_prev_section():
    model = FakeModel()
    model.sections = [Section(10), Section(20), Section(40)]

    nav = NavigationService(model)

    assert nav.find_prev_section(25) == 20
    assert nav.find_prev_section(10) is None

@pytest.mark.unit
def test_first_last_section():
    model = FakeModel()
    model.sections = [Section(50), Section(10), Section(30)]

    nav = NavigationService(model)

    assert nav.find_first_section() == 10
    assert nav.find_last_section() == 50

@pytest.mark.unit
def test_empty_model():
    model = FakeModel()
    nav = NavigationService(model)

    assert nav.find_first_section() is None
    assert nav.find_last_section() is None

