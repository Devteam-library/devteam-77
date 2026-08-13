# Devteam-library

Набор небольших практичных Python-утилит для команд разработки: то, что
обычно каждая команда пишет для себя заново — учёт задач и скорости
спринта, отчёты на дейли, чек-листы для Pull Request, автогенерация
changelog из git-истории и расчёт рабочих дней/дедлайнов.

Библиотека не привязана к конкретному трекеру задач или CI — это чистые
Python-структуры и функции, которые легко встроить в свои скрипты,
Slack-боты или CI-пайплайны.

## Возможности

- **Задачи и спринты** (`devteam_library.tasks`) — модели `Task`/`Sprint`,
  расчёт velocity, процента завершения спринта, распределения нагрузки
  по исполнителям, средней скорости команды за несколько спринтов.
- **Standup-отчёты** (`devteam_library.standup`) — сборка Markdown-отчёта
  для дейли из записей участников, с блокерами в отдельном разделе.
- **Чек-лист для PR** (`devteam_library.checklist`) — генерация
  Markdown-чек-листа с чекбоксами GitHub для описания Pull Request.
- **Рабочие дни и дедлайны** (`devteam_library.time_utils`) — добавление
  рабочих дней к дате, подсчёт рабочих дней между датами, оценка
  дедлайна по объёму задачи и скорости команды — с учётом выходных и
  произвольного списка праздников.
- **Changelog из git** (`devteam_library.git_utils`) — разбор коммитов в
  формате [Conventional Commits](https://www.conventionalcommits.org/) и
  генерация Markdown changelog, сгруппированного по типу изменений.
- **CLI** (`devteam`) — команды `devteam changelog` и `devteam checklist`
  для использования из терминала без написания скриптов.

## Установка

```bash
pip install git+https://github.com/Devteam-library/devteam-77.git
```

Для локальной разработки:

```bash
git clone https://github.com/Devteam-library/devteam-77.git
cd devteam-77
pip install -e ".[dev]"
```

Требуется Python 3.10+.

## Быстрый старт

### Спринт и velocity

```python
from devteam_library import Task, Sprint

sprint = Sprint(
    name="Sprint 12",
    tasks=[
        Task(title="Fix login bug", story_points=3, status="done", assignee="Alice"),
        Task(title="Add dark theme", story_points=5, status="in_progress", assignee="Bob"),
        Task(title="Update docs", story_points=1, status="blocked", blocked_reason="ждём доступ"),
    ],
)

print(sprint.velocity())            # 3 — сумма поинтов завершённых задач
print(sprint.completion_rate())     # 0.333... — доля выполненного объёма
print(sprint.workload_by_assignee())  # {'Bob': 5} — нагрузка по незакрытым задачам
```

### Standup-отчёт

```python
from devteam_library import StandupEntry, build_standup_report

entries = [
    StandupEntry(
        author="Alice",
        yesterday=["Пофиксила баг с логином"],
        today=["Ревью PR #42"],
    ),
    StandupEntry(
        author="Bob",
        yesterday=["Начал тёмную тему"],
        today=["Продолжаю тёмную тему"],
        blockers=["Нужен доступ к дизайн-системе"],
    ),
]

print(build_standup_report(entries, title="Дейли 13 августа"))
```

### Чек-лист для PR

```python
from devteam_library import generate_pr_checklist

print(generate_pr_checklist(pr_title="Добавить тёмную тему"))
```

### Рабочие дни и дедлайны

```python
from datetime import date
from devteam_library import add_business_days, estimate_deadline

add_business_days(date(2026, 8, 14), 1)  # пропускает выходные -> понедельник

estimate_deadline(
    start=date(2026, 8, 10),
    story_points=10,
    points_per_day=5,
)  # -> дата через 2 рабочих дня
```

### Changelog из git-истории

```python
from devteam_library import get_git_log, build_changelog

commits = get_git_log(repo_path=".", max_count=50)
print(build_changelog(commits, version="1.2.0"))
```

Или прямо из терминала:

```bash
devteam changelog --repo . --version 1.2.0
devteam checklist --title "Добавить тёмную тему"
```

## Документация

Подробное описание всех публичных функций и классов — в
[docs/API.md](docs/API.md).

## Тесты

```bash
pytest
```

## Контрибьютинг

Правила и процесс описаны в [CONTRIBUTING.md](CONTRIBUTING.md).

## Лицензия

[MIT](LICENSE)
