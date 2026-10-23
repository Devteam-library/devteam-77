"""
devteam_library.onboarding
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Onboarding checklist generator for new team members.

Produces a Markdown checklist (GitHub-flavoured, with ``- [ ]`` items)
that can be pasted directly into a GitHub Issue, Notion page, or
Confluence task.  Roles and custom steps are fully configurable.

Usage::

    from devteam_library.onboarding import OnboardingConfig, build_onboarding_checklist

    config = OnboardingConfig(
        name="Ivan",
        role="Backend Developer",
        start_date="2025-10-01",
        buddy="Alice",
        repos=["api-service", "devteam-77"],
        extra_steps=["Complete security training by end of week 1"],
    )

    print(build_onboarding_checklist(config))
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ── Role-specific step presets ──────────────────────────────────────────────

_ROLE_STEPS: dict[str, List[str]] = {
    "backend": [
        "Set up local dev environment (Docker Compose)",
        "Run all tests locally and confirm they pass",
        "Read API design guidelines in `docs/api.md`",
        "Review DB schema and migration conventions",
        "Complete first small task / bugfix in week 1",
    ],
    "frontend": [
        "Set up Node.js environment and run dev server",
        "Read component library documentation",
        "Review design system tokens and Figma guidelines",
        "Complete first UI component or bugfix in week 1",
    ],
    "devops": [
        "Get access to cloud console (AWS / GCP / Azure)",
        "Review infrastructure-as-code repository",
        "Understand CI/CD pipeline stages",
        "Review incident runbooks in `docs/runbooks/`",
        "Shadow on-call rotation for first sprint",
    ],
    "qa": [
        "Set up test environment and review test strategy",
        "Read QA guidelines and testing conventions",
        "Run existing test suite and review coverage report",
        "Shadow a sprint demo / exploratory session",
    ],
    "default": [
        "Set up local development environment",
        "Run the project locally and confirm it works",
        "Read the contributing guide (`CONTRIBUTING.md`)",
    ],
}

_COMMON_STEPS: List[str] = [
    "Receive and activate all accounts (GitHub, Slack, email, VPN)",
    "Complete HR / legal paperwork",
    "Meet the team — intro call or async intro message in Slack",
    "Review team working agreements and code-of-conduct",
    "Join all relevant Slack channels",
    "Add yourself to the team roster / wiki page",
    "Set up 1-on-1 cadence with tech lead or manager",
    "Review current sprint board and active priorities",
]


# ── Data model ───────────────────────────────────────────────────────────────

@dataclass
class OnboardingConfig:
    """Configuration for one new team member's onboarding checklist."""

    name: str
    role: str                               # e.g. "Backend Developer"
    start_date: str                         # "YYYY-MM-DD"
    buddy: Optional[str] = None            # assigned onboarding buddy
    repos: List[str] = field(default_factory=list)
    extra_steps: List[str] = field(default_factory=list)
    week_2_goals: List[str] = field(default_factory=list)


# ── Builder ───────────────────────────────────────────────────────────────────

def build_onboarding_checklist(config: OnboardingConfig) -> str:
    """
    Generate a Markdown onboarding checklist.

    Args:
        config: :class:`OnboardingConfig` for the new team member.

    Returns:
        A GitHub-flavoured Markdown string with ``- [ ]`` checkboxes.
    """
    role_key = _detect_role_key(config.role)
    role_steps = _ROLE_STEPS.get(role_key, _ROLE_STEPS["default"])

    lines: List[str] = []

    # Header
    lines.append(f"# 🚀 Onboarding — {config.name}")
    lines.append(f"**Role:** {config.role}  ")
    lines.append(f"**Start date:** {config.start_date}  ")
    if config.buddy:
        lines.append(f"**Buddy:** {config.buddy}  ")
    lines.append("")

    # Week 1 — General
    lines.append("## Week 1 — General\n")
    for step in _COMMON_STEPS:
        lines.append(f"- [ ] {step}")
    lines.append("")

    # Week 1 — Role-specific
    lines.append(f"## Week 1 — {config.role}\n")
    for step in role_steps:
        lines.append(f"- [ ] {step}")
    lines.append("")

    # Repos
    if config.repos:
        lines.append("## Repositories to clone & review\n")
        for repo in config.repos:
            lines.append(f"- [ ] `{repo}`")
        lines.append("")

    # Extra steps
    if config.extra_steps:
        lines.append("## Additional tasks\n")
        for step in config.extra_steps:
            lines.append(f"- [ ] {step}")
        lines.append("")

    # Week 2 goals
    if config.week_2_goals:
        lines.append("## Week 2 — Goals\n")
        for goal in config.week_2_goals:
            lines.append(f"- [ ] {goal}")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by [devteam-library](https://github.com/Devteam-library/devteam-77)*")

    return "\n".join(lines)


def _detect_role_key(role: str) -> str:
    """Map a free-text role string to a preset key."""
    role_lower = role.lower()
    for key in ("backend", "frontend", "devops", "qa"):
        if key in role_lower:
            return key
    return "default"
