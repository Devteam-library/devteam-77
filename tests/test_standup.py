"""Тесты для devteam_library.standup."""

import pytest

from devteam_library.standup import StandupEntry, build_standup_report


def test_has_blockers_true_when_present():
    entry = StandupEntry(author="Alice", blockers=["ждём ревью PR #42"])
    assert entry.has_blockers is True


def test_has_blockers_false_when_empty():
    entry = StandupEntry(author="Alice")
    assert entry.has_blockers is False


def test_build_standup_report_empty_raises():
    with pytest.raises(ValueError):
        build_standup_report([])


def test_build_standup_report_includes_blockers_section_first():
    entries = [
        StandupEntry(author="Alice", yesterday=["Сделал X"], today=["Сделаю Y"], blockers=["Нет доступа к БД"]),
        StandupEntry(author="Bob", yesterday=["Сделал Z"], today=["Сделаю W"]),
    ]
    report = build_standup_report(entries, title="Дейли 13 августа")

    assert report.startswith("# Дейли 13 августа")
    assert "## ⚠️ Блокеры" in report
    # Раздел блокеров должен идти раньше персональных разделов
    assert report.index("## ⚠️ Блокеры") < report.index("## Alice")
    assert "Нет доступа к БД" in report
    assert "## Bob" in report
    assert "Сделал Z" in report


def test_build_standup_report_no_blockers_section_when_none():
    entries = [StandupEntry(author="Alice", yesterday=["X"], today=["Y"])]
    report = build_standup_report(entries)
    assert "Блокеры" not in report
