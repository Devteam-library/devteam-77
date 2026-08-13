"""Модели задач и спринта: учёт стори-поинтов, статусов и скорости команды.

Модуль не привязан ни к одному конкретному трекеру задач (Jira, Trello,
Linear и т.п.) — это просто лёгкие структуры данных, которые удобно
заполнять из экспорта любой системы и считать по ним метрики.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

#: Допустимые статусы задачи. Список закрытый специально: он используется
#: и людьми, и другими функциями пакета (например, для построения
#: standup-отчёта), поэтому важно не допускать опечаток вроде "Done"/"DONE".
VALID_STATUSES = ("todo", "in_progress", "in_review", "done", "blocked")


@dataclass
class Task:
    """Единица работы в спринте.

    Attributes:
        title: Короткое название задачи, как оно выглядит в трекере.
        story_points: Оценка в стори-поинтах. Может быть дробной (0.5, 1, 2, 3, 5, 8...).
        status: Один из :data:`VALID_STATUSES`.
        assignee: Имя или логин исполнителя. ``None``, если задача не назначена.
        blocked_reason: Причина блокировки. Заполняется только при status="blocked".
    """

    title: str
    story_points: float = 0.0
    status: str = "todo"
    assignee: str | None = None
    blocked_reason: str | None = None

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"Некорректный статус {self.status!r}. Допустимые значения: {VALID_STATUSES}"
            )
        if self.story_points < 0:
            raise ValueError("story_points не может быть отрицательным")
        if self.status == "blocked" and not self.blocked_reason:
            raise ValueError("Для статуса 'blocked' нужно указать blocked_reason")

    @property
    def is_done(self) -> bool:
        """True, если задача полностью завершена."""
        return self.status == "done"


@dataclass
class Sprint:
    """Спринт — набор задач за фиксированный период времени.

    Attributes:
        name: Название спринта, например "Sprint 12" или "2026-W33".
        tasks: Список задач, входящих в спринт.
    """

    name: str
    tasks: list[Task] = field(default_factory=list)

    def velocity(self) -> float:
        """Сумма стори-поинтов по завершённым задачам (фактическая скорость).

        Returns:
            Суммарное количество стори-поинтов задач со статусом ``done``.
        """
        return sum(task.story_points for task in self.tasks if task.is_done)

    def planned_points(self) -> float:
        """Сумма стори-поинтов по всем задачам спринта (плановый объём)."""
        return sum(task.story_points for task in self.tasks)

    def completion_rate(self) -> float:
        """Доля выполненного объёма работы от 0.0 до 1.0.

        Если в спринте нет задач или их суммарная оценка равна нулю,
        возвращается 0.0, чтобы избежать деления на ноль.
        """
        planned = self.planned_points()
        if planned == 0:
            return 0.0
        return self.velocity() / planned

    def blocked_tasks(self) -> list[Task]:
        """Список задач со статусом ``blocked`` — то, что мешает команде."""
        return [task for task in self.tasks if task.status == "blocked"]

    def workload_by_assignee(self) -> dict[str, float]:
        """Считает суммарные стори-поинты незакрытых задач на каждого исполнителя.

        Полезно, чтобы быстро увидеть перекос нагрузки в спринте.
        Задачи без исполнителя (``assignee is None``) собираются в ключ
        ``"unassigned"``.

        Returns:
            Словарь {имя_исполнителя: сумма_поинтов}, отсортированный по
            убыванию нагрузки.
        """
        totals: dict[str, float] = {}
        for task in self.tasks:
            if task.is_done:
                continue
            key = task.assignee or "unassigned"
            totals[key] = totals.get(key, 0.0) + task.story_points
        return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def average_velocity(sprints: Iterable[Sprint]) -> float:
    """Средняя скорость команды по нескольким прошедшим спринтам.

    Используется для прогнозирования вместимости будущих спринтов —
    типичная задача при планировании (capacity planning).

    Args:
        sprints: Итерируемая коллекция уже завершённых спринтов.

    Returns:
        Средняя скорость (сумма velocity / количество спринтов).
        0.0, если список спринтов пуст.
    """
    sprints = list(sprints)
    if not sprints:
        return 0.0
    return sum(sprint.velocity() for sprint in sprints) / len(sprints)
