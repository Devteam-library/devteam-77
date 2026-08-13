"""Тесты для devteam_library.time_utils."""

from datetime import date

import pytest

from devteam_library.time_utils import add_business_days, business_days_between, estimate_deadline


def test_add_business_days_skips_weekend():
    # Пятница 2026-08-14 + 1 рабочий день -> понедельник 2026-08-17
    friday = date(2026, 8, 14)
    assert add_business_days(friday, 1) == date(2026, 8, 17)


def test_add_business_days_skips_holiday():
    monday = date(2026, 8, 10)
    holiday = date(2026, 8, 11)  # вторник — праздник
    # +1 рабочий день от понедельника при выходном вторнике -> среда
    assert add_business_days(monday, 1, holidays=[holiday]) == date(2026, 8, 12)


def test_add_business_days_zero_returns_same_date():
    d = date(2026, 8, 10)
    assert add_business_days(d, 0) == d


def test_add_business_days_negative_raises():
    with pytest.raises(ValueError):
        add_business_days(date(2026, 8, 10), -1)


def test_business_days_between_simple_week():
    # С понедельника по следующий понедельник — 5 рабочих дней
    assert business_days_between(date(2026, 8, 10), date(2026, 8, 17)) == 5


def test_business_days_between_negative_when_end_before_start():
    assert business_days_between(date(2026, 8, 17), date(2026, 8, 10)) == -5


def test_estimate_deadline_basic():
    start = date(2026, 8, 10)  # понедельник
    # 10 стори-поинтов при скорости 5/день -> 2 рабочих дня -> среда
    assert estimate_deadline(start, story_points=10, points_per_day=5) == date(2026, 8, 12)


def test_estimate_deadline_rounds_up():
    start = date(2026, 8, 10)
    # 1 поинт при скорости 5/день -> округление вверх до 1 рабочего дня
    assert estimate_deadline(start, story_points=1, points_per_day=5) == date(2026, 8, 11)


def test_estimate_deadline_invalid_points_per_day_raises():
    with pytest.raises(ValueError):
        estimate_deadline(date(2026, 8, 10), story_points=5, points_per_day=0)
