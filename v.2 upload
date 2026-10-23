## [Unreleased]

### Added

- **`devteam_library.retro`** — Sprint retrospective report generator.  
  Collects "went well / to improve / action items" from each team member and renders
  a structured Markdown report with optional velocity stats.  
  New public API: `RetroEntry`, `build_retro_report()`.

- **`devteam_library.review_stats`** — PR review workload analytics.  
  Tracks who reviewed what, surfaces unreviewed PRs, and reports average
  open→merge turnaround per author from any list of `PRRecord` dicts.  
  New public API: `PRRecord`, `ReviewStats`.

- **`devteam_library.onboarding`** — Onboarding checklist generator.  
  Produces a GitHub-flavoured Markdown checklist (`- [ ]`) for new team members,
  with role-aware presets (backend / frontend / devops / qa) and fully
  configurable extra steps and week-2 goals.  
  New public API: `OnboardingConfig`, `build_onboarding_checklist()`.

- Tests for all three new modules in `tests/test_new_modules.py`.
