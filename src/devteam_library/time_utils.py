"""Расчёт рабочих дней и дедлайнов без учёта выходных и праздников.

Модуль решает частую задачу планирования: "через сколько рабочих дней
будет готова задача" или "сколько рабочих дней осталось до дедлайна".
Праздники передаются явно списком дат — библиотека не завязана на
календарь конкретной страны, чтобы одинаково работать для распределённых
команд в разных юрисдикциях.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

#: Индексы дня недели (см. datetime.date.weekday()), которые считаются
#: выходными по умолчанию: 5 = суббота, 6 = воскресенье.
DEFAULT_WEEKEND = (5, 6)


def _is_business_day(day: date, holidays: set[date], weekend: tuple[int, ...]) -> bool:
    """Внутренняя проверка: рабочий ли день с учётом выходных и праздников."""
    return day.weekday() not in weekend and day not in holidays


def add_business_days(
    start: date,
    days: int,
    holidays: Iterable[date] | None = None,
    weekend: tuple[int, ...] = DEFAULT_WEEKEND,
) -> date:
    """Добавляет к дате заданное количество рабочих дней.

    Args:
        start: Начальная дата (сама не считается добавленным днём).
        days: Сколько рабочих дней нужно добавить. Должно быть >= 0.
        holidays: Список дополнительных нерабочих дат (праздники).
        weekend: Индексы дней недели, которые считаются выходными
            (0=понедельник ... 6=воскресенье). По умолчанию сб/вс.

    Returns:
        Дата через ``days`` рабочих дней от ``start``.

    Raises:
        ValueError: если ``days`` отрицательное.
    """
    if days < 0:
        raise ValueError("days не может быть отрицательным")

    holiday_set = set(holidays or ())
    current = start
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        if _is_business_day(current, holiday_set, weekend):
            remaining -= 1
    return current


def business_days_between(
    start: date,
    end: date,
    holidays: Iterable[date] | None = None,
    weekend: tuple[int, ...] = DEFAULT_WEEKEND,
) -> int:
    """Считает количество рабочих дней между двумя датами (не включая start).

    Если ``end`` раньше ``start``, результат будет отрицательным —
    это удобно, чтобы одной функцией проверять и "сколько дней прошло",
    и "сколько дней осталось" (при разных знаках аргументов).

    Args:
        start: Начальная дата.
        end: Конечная дата.
        holidays: Дополнительные нерабочие даты.
        weekend: Индексы выходных дней недели.

    Returns:
        Целое число рабочих дней между датами.
    """
    holiday_set = set(holidays or ())
    sign = 1 if end >= start else -1
    lo, hi = (start, end) if end >= start else (end, start)

    count = 0
    current = lo
    while current < hi:
        current += timedelta(days=1)
        if _is_business_day(current, holiday_set, weekend):
            count += 1
    return sign * count


def estimate_deadline(
    start: date,
    story_points: float,
    points_per_day: float,
    holidays: Iterable[date] | None = None,
    weekend: tuple[int, ...] = DEFAULT_WEEKEND,
) -> date:
    """Оценивает дедлайн задачи по объёму работы и скорости команды.

    Простая, но практичная модель: объём работы делится на
    производительность в стори-поинтах/день, результат округляется вверх
    до целого числа рабочих дней (округление вверх — чтобы не
    недооценить срок) и добавляется к начальной дате.

    Args:
        start: Дата начала работы.
        story_points: Объём задачи в стори-поинтах.
        points_per_day: Средняя производительность команды в поинтах/день.
            Обычно берётся из :func:`devteam_library.tasks.average_velocity`,
            делённой на длину спринта в рабочих днях.
        holidays: Дополнительные нерабочие даты.
        weekend: Индексы выходных дней недели.

    Returns:
        Оценочная дата завершения задачи.

    Raises:
        ValueError: если ``story_points`` отрицательный или
            ``points_per_day`` не положительный (иначе оценка не имеет смысла).
    """
    if story_points < 0:
        raise ValueError("story_points не может быть отрицательным")
    if points_per_day <= 0:
        raise ValueError("points_per_day должен быть положительным")

    import math

    days_needed = math.ceil(story_points / points_per_day)
    return add_business_days(start, days_needed, holidays=holidays, weekend=weekend)
