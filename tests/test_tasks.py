"""Тесты для devteam_library.tasks."""

import pytest

from devteam_library.tasks import Task, Sprint, average_velocity


def test_task_is_done():
    done_task = Task(title="A", status="done")
    todo_task = Task(title="B", status="todo")
    assert done_task.is_done is True
    assert todo_task.is_done is False


def test_task_invalid_status_raises():
    with pytest.raises(ValueError):
        Task(title="A", status="Done")  # неверный регистр — не входит в VALID_STATUSES


def test_task_negative_points_raises():
    with pytest.raises(ValueError):
        Task(title="A", story_points=-1)


def test_task_blocked_requires_reason():
    with pytest.raises(ValueError):
        Task(title="A", status="blocked")  # без blocked_reason

    # с указанной причиной всё ок
    task = Task(title="A", status="blocked", blocked_reason="ждём доступ к БД")
    assert task.blocked_reason == "ждём доступ к БД"


def test_sprint_velocity_counts_only_done():
    sprint = Sprint(
        name="Sprint 1",
        tasks=[
            Task(title="A", story_points=3, status="done"),
            Task(title="B", story_points=5, status="in_progress"),
            Task(title="C", story_points=2, status="done"),
        ],
    )
    assert sprint.velocity() == 5


def test_sprint_planned_points_counts_everything():
    sprint = Sprint(
        name="Sprint 1",
        tasks=[
            Task(title="A", story_points=3, status="done"),
            Task(title="B", story_points=5, status="todo"),
        ],
    )
    assert sprint.planned_points() == 8


def test_sprint_completion_rate():
    sprint = Sprint(
        name="Sprint 1",
        tasks=[
            Task(title="A", story_points=4, status="done"),
            Task(title="B", story_points=4, status="todo"),
        ],
    )
    assert sprint.completion_rate() == 0.5


def test_sprint_completion_rate_empty_is_zero():
    assert Sprint(name="Empty").completion_rate() == 0.0


def test_sprint_blocked_tasks():
    blocked = Task(title="A", status="blocked", blocked_reason="нет доступа")
    ok = Task(title="B", status="in_progress")
    sprint = Sprint(name="Sprint 1", tasks=[blocked, ok])
    assert sprint.blocked_tasks() == [blocked]


def test_sprint_workload_by_assignee_excludes_done_and_sorts_desc():
    sprint = Sprint(
        name="Sprint 1",
        tasks=[
            Task(title="A", story_points=2, status="in_progress", assignee="Alice"),
            Task(title="B", story_points=5, status="todo", assignee="Bob"),
            Task(title="C", story_points=100, status="done", assignee="Alice"),
            Task(title="D", story_points=1, status="todo", assignee=None),
        ],
    )
    workload = sprint.workload_by_assignee()
    assert list(workload.items()) == [("Bob", 5), ("Alice", 2), ("unassigned", 1)]


def test_average_velocity_of_multiple_sprints():
    s1 = Sprint(name="S1", tasks=[Task(title="A", story_points=4, status="done")])
    s2 = Sprint(name="S2", tasks=[Task(title="B", story_points=6, status="done")])
    assert average_velocity([s1, s2]) == 5.0


def test_average_velocity_empty_list_is_zero():
    assert average_velocity([]) == 0.0
