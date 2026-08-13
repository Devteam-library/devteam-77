"""Тесты для devteam_library.git_utils."""

import subprocess

from devteam_library.git_utils import (
    build_changelog,
    get_git_log,
    parse_conventional_commit,
)


def test_parse_conventional_commit_basic():
    parsed = parse_conventional_commit("feat(auth): добавить вход через Google")
    assert parsed.type == "feat"
    assert parsed.scope == "auth"
    assert parsed.description == "добавить вход через Google"
    assert parsed.breaking is False


def test_parse_conventional_commit_breaking_change():
    parsed = parse_conventional_commit("feat!: убрать поддержку Python 3.8")
    assert parsed.type == "feat"
    assert parsed.breaking is True


def test_parse_conventional_commit_no_scope():
    parsed = parse_conventional_commit("fix: убрать падение на пустом списке")
    assert parsed.type == "fix"
    assert parsed.scope is None


def test_parse_conventional_commit_non_conventional_message():
    parsed = parse_conventional_commit("быстрый фикс без формата")
    assert parsed.type is None
    assert parsed.description == "быстрый фикс без формата"


def test_parse_conventional_commit_uses_only_first_line():
    parsed = parse_conventional_commit("fix: заголовок\n\nподробное описание в теле коммита")
    assert parsed.description == "заголовок"


def test_build_changelog_groups_by_type_in_defined_order():
    commits = [
        "fix: исправить крэш при пустом вводе",
        "feat: добавить экспорт в CSV",
        "chore: обновить зависимости",
    ]
    changelog = build_changelog(commits, version="1.2.0")

    assert changelog.startswith("# Changelog — 1.2.0")
    # Разделы должны идти в порядке COMMIT_TYPE_TITLES: feat перед fix
    assert changelog.index("Новые возможности") < changelog.index("Исправления")
    assert "добавить экспорт в CSV" in changelog
    assert "исправить крэш при пустом вводе" in changelog


def test_build_changelog_non_conventional_goes_to_other_section():
    changelog = build_changelog(["просто текстовый коммит без формата"])
    assert "## Прочее" in changelog
    assert "просто текстовый коммит без формата" in changelog


def test_get_git_log_reads_real_repo(tmp_path):
    # Создаём временный git-репозиторий с одним коммитом и проверяем,
    # что get_git_log корректно читает его сообщение.
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "file.txt").write_text("hello")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "feat: первый коммит"], cwd=tmp_path, check=True)

    messages = get_git_log(repo_path=str(tmp_path))
    assert messages == ["feat: первый коммит"]
