"""Генератор чек-листов для код-ревью и Pull Request'ов.

Цель модуля — избавить команду от копирования одного и того же шаблона
чек-листа между PR вручную. Набор разделов настраивается: можно
использовать значения по умолчанию (:data:`DEFAULT_CHECKLIST_SECTIONS`)
или передать свой словарь для нестандартных процессов (например,
для команды, где обязателен раздел "Security review").
"""

from __future__ import annotations

#: Чек-лист по умолчанию: {название_раздела: [пункты]}.
#: Порядок разделов и пунктов внутри сохраняется (Python dict начиная с 3.7
#: гарантирует порядок вставки), поэтому итоговый Markdown воспроизводим.
DEFAULT_CHECKLIST_SECTIONS: dict[str, list[str]] = {
    "Код": [
        "Код соответствует code style проекта (линтер проходит без ошибок)",
        "Нет закомментированного или мёртвого кода",
        "Нет отладочных print/console.log",
        "Обработаны ожидаемые ошибки и граничные случаи",
    ],
    "Тесты": [
        "Добавлены/обновлены unit-тесты на новую логику",
        "Все тесты проходят локально",
        "Покрыты граничные случаи (пустые значения, ошибки, лимиты)",
    ],
    "Документация": [
        "Обновлён README/CHANGELOG, если менялось поведение",
        "Публичные функции/классы имеют docstring",
    ],
    "Безопасность и совместимость": [
        "Не добавлены секреты/токены в код или историю коммитов",
        "Изменения не ломают обратную совместимость публичного API",
    ],
}


def generate_pr_checklist(
    sections: dict[str, list[str]] | None = None,
    pr_title: str | None = None,
) -> str:
    """Формирует Markdown-чек-лист для описания Pull Request.

    Args:
        sections: Словарь {раздел: пункты}. Если ``None`` — используется
            :data:`DEFAULT_CHECKLIST_SECTIONS`.
        pr_title: Необязательный заголовок PR, добавляется первой строкой.

    Returns:
        Markdown-текст с чек-боксами GitHub (``- [ ] пункт``), готовый
        для вставки в описание PR.

    Raises:
        ValueError: если после подстановки итоговый набор разделов пуст
            или один из разделов не содержит пунктов.
    """
    sections = sections if sections is not None else DEFAULT_CHECKLIST_SECTIONS
    if not sections:
        raise ValueError("sections не может быть пустым словарём")

    lines: list[str] = []
    if pr_title:
        lines.append(f"# {pr_title}")
        lines.append("")

    for section, items in sections.items():
        if not items:
            raise ValueError(f"Раздел {section!r} не содержит пунктов чек-листа")
        lines.append(f"### {section}")
        lines.extend(f"- [ ] {item}" for item in items)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
