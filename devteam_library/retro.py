"""
devteam_library.retro
~~~~~~~~~~~~~~~~~~~~~
Sprint retrospective report generator.

Collects "went well / to improve / action items" from team members
and renders a structured Markdown report ready to paste into Confluence,
Notion, or a GitHub Discussion.

Usage::

    from devteam_library.retro import RetroEntry, build_retro_report

    entries = [
        RetroEntry(
            author="Alice",
            went_well=["CI is fast", "good PR reviews"],
            to_improve=["stand-ups too long"],
            action_items=["timebox stand-up to 15 min — Alice, by Fri"],
        ),
        RetroEntry(
            author="Bob",
            went_well=["new deploy pipeline"],
            to_improve=["unclear acceptance criteria"],
            action_items=["add AC template to PR checklist — Bob"],
        ),
    ]

    report = build_retro_report(
        sprint_name="Sprint 42",
        entries=entries,
        velocity=34,
        planned_points=40,
    )
    print(report)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class RetroEntry:
    """One team member's retrospective input."""

    author: str
    went_well: List[str] = field(default_factory=list)
    to_improve: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)


def build_retro_report(
    sprint_name: str,
    entries: List[RetroEntry],
    velocity: Optional[int] = None,
    planned_points: Optional[int] = None,
    report_date: Optional[date] = None,
) -> str:
    """
    Render a Markdown retrospective report.

    Args:
        sprint_name:     Display name of the sprint, e.g. ``"Sprint 42"``.
        entries:         List of :class:`RetroEntry` from team members.
        velocity:        Actual story points completed (optional).
        planned_points:  Originally planned story points (optional).
        report_date:     Date to show in the header; defaults to today.

    Returns:
        A Markdown string ready to paste into any wiki or GitHub issue.
    """
    today = (report_date or date.today()).strftime("%Y-%m-%d")
    lines: List[str] = []

    # Header
    lines.append(f"# 🔄 Retrospective — {sprint_name}")
    lines.append(f"*Generated: {today}*\n")

    # Velocity block
    if velocity is not None or planned_points is not None:
        lines.append("## 📊 Sprint Stats\n")
        if planned_points:
            lines.append(f"- **Planned:** {planned_points} pts")
        if velocity is not None:
            lines.append(f"- **Completed:** {velocity} pts")
            if planned_points:
                pct = round(velocity / planned_points * 100)
                lines.append(f"- **Completion:** {pct}%")
        lines.append("")

    # Aggregate sections
    all_went_well: List[str] = []
    all_to_improve: List[str] = []
    all_action_items: List[str] = []

    for entry in entries:
        all_went_well.extend(
            [f"{item} *(by {entry.author})*" for item in entry.went_well]
        )
        all_to_improve.extend(
            [f"{item} *(by {entry.author})*" for item in entry.to_improve]
        )
        all_action_items.extend(entry.action_items)

    def _render_section(title: str, emoji: str, items: List[str]) -> None:
        lines.append(f"## {emoji} {title}\n")
        if items:
            for item in items:
                lines.append(f"- {item}")
        else:
            lines.append("*No input collected.*")
        lines.append("")

    _render_section("What went well", "✅", all_went_well)
    _render_section("What to improve", "🔧", all_to_improve)
    _render_section("Action items", "📌", all_action_items)

    # Per-person breakdown
    if entries:
        lines.append("## 👥 Per-person input\n")
        for entry in entries:
            lines.append(f"### {entry.author}\n")
            if entry.went_well:
                lines.append("**Went well:**")
                lines.extend(f"- {i}" for i in entry.went_well)
            if entry.to_improve:
                lines.append("\n**To improve:**")
                lines.extend(f"- {i}" for i in entry.to_improve)
            if entry.action_items:
                lines.append("\n**Action items:**")
                lines.extend(f"- {i}" for i in entry.action_items)
            lines.append("")

    return "\n".join(lines)
