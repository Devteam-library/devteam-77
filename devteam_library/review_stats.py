"""
devteam_library.review_stats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Pull Request review workload analytics.

Tracks who reviewed what, surfaces unreviewed PRs, and reports
average review turnaround time per author — no external API needed,
works from any list of plain dicts you feed it (GitHub webhook payloads,
a CSV export, your own tracker).

Usage::

    from devteam_library.review_stats import PRRecord, ReviewStats

    records = [
        PRRecord(pr_id=101, author="alice", reviewers=["bob", "carol"],
                 opened_at="2025-09-01", merged_at="2025-09-03"),
        PRRecord(pr_id=102, author="bob",   reviewers=[],
                 opened_at="2025-09-02", merged_at=None),
        PRRecord(pr_id=103, author="carol", reviewers=["alice"],
                 opened_at="2025-09-02", merged_at="2025-09-04"),
    ]

    stats = ReviewStats(records)
    print(stats.summary_markdown())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional
from collections import defaultdict


_DATE_FMT = "%Y-%m-%d"


def _parse(d: Optional[str]) -> Optional[date]:
    return datetime.strptime(d, _DATE_FMT).date() if d else None


@dataclass
class PRRecord:
    """Minimal representation of one pull request."""

    pr_id: int
    author: str
    reviewers: List[str] = field(default_factory=list)
    opened_at: Optional[str] = None   # "YYYY-MM-DD"
    merged_at: Optional[str] = None   # "YYYY-MM-DD" or None if still open


class ReviewStats:
    """Compute and report PR review load across a list of :class:`PRRecord`."""

    def __init__(self, records: List[PRRecord]) -> None:
        self.records = records

    # ------------------------------------------------------------------ #
    # Core metrics                                                         #
    # ------------------------------------------------------------------ #

    def unreviewed(self) -> List[PRRecord]:
        """Return PRs that have no reviewers assigned."""
        return [r for r in self.records if not r.reviewers]

    def review_counts(self) -> Dict[str, int]:
        """Return ``{reviewer: number_of_prs_reviewed}`` mapping."""
        counts: Dict[str, int] = defaultdict(int)
        for record in self.records:
            for reviewer in record.reviewers:
                counts[reviewer] += 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def avg_turnaround_days(self) -> Dict[str, float]:
        """
        Average days from open → merge, grouped by PR author.
        Only closed PRs are included.
        """
        buckets: Dict[str, List[int]] = defaultdict(list)
        for r in self.records:
            opened = _parse(r.opened_at)
            merged = _parse(r.merged_at)
            if opened and merged:
                buckets[r.author].append((merged - opened).days)
        return {
            author: round(sum(days) / len(days), 1)
            for author, days in buckets.items()
        }

    def author_pr_counts(self) -> Dict[str, int]:
        """Return ``{author: total_prs_opened}`` mapping."""
        counts: Dict[str, int] = defaultdict(int)
        for r in self.records:
            counts[r.author] += 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    # ------------------------------------------------------------------ #
    # Report                                                               #
    # ------------------------------------------------------------------ #

    def summary_markdown(self) -> str:
        """Render a Markdown summary table suitable for a daily or weekly report."""
        lines: List[str] = ["# 📋 PR Review Stats\n"]

        # Review load table
        rc = self.review_counts()
        if rc:
            lines.append("## Reviews given\n")
            lines.append("| Reviewer | PRs reviewed |")
            lines.append("|----------|-------------|")
            for reviewer, count in rc.items():
                lines.append(f"| {reviewer} | {count} |")
            lines.append("")

        # Turnaround
        ta = self.avg_turnaround_days()
        if ta:
            lines.append("## Avg. turnaround (open → merge)\n")
            lines.append("| Author | Avg days |")
            lines.append("|--------|----------|")
            for author, days in sorted(ta.items(), key=lambda x: x[1]):
                lines.append(f"| {author} | {days} |")
            lines.append("")

        # Unreviewed
        unrev = self.unreviewed()
        if unrev:
            lines.append(f"## ⚠️ Unreviewed PRs ({len(unrev)})\n")
            for r in unrev:
                lines.append(f"- PR #{r.pr_id} by **{r.author}** (opened {r.opened_at})")
            lines.append("")
        else:
            lines.append("## ✅ All PRs have reviewers\n")

        return "\n".join(lines)
