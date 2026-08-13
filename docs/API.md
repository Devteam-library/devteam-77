# API Reference

Подробное описание публичного API `devteam_library`. Все объекты ниже
также доступны напрямую из корня пакета: `from devteam_library import Task`.

## devteam_library.tasks

### `class Task`

Единица работы в спринте.

| Поле | Тип | Описание |
|---|---|---|
| `title` | `str` | Название задачи |
| `story_points` | `float` | Оценка в стори-поинтах (по умолчанию `0.0`) |
| `status` | `str` | Один из: `todo`, `in_progress`, `in_review`, `done`, `blocked` |
| `assignee` | `str \| None` | Исполнитель |
| `blocked_reason` | `str \| None` | Обязателен, если `status == "blocked"` |

Свойство `is_done: bool` — True, если `status == "done"`.

Исключения: `ValueError` при недопустимом `status`, отрицательном
`story_points` или отсутствующем `blocked_reason` для статуса `blocked`.

### `class Sprint`

Набор задач за период.

| Поле | Тип | Описание |
|---|---|---|
| `name` | `str` | Название спринта |
| `tasks` | `list[Task]` | Задачи спринта |

Методы:

- **`velocity() -> float`** — сумма `story_points` задач со `status == "done"`.
- **`planned_points() -> float`** — сумма `story_points` всех задач спринта.
- **`completion_rate() -> float`** — `velocity() / planned_points()`, `0.0` если `planned_points() == 0`.
- **`blocked_tasks() -> list[Task]`** — задачи со `status == "blocked"`.
- **`workload_by_assignee() -> dict[str, float]`** — суммарные поинты незакрытых
  задач на каждого исполнителя (ключ `"unassigned"` для задач без исполнителя),
  словарь отсортирован по убыванию нагрузки.

### `average_velocity(sprints: Iterable[Sprint]) -> float`

Средняя `velocity()` по списку спринтов. `0.0` для пустого списка.

---

## devteam_library.standup

### `class StandupEntry`

| Поле | Тип | Описание |
|---|---|---|
| `author` | `str` | Имя участника |
| `yesterday` | `list[str]` | Пункты за прошлый рабочий день |
| `today` | `list[str]` | Пункты на сегодня |
| `blockers` | `list[str]` | Блокеры (пусто = нет блокеров) |

Свойство `has_blockers: bool`.

### `build_standup_report(entries: list[StandupEntry], title: str = "Daily standup") -> str`

Собирает Markdown-отчёт. Раздел блокеров (если есть хотя бы один
`StandupEntry` с `has_blockers == True`) выводится первым, перед
персональными разделами участников.

Исключение: `ValueError`, если `entries` пуст.

---

## devteam_library.checklist

### `DEFAULT_CHECKLIST_SECTIONS: dict[str, list[str]]`

Чек-лист по умолчанию с разделами: «Код», «Тесты», «Документация»,
«Безопасность и совместимость».

### `generate_pr_checklist(sections=None, pr_title=None) -> str`

Формирует Markdown-чек-лист с чекбоксами `- [ ] пункт`.

- `sections` — свой словарь `{раздел: [пункты]}`. По умолчанию используется
  `DEFAULT_CHECKLIST_SECTIONS`.
- `pr_title` — если указан, добавляется как заголовок `# {pr_title}`.

Исключение: `ValueError`, если `sections` пуст или какой-то раздел не
содержит пунктов.

---

## devteam_library.time_utils

### `add_business_days(start, days, holidays=None, weekend=(5, 6)) -> date`

Добавляет `days` рабочих дней к `start`, пропуская выходные (`weekend`,
индексы дней недели, по умолчанию сб/вс) и даты из `holidays`.

Исключение: `ValueError`, если `days < 0`.

### `business_days_between(start, end, holidays=None, weekend=(5, 6)) -> int`

Количество рабочих дней между датами. Если `end < start`, результат
отрицательный.

### `estimate_deadline(start, story_points, points_per_day, holidays=None, weekend=(5, 6)) -> date`

Оценивает дату завершения: `ceil(story_points / points_per_day)` рабочих
дней добавляется к `start`.

Исключение: `ValueError`, если `story_points < 0` или `points_per_day <= 0`.

---

## devteam_library.git_utils

### `class ParsedCommit`

Результат разбора сообщения коммита: `type`, `scope`, `description`,
`breaking`, `raw`. `type is None`, если сообщение не в формате
Conventional Commits.

### `parse_conventional_commit(message: str) -> ParsedCommit`

Разбирает первую строку сообщения коммита по формату
`type(scope)!: description`. Не выбрасывает исключений на "неправильных"
сообщениях — возвращает `type=None` и весь текст в `description`.

### `get_git_log(repo_path=".", max_count=None) -> list[str]`

Читает сообщения коммитов через `git log`. Исключение `RuntimeError`,
если команда завершилась с ошибкой.

### `build_changelog(commit_messages: list[str], version=None) -> str`

Строит Markdown changelog, сгруппированный по типу коммита (порядок и
заголовки — см. `COMMIT_TYPE_TITLES`). Коммиты без распознанного типа
попадают в раздел «Прочее».

---

## devteam_library.cli

Консольная команда `devteam` (устанавливается автоматически через
`pip install`). Подкоманды:

- `devteam changelog [--repo PATH] [--max-count N] [--version VERSION]`
- `devteam checklist [--title TITLE]`

Программный доступ: `devteam_library.cli.main(argv=None) -> int`.
