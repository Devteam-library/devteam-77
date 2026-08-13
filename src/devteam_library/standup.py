"""Генерация текстового отчёта для ежедневного стендапа (daily standup).

Идея модуля: каждый участник команды описывает свою активность через
простую структуру :class:`StandupEntry` (что сделал вчера / что делает
сегодня / что блокирует), а :func:`build_standup_report` собирает из
этих записей единый читаемый Markdown-отчёт для канала команды.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StandupEntry:
    """Запись одного участника команды для дейли-стендапа.

    Attributes:
        author: Имя участника.
        yesterday: Список пунктов "что было сделано вчера/в прошлый рабочий день".
        today: Список пунктов "что планируется сделать сегодня".
        blockers: Список блокеров. Пустой список означает, что блокеров нет.
    """

    author: str
    yesterday: list[str] = field(default_factory=list)
    today: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)

    @property
    def has_blockers(self) -> bool:
        """True, если у участника есть незакрытые блокеры."""
        return len(self.blockers) > 0


def _format_bullets(items: list[str]) -> str:
    """Форматирует список строк в Markdown-пункты с отступом.

    Если список пуст, возвращает строку-заглушку, чтобы отчёт не выглядел
    как ошибка рендеринга.
    """
    if not items:
        return "  - _нет пунктов_"
    return "\n".join(f"  - {item}" for item in items)


def build_standup_report(entries: list[StandupEntry], title: str = "Daily standup") -> str:
    """Собирает Markdown-отчёт из списка записей участников.

    Блокеры выносятся в отдельный раздел в начале отчёта, чтобы команда
    сразу видела, что требует внимания, не читая всё по порядку.

    Args:
        entries: Список записей участников за сегодня.
        title: Заголовок отчёта.

    Returns:
        Готовый Markdown-текст отчёта.

    Raises:
        ValueError: если ``entries`` пуст — пустой отчёт бессмысленен.
    """
    if not entries:
        raise ValueError("Список записей entries не может быть пустым")

    lines = [f"# {title}", ""]

    blocked_entries = [entry for entry in entries if entry.has_blockers]
    if blocked_entries:
        lines.append("## ⚠️ Блокеры")
        for entry in blocked_entries:
            lines.append(f"- **{entry.author}**:")
            lines.append(_format_bullets(entry.blockers))
        lines.append("")

    for entry in entries:
        lines.append(f"## {entry.author}")
        lines.append("**Вчера:**")
        lines.append(_format_bullets(entry.yesterday))
        lines.append("**Сегодня:**")
        lines.append(_format_bullets(entry.today))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
