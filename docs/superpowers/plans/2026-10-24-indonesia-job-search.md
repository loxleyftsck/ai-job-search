# Indonesia Job Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Apply the approved Indonesia adaptation with tested deduplication and honest incomplete-data verdicts.
**Architecture:** Keep the existing Python state helpers and agent workflow specifications. Add one canonical Indonesia market guide and wire it into setup, scrape, rank, and apply; do not invent portal APIs.
**Tech Stack:** Python standard library, unittest, Markdown workflow specifications.
**Spec:** docs/superpowers/specs/2026-10-24-indonesia-job-search-design.md (approved 2026-10-24).

## Global Constraints

- Preserve old state keys and application history.
- Do not install dependencies or send applications.
- Keep candidate facts as placeholders until supplied.
- Local-board integrations use web search fallback, not an unverified scraper.
- Implement in the current checkout; user explicitly authorized implementation of the design.

## Review Focus

- Location is missing in legacy entries: deduplication stays conservative.
- Known different cities with the same company/title: retain both without key collision.
- Repeated URL with differing query tracking: leave URL canonicalization outside this bounded change; retain current exact-URL behavior.
- A missing/null/empty gate must be FLAG, while explicit FAIL remains a veto.
- A later scoring result must not silently inherit an outdated language PASS or hide a FLAG reason.

### Task 1: Preserve distinct locations

**Files:** tools/scrape_state.py, tests/test_scrape_state.py, .claude/skills/job-scraper/SKILL.md.
**Interfaces:** select(jobs, seen, tracker, strict=False) retains its return schema. Storage uses a private collision helper returning a stable new key; make_key and existing keys remain unchanged. Tracker company/title exclusions stay conservative and are documented.

- [x] Add regression tests for different-city selection/storage, repeat selection, missing location, exact same URL, and unchanged historical entries.
- [x] Run tests/test_scrape_state.py and verify the new different-city tests fail on the baseline.
- [x] Compare normalized company/title plus location when both locations are known; missing location remains a match. Assign an unused stable suffix from the posting URL only on new key collisions, after all entries have validated.
- [x] Run scrape and job-key tests; align the scraper specification with exact behavior.

### Task 2: Keep unknown verdicts visible

**Files:** tools/rank_state.py, tests/test_rank_state.py, .claude/commands/rank.md.
**Interfaces:** cmd_apply(args) keeps ranked/vetoed/errors output. Missing gate values become FLAG with location_note/language_note, emitted and persisted. Explicit valid legacy location verdicts remain readable.

- [x] Add regression tests for absent/null/empty gates, explicit FAIL, legacy location compatibility, and reason replacement on re-score.
- [x] Run the added tests and verify failure on PASS defaults.
- [x] Validate supplied gates, use FLAG for unavailable decisions, and persist/report notes. Preserve existing score math and retry semantics.
- [x] Run rank-state, rank-command, and score-rounding tests; update the JSON contract and reporting instructions.

### Task 3: Wire Indonesia configuration into the full workflow

**Files:** .claude/skills/job-application-assistant/10-indonesia-market.md (new), CLAUDE.md, .claude/commands/setup.md, .claude/skills/job-scraper/search-queries.md, .claude/skills/job-scraper/SKILL.md, .claude/skills/job-application-assistant/04-job-evaluation.md, .claude/skills/job-application-assistant/SKILL.md, .claude/commands/rank.md, .claude/commands/apply.md, README.md.
**Interfaces:** one canonical Indonesia guide; call sites reference it instead of copying the whole policy. Existing profile and tracker schemas remain valid.

- [x] Verify local board URLs from primary pages, especially Kalibrr. Add source links and label fallback access accurately.
- [x] Add setup questions for work mode, actual city/commute/relocation, level/education, contract preferences, IDR salary period/basis and known languages without fabricating answers.
- [x] Add local-board query templates, keyword variants and source fallback. Keep the country-specific portal opt-in flags unchanged.
- [x] Correct location scoring to honor candidate preferences; unknown information is FLAG, remote does not imply Indonesia eligibility. State the fresh-graduate, contract, salary and recruiter-verification rules once in the market guide.
- [x] Wire guide loading into all consumers; bump framework_version where required.
- [x] Run specification consistency tests, skill lint and framework version checks; run the relevant Python suite.

### Task 4: Final review and verification

- [x] Inspect diff for compatibility, unknown-data behavior, and candidate privacy.
- [x] Run the documented regression checks on the final files.
- [x] Report implemented behavior, exact test results and the untested live-portal limitations.

## Execution record — 2026-10-24

- Implemented locally on `codex/indonesia-job-search` in the dedicated clone; changes remain uncommitted for review. No push, application submission or dependency installation.
- Task 1: complete. Reproduced two different-city postings collapsing to one, watched regressions fail, then passed selection/storage/history/key checks. Also tested unknown/N/A/belum diketahui sentinels before treating them as unknown.
- Task 2: complete. Reproduced missing decisions becoming PASS; regressions now verify FLAG reasons, preserved prior vetoes, explicit PASS cleanup, invalid-value errors and legacy state compatibility.
- Task 3: complete. Added canonical Indonesia guide and wired setup/scrape/rank/apply. Verified current local-board pages, including kalibrr.id. Workflow behavior scenarios changed from blanket relocation FAIL/remote PASS to evidence-based PASS/FAIL/FLAG.
- Ruling: added eligibility_gate/eligibility_note during final review because the approved must-have exclusions otherwise had no representation in /rank. Salary/contract conflicts cannot safely be encoded as location/language failure or expiry. Three new failing regressions preceded implementation; the helper now independently vetoes eligibility FAIL and preserves its evidence.
- Ruling: retained exact-URL matching, historical keys and conservative tracker company/role exclusions. Geographic aliases and a tracker-location migration remain out of scope as specified.
- Ruling: replaced an exact old-version assertion with a minimum-version assertion; the posting integrity-gate presence check remains intact.
- Task 4: complete. Focused final suite: 108 tests, 107 passed and 1 skipped. Full final suite: 846 tests in 102.385 seconds, 831 passed, 15 skipped, no failures/errors. Framework version check, security guards and git diff --check passed.
- Skip breakdown: 6 PyYAML-dependent lint integrations, 7 pristine-upstream template guards in this fork, 2 Windows symlink-privilege checks. Direct lint_skills.py cannot run without PyYAML; no dependency was installed to bypass the approved scope.
- Independent final review: original general must-have veto and commute-filter findings resolved; targeted re-verification reported no remaining actionable findings.
- Live portal limit: these changes provide local-board WebSearch/fetch routes, not new verified scrapers. Bun/LinkedIn live CLI behavior was not exercised; the earlier LinkedIn request returned HTTP 429.
