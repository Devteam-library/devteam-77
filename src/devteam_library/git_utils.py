"""Хелперы для работы с git: чтение истории коммитов и генерация changelog.

Модуль умеет разбирать сообщения коммитов в формате
`Conventional Commits <https://www.conventionalcommits.org/>`_
(``feat: ...``, ``fix: ...``, ``docs: ...`` и т.д.) и на основе истории
git строить changelog, сгруппированный по типу изменений — то, что
обычно вручную собирают перед релизом.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

#: Порядок типов коммитов в итоговом changelog и человекочитаемые заголовки.
#: Типы, не входящие в этот словарь, попадают в раздел "Прочее".
COMMIT_TYPE_TITLES: dict[str, str] = {
    "feat": "✨ Новые возможности",
    "fix": "🐛 Исправления",
    "docs": "📝 Документация",
    "refactor": "♻️ Рефакторинг",
    "perf": "⚡ Производительность",
    "test": "✅ Тесты",
    "chore": "🔧 Прочие изменения",
}

_CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(?P<type>[a-zA-Z]+)(\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<description>.+)$"
)


@dataclass
class ParsedCommit:
    """Результат разбора одного сообщения коммита.

    Attributes:
        type: Тип коммита (``feat``, ``fix``, ...) в нижнем регистре,
            либо ``None``, если сообщение не соответствует формату
            Conventional Commits.
        scope: Необязательная область изменений из скобок, например
            ``auth`` в ``fix(auth): ...``.
        description: Текст описания после ``:``.
        breaking: True, если после типа/скоупа стоит ``!`` — признак
            breaking change.
        raw: Исходное, неизменённое сообщение коммита.
    """

    type: str | None
    scope: str | None
    description: str
    breaking: bool
    raw: str


def parse_conventional_commit(message: str) -> ParsedCommit:
    """Разбирает первую строку сообщения коммита по формату Conventional Commits.

    Если сообщение не соответствует формату (например, обычное
    "fix bug in login"), функция не выбрасывает исключение — вместо
    этого возвращает :class:`ParsedCommit` с ``type=None`` и полным
    текстом в ``description``. Это осознанное решение: история реальных
    репозиториев почти никогда не бывает идеально причёсанной, и
    падать на первом "неправильном" коммите было бы непрактично.

    Args:
        message: Полное или однострочное сообщение коммита.

    Returns:
        Разобранная структура :class:`ParsedCommit`.
    """
    first_line = message.strip().splitlines()[0] if message.strip() else ""
    match = _CONVENTIONAL_COMMIT_RE.match(first_line)
    if not match:
        return ParsedCommit(type=None, scope=None, description=first_line, breaking=False, raw=message)

    return ParsedCommit(
        type=match.group("type").lower(),
        scope=match.group("scope"),
        description=match.group("description").strip(),
        breaking=match.group("breaking") == "!",
        raw=message,
    )


def get_git_log(repo_path: str = ".", max_count: int | None = None) -> list[str]:
    """Читает сообщения коммитов git-репозитория через ``git log``.

    Args:
        repo_path: Путь к git-репозиторию (директория с ``.git``).
        max_count: Ограничение на количество последних коммитов.
            ``None`` — без ограничения (вся история).

    Returns:
        Список полных сообщений коммитов, от новых к старым.

    Raises:
        RuntimeError: если команда ``git log`` завершилась с ошибкой
            (например, ``repo_path`` не является git-репозиторием).
    """
    # %B — полное сообщение коммита. Между коммитами используем
    # редкий разделитель, чтобы не спутать его с текстом сообщений.
    separator = "\x1e"
    args = ["git", "log", f"--pretty=format:%B{separator}"]
    if max_count is not None:
        args.insert(2, f"-n{max_count}")

    result = subprocess.run(args, cwd=repo_path, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git log завершился с ошибкой: {result.stderr.strip()}")

    messages = [chunk.strip() for chunk in result.stdout.split(separator)]
    return [message for message in messages if message]


def build_changelog(commit_messages: list[str], version: str | None = None) -> str:
    """Строит Markdown changelog, сгруппированный по типу коммита.

    Коммиты, не соответствующие формату Conventional Commits, и коммиты
    с типами вне :data:`COMMIT_TYPE_TITLES` (кроме известных), попадают
    в раздел "Прочее" в конце.

    Args:
        commit_messages: Список сообщений коммитов, например результат
            :func:`get_git_log`.
        version: Необязательный номер версии/дата релиза для заголовка.

    Returns:
        Готовый Markdown-текст changelog.
    """
    grouped: dict[str, list[ParsedCommit]] = {}
    other: list[ParsedCommit] = []

    for message in commit_messages:
        parsed = parse_conventional_commit(message)
        if parsed.type in COMMIT_TYPE_TITLES:
            grouped.setdefault(parsed.type, []).append(parsed)
        else:
            other.append(parsed)

    lines = [f"# Changelog{f' — {version}' if version else ''}", ""]

    for commit_type, title in COMMIT_TYPE_TITLES.items():
        commits = grouped.get(commit_type)
        if not commits:
            continue
        lines.append(f"## {title}")
        for commit in commits:
            scope_prefix = f"**{commit.scope}**: " if commit.scope else ""
            breaking_marker = " ⚠️ BREAKING CHANGE" if commit.breaking else ""
            lines.append(f"- {scope_prefix}{commit.description}{breaking_marker}")
        lines.append("")

    if other:
        lines.append("## Прочее")
        for commit in other:
            lines.append(f"- {commit.description}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
