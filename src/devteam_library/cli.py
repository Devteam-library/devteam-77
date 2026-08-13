"""Командная строка devteam-library: ``devteam <команда> ...``.

Тонкая обёртка над функциями пакета для быстрого использования из
терминала, без написания Python-скрипта. Доступные команды:

* ``devteam changelog`` — сгенерировать changelog из git-истории текущего репозитория.
* ``devteam checklist`` — вывести чек-лист для PR (по умолчанию или из файла).
"""

from __future__ import annotations

import argparse
import sys

from devteam_library.checklist import generate_pr_checklist
from devteam_library.git_utils import build_changelog, get_git_log


def _cmd_changelog(args: argparse.Namespace) -> int:
    """Обработчик команды ``devteam changelog``."""
    try:
        messages = get_git_log(repo_path=args.repo, max_count=args.max_count)
    except RuntimeError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    changelog = build_changelog(messages, version=args.version)
    print(changelog)
    return 0


def _cmd_checklist(args: argparse.Namespace) -> int:
    """Обработчик команды ``devteam checklist``."""
    print(generate_pr_checklist(pr_title=args.title))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Собирает ``argparse.ArgumentParser`` со всеми подкомандами CLI."""
    parser = argparse.ArgumentParser(
        prog="devteam",
        description="Утилиты для команд разработки: changelog, чек-листы PR и другое.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    changelog_parser = subparsers.add_parser("changelog", help="Сгенерировать changelog из git-истории")
    changelog_parser.add_argument("--repo", default=".", help="Путь к git-репозиторию (по умолчанию текущая директория)")
    changelog_parser.add_argument("--max-count", type=int, default=None, help="Ограничить число последних коммитов")
    changelog_parser.add_argument("--version", default=None, help="Номер версии/дата для заголовка changelog")
    changelog_parser.set_defaults(func=_cmd_changelog)

    checklist_parser = subparsers.add_parser("checklist", help="Вывести чек-лист для Pull Request")
    checklist_parser.add_argument("--title", default=None, help="Заголовок PR для чек-листа")
    checklist_parser.set_defaults(func=_cmd_checklist)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI. Возвращает код завершения процесса."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
