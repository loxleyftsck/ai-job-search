# Search Queries for Job Scraper

<!-- SETUP: Customize these queries based on your skills, target roles, and location -->

**Market preset: Indonesia.** Read `../job-application-assistant/10-indonesia-market.md` for market rules. This file holds query configuration, not candidate facts. Resolve the actual role/function and geographic scope with the user before running queries containing placeholders. Keep the location and proficiency fields unknown until confirmed.

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first. Shipped country-agnostic CLIs include `linkedin-search` and `freehire-search`; Danish demos and any skill you add with `/add-portal` are included the same way. You do **not** need a matching `site:` line below for those CLIs to run.

The `site:` query templates in this file are the **WebSearch fallback** — for portals without a CLI, company career pages, or when a CLI fails.

For this checkout's Indonesia sources, `python tools/indonesia_search_plan.py` generates a bounded plan from confirmed roles, locations and optional work-mode/level preferences. See `../job-application-assistant/10-indonesia-market.md` for usage. Prefer its generated queries/argument arrays over copying unresolved template tokens; preserve any profile-specific queries and custom portals this planner does not cover. It never fetches a result or marks a job as found.

**Language scope:** write every query category in every language listed in your CLAUDE.md Languages table (typically 1-2, sometimes more). A posting requiring a language you have *not* declared, as a job condition, is excluded before scoring; a posting requiring a *higher level* than you declared in a language you *do* work in is flagged for your own judgment, not excluded — see `04-job-evaluation.md`'s Language Gate, the single source of truth for this rule. Translate each category's keywords rather than machine-translating word-for-word (e.g. "Frontend Developer" -> "Desarrollador Frontend", not a literal word-for-word translation) if you work in more than one language.

## Search Sites

Primary for Indonesia:
- **id.jobstreet.com** - JobStreet Indonesia, WebSearch fallback
- **glints.com/id** - Glints Indonesia, WebSearch fallback
- **dealls.com/loker** - Dealls, WebSearch fallback
- **kalibrr.id** - Kalibrr Indonesia, WebSearch fallback; `kalibrr.com` is a legacy discovery source, not a verified alias for a specific posting
- **linkedin.com/jobs** - use `linkedin-search` with the user's confirmed location; fall back to WebSearch when unavailable
- **freehire.me** - use `freehire-search --country ID` only for relevant tech roles, with coverage reported honestly

These local-board fallback routes are not installed portal CLIs. Search engines can return category pages, blogs, old snippets, and login walls. Keep only an actual, fetched posting URL (or explicitly request pasted posting text); never save a listing page as a job.

Secondary (company career pages via Google):
- Direct Google searches with `site:` filters for known target companies

## Query Categories

Queries are grouped by priority. Write **each category in every language from your Languages table** (see Language scope above). Combine each query with your location terms (e.g. your city, region, or metro area) where the site supports it.

**Organize by function, not job title.** The same underlying work carries different titles across companies and markets (a "Data Scientist" role at one employer may be posted as "Insights Analyst" or "Data Consultant" at another). Name each priority category after the function it covers, and list several plausible job titles as query variants within that category rather than betting an entire priority tier on one exact title string.

### Priority 1: [YOUR_PRIMARY_ROLE_TYPE]

These match your strongest and most desired career direction.

```
site:[YOUR_JOB_BOARD] "[YOUR_PRIMARY_JOB_TITLE_1]" [YOUR_CITY]
site:[YOUR_JOB_BOARD] "[YOUR_PRIMARY_JOB_TITLE_2]" [YOUR_CITY]
site:[YOUR_JOB_BOARD] "[YOUR_KEY_SKILL]" [YOUR_CITY]
site:linkedin.com/jobs "[YOUR_PRIMARY_JOB_TITLE_1]" [YOUR_COUNTRY]
```

Indonesia fallback variants (substitute confirmed terms; do not send the brackets):

```
site:id.jobstreet.com "[YOUR_PRIMARY_JOB_TITLE_1]" "[YOUR_CITY]"
site:glints.com/id "[YOUR_PRIMARY_JOB_TITLE_2]" "[YOUR_CITY]"
site:dealls.com/loker "[YOUR_PRIMARY_JOB_TITLE_1]" "[YOUR_CITY]"
site:kalibrr.id "[YOUR_KEY_SKILL]" "[YOUR_CITY]"
site:linkedin.com/jobs "[YOUR_PRIMARY_JOB_TITLE_1]" Indonesia
```

Use functional synonyms appropriate to the profile (e.g. administrasi/admin/administrative assistant, akuntansi/accounting, layanan pelanggan/customer service), not only technical job titles. Add fresh graduate/lulusan baru, magang/intern, staff/staf, or supervisor only when that level matches the candidate. Search English titles only when useful to the role; the ad language alone does not prove a job requires English proficiency.

### Priority 2: [YOUR_DOMAIN_EXPERTISE]

These match your domain expertise.

```
site:[YOUR_JOB_BOARD] [YOUR_DOMAIN_KEYWORD_1] [YOUR_CITY] OR [YOUR_REGION]
site:[YOUR_JOB_BOARD] [YOUR_DOMAIN_KEYWORD_2] [YOUR_COUNTRY]
site:linkedin.com/jobs [YOUR_DOMAIN_KEYWORD_1] [YOUR_CITY] [YOUR_COUNTRY]
```

### Priority 3: [YOUR_ADJACENT_ROLE_TYPE]

Adjacent roles you could pivot into.

```
site:[YOUR_JOB_BOARD] "[YOUR_ADJACENT_TITLE_1]" [YOUR_KEY_SKILL] [YOUR_CITY]
site:[YOUR_JOB_BOARD] "[YOUR_ADJACENT_TITLE_2]" [YOUR_KEY_SKILL] [YOUR_CITY]
```

### Priority 4: Broader Technical / Consulting

Wider net for general technical roles.

```
site:[YOUR_JOB_BOARD] [YOUR_KEY_SKILL] developer [YOUR_CITY]
site:linkedin.com/jobs "[YOUR_KEY_SKILL] developer" [YOUR_CITY]
site:[YOUR_JOB_BOARD] "technical consultant" [YOUR_DOMAIN] [YOUR_CITY]
```

## Location Filter

When evaluating results, apply the confirmed placement/work-mode/relocation preferences and `10-indonesia-market.md`'s location rules. Commute limits apply to actual required office attendance; an accepted relocation destination or an eligible remote job must not be rejected merely because it is far from the current home. If attendance, remote eligibility or candidate preferences are unknown, FLAG rather than guessing. Define acceptable areas for jobs requiring commuting:
- [YOUR_CITY] and surrounding areas
- [ACCEPTABLE_AREA_1]
- [ACCEPTABLE_AREA_2]
- [BORDERLINE_AREA] (borderline - ~X min by transit)
- [TOO_FAR_AREA] (too far)

## Language Filter

Your working languages and levels are in CLAUDE.md's Languages table. When filtering scraped results, apply `04-job-evaluation.md`'s Language Gate: a posting requiring a language you haven't declared at all is excluded; a posting requiring a higher level than you declared in a language you do work in is not excluded, flag it clearly instead (see `job-scraper/SKILL.md`'s Step 3 "Quick Fit Assessment" for how the flag surfaces in `/scrape` output). Postings simply *written* in a language you don't work in, that don't require it on the job, are fine.

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown".

## Adapting Queries

If the user specifies a focus area, select queries from the matching category and also generate 2-3 custom queries for that focus. For example:
- "/scrape [focus_area]" -> relevant category queries + custom focus-specific queries
