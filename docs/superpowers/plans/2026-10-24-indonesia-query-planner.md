# Indonesia Query Planner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Turn confirmed target roles and placement preferences into a bounded, reproducible Indonesia search plan without requiring additional dependencies or live scraping.
**Architecture:** A standard-library Python CLI emits JSON or readable text. It does not fetch websites, execute generated commands, or write profile/history files. The existing scraper consumes its output and retains the posting-integrity and evidence gates.
**Tech Stack:** Python 3.10+, argparse, JSON, unittest.
**Spec:** Continuation of the approved Indonesia market adaptation and the user's instruction to continue development. Implementation proceeds natively in the existing local branch.

## Global Constraints

- Use actual roles and placement preferences supplied by the caller; reject unresolved YOUR_* placeholders and blank/control-character input.
- Do not create a second personal profile, install dependencies, execute generated commands, or contact portals from the planner.
- Keep local-board routes explicitly WebSearch, and emit existing portal-CLI argument arrays only when available/selected.
- Retain bounded search budgets with visible deferred counts and pagination offsets.
- Remote searches cover Indonesia rather than restricting results to the candidate's home city; actual remote eligibility still needs verification.

## Review Focus

- CLI arguments must remain data in an argv array, never interpolated shell commands.
- Missing Bun must degrade to web discovery without claiming that a CLI ran.
- Missing/placeholder role or placement information must fail without emitting a usable-looking broad search.
- Unsupported portal filters must remain explicit post-fetch checks, not invented CLI flags.
- Repeated terms and pagination must not hide deferred search combinations or duplicate the same request.

### Task 1: Implement a safe, bounded planner

**Files:** tools/indonesia_search_plan.py (new), tests/test_indonesia_search_plan.py (new).
**Interfaces:** CLI --role (repeatable), --location (repeatable; required except remote), --mode onsite|hybrid|remote, --level fresh-graduate|internship|junior|senior|supervisor, --tech, --days 1|7|14|30, --limit, --max-searches, --offset, --web-only, --format json|text. Output searches contain source, role, placement scope, web query, mechanism and optional argv/cwd; metadata records total/selected/deferred/next_offset and post-fetch checks.

- [x] Write behavior tests for Indonesian board scopes, validation, remote scope, level variants, tech opt-in, pagination, data-safe argv and UTF-8.
- [x] Run them against the missing implementation and observe failures.
- [x] Implement only plan generation, validation, explicit fallback and bounded pagination; never execute requests.
- [x] Run planner tests and fix genuine failures.

### Task 2: Integrate and verify

**Files:** .claude/skills/job-scraper/SKILL.md, .claude/skills/job-scraper/search-queries.md, .claude/skills/job-application-assistant/10-indonesia-market.md, README.md.

- [x] Wire the planner into search preparation after collecting actual role/location preferences; retain the free-form strategy and source-failure fallback.
- [x] Document example invocations as examples and describe Bun detection, remote scope, limits and unexecuted-plan semantics.
- [x] Bump the market-guide framework version and run consistency/security/version checks.
- [x] Perform fresh read-only review, exercise example plans, and run the full Python suite.
- [x] Record exact verification results and limitations. Keep changes local; integration/publishing is outside this request.

## Execution record — 2026-10-24

- Implemented in the existing local branch codex/indonesia-job-search, with no new dependencies, profile files, network calls or executed portal commands from the planner.
- Task 1 complete: behavioral tests were written before the script existed and failed; the first implementation passed. Additional punctuation-only input cases failed before validation was tightened.
- Task 2 complete: planner is wired into search preparation, replacing equivalent discovery requests rather than duplicating them; existing fetch/integrity/expiry/dedup gates remain mandatory.
- Review ruling: Freehire's country/city facets are OR. The planner now performs one country-ID request per role, preserving every requested placement scope for verification. Repeated country-wide calls are removed before pagination.
- Review ruling: installed portals' enabled:false applies before either CLI or WebSearch planning; omitted sources are reported. Missing CLI files never receive executable argv.
- Both review regressions were observed failing before their fixes. Fresh targeted review verified both resolved; no remaining concrete findings.
- Cross-platform instruction checks found bare-python example commands in a workflow guide; canonical examples now use python3 with the existing Windows note convention. README examples remain Windows-oriented.
- Final planner tests: 14 passed. Combined targeted planner/spec tests: 29 passed.
- Full final Python suite: 860 tests in 99.053 seconds, 845 passed, 15 skipped, no failures/errors. Framework version, security guards and git diff --check passed.
- Skip conditions unchanged: 6 require PyYAML, 7 apply only to pristine upstream templates, 2 need Windows symlink privileges. No dependencies were installed; direct PyYAML-based lint remains unavailable.
- Output examples were exercised offline for fresh-graduate Admin/Bandung and remote Data Analyst/Indonesia. They remain illustrative, not candidate profile facts or actual job results.
