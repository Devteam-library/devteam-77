"""devteam_library — набор утилит для команд разработки.

Пакет собирает небольшие, но практичные инструменты, которые обычно
приходится писать заново в каждой команде: расчёт скорости спринта,
генерация отчёта на дейли (standup), автогенерация changelog из
git-истории, чек-листы для код-ревью и расчёт рабочих дней.

Пример быстрого использования:

    >>> from devteam_library import Task, Sprint
    >>> sprint = Sprint(name="Sprint 12", tasks=[
    ...     Task(title="Fix login bug", story_points=3, status="done", assignee="Alice"),
    ...     Task(title="Add dark theme", story_points=5, status="in_progress", assignee="Bob"),
    ... ])
    >>> sprint.velocity()
    3

Все публичные объекты пакета также доступны напрямую из
``devteam_library``, чтобы не импортировать каждый модуль отдельно.
"""

from devteam_library.tasks import Task, Sprint
from devteam_library.standup import StandupEntry, build_standup_report
from devteam_library.checklist import generate_pr_checklist, DEFAULT_CHECKLIST_SECTIONS
from devteam_library.time_utils import add_business_days, business_days_between, estimate_deadline
from devteam_library.git_utils import parse_conventional_commit, build_changelog, get_git_log

__version__ = "0.1.0"

__all__ = [
    "Task",
    "Sprint",
    "StandupEntry",
    "build_standup_report",
    "generate_pr_checklist",
    "DEFAULT_CHECKLIST_SECTIONS",
    "add_business_days",
    "business_days_between",
    "estimate_deadline",
    "parse_conventional_commit",
    "build_changelog",
    "get_git_log",
    "__version__",
]
