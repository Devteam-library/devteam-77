"""Тесты для devteam_library.checklist."""

import pytest

from devteam_library.checklist import generate_pr_checklist, DEFAULT_CHECKLIST_SECTIONS


def test_default_checklist_contains_all_sections():
    checklist = generate_pr_checklist()
    for section in DEFAULT_CHECKLIST_SECTIONS:
        assert f"### {section}" in checklist


def test_checklist_uses_github_style_checkboxes():
    checklist = generate_pr_checklist(sections={"Тесты": ["Пункт один"]})
    assert "- [ ] Пункт один" in checklist


def test_checklist_with_title():
    checklist = generate_pr_checklist(sections={"A": ["x"]}, pr_title="Мой PR")
    assert checklist.startswith("# Мой PR")


def test_checklist_empty_sections_raises():
    with pytest.raises(ValueError):
        generate_pr_checklist(sections={})


def test_checklist_section_without_items_raises():
    with pytest.raises(ValueError):
        generate_pr_checklist(sections={"Пустой раздел": []})
