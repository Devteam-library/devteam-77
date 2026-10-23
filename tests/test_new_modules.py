"""Tests for retro, review_stats, and onboarding modules."""

import pytest
from devteam_library.retro import RetroEntry, build_retro_report
from devteam_library.review_stats import PRRecord, ReviewStats
from devteam_library.onboarding import OnboardingConfig, build_onboarding_checklist


# ── retro ────────────────────────────────────────────────────────────────────

class TestRetro:
    def _entries(self):
        return [
            RetroEntry(
                author="Alice",
                went_well=["fast CI"],
                to_improve=["standups too long"],
                action_items=["timebox standups — Alice"],
            ),
            RetroEntry(
                author="Bob",
                went_well=["smooth deploy"],
                to_improve=["unclear ACs"],
                action_items=["add AC template — Bob"],
            ),
        ]

    def test_report_contains_sprint_name(self):
        report = build_retro_report("Sprint 10", self._entries())
        assert "Sprint 10" in report

    def test_report_contains_went_well(self):
        report = build_retro_report("Sprint 10", self._entries())
        assert "fast CI" in report

    def test_report_contains_action_items(self):
        report = build_retro_report("Sprint 10", self._entries())
        assert "timebox standups" in report

    def test_velocity_section_shown(self):
        report = build_retro_report("Sprint 10", self._entries(), velocity=34, planned_points=40)
        assert "34" in report
        assert "85%" in report

    def test_empty_entries(self):
        report = build_retro_report("Sprint 0", [])
        assert "Sprint 0" in report
        assert "No input collected" in report


# ── review_stats ─────────────────────────────────────────────────────────────

class TestReviewStats:
    def _records(self):
        return [
            PRRecord(101, "alice", ["bob", "carol"], "2025-09-01", "2025-09-03"),
            PRRecord(102, "bob",   [],               "2025-09-02", None),
            PRRecord(103, "carol", ["alice"],         "2025-09-02", "2025-09-05"),
        ]

    def test_unreviewed(self):
        stats = ReviewStats(self._records())
        unrev = stats.unreviewed()
        assert len(unrev) == 1
        assert unrev[0].pr_id == 102

    def test_review_counts(self):
        stats = ReviewStats(self._records())
        counts = stats.review_counts()
        assert counts["bob"] == 1
        assert counts["carol"] == 1
        assert counts["alice"] == 1

    def test_avg_turnaround(self):
        stats = ReviewStats(self._records())
        ta = stats.avg_turnaround_days()
        assert ta["alice"] == 2.0   # 3 Sep - 1 Sep
        assert ta["carol"] == 3.0   # 5 Sep - 2 Sep

    def test_summary_markdown_contains_table(self):
        stats = ReviewStats(self._records())
        md = stats.summary_markdown()
        assert "| Reviewer" in md
        assert "Unreviewed" in md

    def test_all_reviewed(self):
        records = [PRRecord(1, "alice", ["bob"], "2025-01-01", "2025-01-02")]
        stats = ReviewStats(records)
        assert "All PRs have reviewers" in stats.summary_markdown()


# ── onboarding ───────────────────────────────────────────────────────────────

class TestOnboarding:
    def _config(self, role="Backend Developer"):
        return OnboardingConfig(
            name="Ivan",
            role=role,
            start_date="2025-10-01",
            buddy="Alice",
            repos=["api-service", "devteam-77"],
            extra_steps=["Complete security training"],
            week_2_goals=["Ship first independent feature"],
        )

    def test_name_in_checklist(self):
        md = build_onboarding_checklist(self._config())
        assert "Ivan" in md

    def test_buddy_in_checklist(self):
        md = build_onboarding_checklist(self._config())
        assert "Alice" in md

    def test_repos_listed(self):
        md = build_onboarding_checklist(self._config())
        assert "api-service" in md
        assert "devteam-77" in md

    def test_backend_role_steps(self):
        md = build_onboarding_checklist(self._config("Backend Developer"))
        assert "Docker Compose" in md

    def test_frontend_role_steps(self):
        md = build_onboarding_checklist(self._config("Frontend Developer"))
        assert "component library" in md

    def test_extra_steps(self):
        md = build_onboarding_checklist(self._config())
        assert "security training" in md

    def test_checkboxes_present(self):
        md = build_onboarding_checklist(self._config())
        assert "- [ ]" in md
