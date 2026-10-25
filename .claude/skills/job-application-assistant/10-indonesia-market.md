---
framework_version: 1.0.1
---

# Indonesia Market Guide

This is the canonical Indonesia policy for this checkout. Read it with the candidate profile and `04-job-evaluation.md` before setup, search, ranking, or application drafting. It refines the existing workflow; it does not supply candidate facts or replace the posting integrity gate. If the user selects another market, adapt the search sources and apply their confirmed preferences instead.

## Onboarding: collect once, reuse everywhere

Use Bahasa Indonesia for conversation unless the user requests otherwise. Ask only for information not already supplied by the candidate or their documents. A target market of Indonesia does not establish citizenship, work rights, home city, education, or language proficiency.

Capture confirmed answers in `CLAUDE.md` and the canonical profile; put search terms and geographic tiers in `../job-scraper/search-queries.md`. Do not create a second personal profile here.

| Preference | What to confirm |
|---|---|
| Work function and level | Desired daily work, 3-8 useful title variants, sector; student, fresh graduate, experienced, or career switcher |
| Location | Actual city/kabupaten, acceptable placement areas and commute limit; distinguish Kota from Kabupaten where relevant |
| Work mode | On-site, hybrid, remote; office frequency, travel, shift/weekend willingness, relocation yes/no/undecided |
| Education and evidence | SMA/SMK, D3/D4, S1/S2 or the candidate's actual qualification; projects, internships, freelance and employment as distinct evidence |
| Employment type | Permanent/tetap, contract/PKWT, outsourcing, internship/magang, freelance, part-time; preferred vs unacceptable |
| Compensation | Optional minimum and target in IDR, monthly/yearly period, gross/net/THP when known; distinguish hard floor from negotiable target |
| Language and documents | Confirm actual working languages and proficiency; choose CV language independently of conversation language |
| Availability | Actual start date/notice period and any confirmed scheduling constraints |

Keep unanswered preferences explicitly unknown. Do not default a person to Jakarta, software engineering, S1, full working rights, or fluent English. Ask for the target function and location scope before personalized searching, and establish a usable profile before scoring or drafting. Examples below are examples, not the candidate's preferences.

## Search sources and bounded fallback

Local-board pages checked on 2026-10-24:

| Source | Route used by this checkout | Primary page |
|---|---|---|
| JobStreet Indonesia | WebSearch discovery, then fetch the actual posting | [Jobs](https://id.jobstreet.com/jobs) |
| Glints Indonesia | WebSearch discovery, then fetch the actual posting | [Glints Indonesia](https://glints.com/id) |
| Dealls | WebSearch discovery, then fetch the actual posting | [Loker](https://dealls.com/loker) |
| Kalibrr Indonesia | WebSearch on `kalibrr.id`, then fetch the actual posting | [Kalibrr](https://www.kalibrr.id/home) |
| LinkedIn | Existing `linkedin-search` CLI with explicit confirmed location; WebSearch fallback | [Indonesia jobs](https://id.linkedin.com/jobs/search) |
| Freehire | Existing `freehire-search --country ID` for relevant tech roles only | Coverage is best-effort, not a complete Indonesia index |
| Employer careers | Find independently and prefer the employer's own posting when available | Verify the actual employer domain |

The first four routes are **not installed portal CLIs or verified scraping APIs**. Their search and posting pages can require login, change structure, or block access. `kalibrr.com` can appear in older results; do not silently rewrite an old posting URL to `.id` and assume it is the same job. Locate the actual current posting independently.

Use the function/title variants from `search-queries.md`, adding relevant Indonesian and English synonyms. Examples: administrasi/admin/administrative assistant; akuntansi/accounting; layanan pelanggan/customer service; pengembang perangkat lunak/software developer. Add lulusan baru/fresh graduate, magang/intern, staf/staff or supervisor only for the appropriate level. Do not require an English job title merely because the software documentation is English.

Follow documented CLI flags and bounded retry policies. After a 429/rate-limit, 403, login wall, or unavailable Bun runtime, record that source as unavailable and use the existing WebSearch/employer-careers fallback. Do not restart the same failing CLI repeatedly, bypass access controls, or claim zero search hits means no jobs exist. A pasted description is supported by `/apply`; label its source as user-provided rather than claiming a live fetch succeeded.

### Reproducible search preparation

`tools/indonesia_search_plan.py` turns confirmed inputs into a bounded plan without a second personal-profile file, new dependencies, network calls, history writes or command execution. Run from the repo root; on Windows use `python`, elsewhere `python3` as appropriate. These are examples, not the candidate's preferences:

> **Windows:** run these tools as `python`, not `python3`. A python.org install ships no `python3`; use the interpreter where your packages are installed.

```text
python3 tools/indonesia_search_plan.py --role "Admin" --role "Administrative Assistant" --location "Bandung" --level fresh-graduate --web-only --format text
python3 tools/indonesia_search_plan.py --role "Data Analyst" --mode remote --tech --max-searches 10
```

Supply up to 8 distinct role variants and 8 placement scopes with repeated `--role`/`--location`. City, metro or nationwide scope must come from the profile; syntax validation is not geocoding. Non-remote searches require a scope; remote searches deliberately use Indonesia-wide discovery instead of the home city. Empty, punctuation-only, invisible/control-character and unresolved `YOUR_*` values are rejected.

The default JSON includes the actual query, selected mechanism, optional existing CLI `argv`/`cwd`, `recency_days`, post-fetch checks and pagination metadata. The CLI path is present only when Bun and the installed CLI file are available and `--web-only` is not selected. Local boards remain WebSearch routes; Freehire appears only with `--tech`. Installed portals with `enabled: false` are omitted before pagination and listed in `disabled_sources`, including their WebSearch route. Execute arrays as data through a process API, never by joining/evaluating a shell command. An array in the output does not mean it ran.

`--mode onsite|hybrid|remote` and `--level fresh-graduate|internship|junior|senior|supervisor` are optional confirmed preferences. Level keywords affect web discovery; unsupported CLI seniority filters are not invented. CLI results can therefore be broader and require post-fetch checks. Freehire's country and city facets form an OR-group, so the planner searches country `ID` once per role, with no misleading additional city filter; its item retains every requested `placement_scopes` for actual placement verification. Equivalent country-wide requests are removed before counting/pagination.

The default budget is 20 search items, with `--max-searches` 1–200 and a `next_offset` for remaining items. Continue with the **same inputs** and that `--offset` to avoid repeating the previous page. Keep `deferred` visible instead of calling those jobs nonexistent. `--days` accepts 1/7/14/30 (default 14), and `--limit` caps a CLI's results without guaranteeing its yield. Search recency is a discovery window, not a closing date or a verification that a job is active. Use the existing fetch/integrity/expiry gates after executing discovery.

Search snippets are leads, not verified job text. Fetch a real posting, apply `posting_guard.py`, preserve the actual URL and source/portal provenance, and only then score. Reject category/blog/listing pages as job records. A failed fetch is not proof a vacancy closed. Prefer recent postings, but do not discard an older one with a confirmed future deadline; unknown dates remain unknown. A recruiter's recent activity is not the posting date, and an evergreen label is not evidence of an open requisition.

## Placement and remote eligibility

Evaluate the **work placement**, not the employer's headquarters. Jabodetabek or another metro label does not prove the commute is acceptable. Keep Kota/Kabupaten and office attendance requirements visible; do not invent commute times or merge places by a loose substring.

- **PASS:** stated placement/work mode is compatible with confirmed candidate constraints. A candidate who explicitly accepts relocation can pass a job in the accepted destination.
- **FAIL:** an explicit requirement contradicts a confirmed must-have: e.g. mandatory Singapore office visits for a candidate who cannot travel there, or on-site Surabaya when relocation is explicitly refused and commuting is impossible.
- **FLAG:** either side is unknown or ambiguous: unspecified office address, hybrid without frequency, remote without stated acceptance of Indonesia-based workers, or undecided relocation. Say exactly what needs confirming.

Remote is not automatically worldwide or work-from-anywhere. For foreign employers, look for Indonesia eligibility, employment/contractor arrangement, timezone overlap and office/travel requirements in the posting. Keep visa/work-rights questions unverified until supported; a remote label alone cannot answer them. Use the user's timezone for deadline comparisons (Indonesia includes WIB, WITA and WIT); this session's default is Asia/Jakarta, not a claim all Indonesian candidates use WIB. Never infer a deadline year or time from a truncated label.

## Fit and application evidence

Use the standard score weights and bands. Score functions and evidence rather than prestige or literal title matches. Do not assume every Indonesian candidate has a technology background.

- For fresh graduates or career switchers, recognize verified projects, organization work, internships and freelance work as transferable evidence, clearly labeled. Do not fabricate years of professional experience or treat a missing formal job history as no capability.
- Compare stated education/major, certification and experience requirements with actual qualifications. Do not claim D3/D4/S1 equivalence accepted by an employer unless its requirements support that interpretation. Distinguish required conditions from preferred ones; a hard condition the candidate cannot satisfy is a visible eligibility concern, never hidden behind a high score.
- Record contract type, outsourcing employer vs placement company, probation, shifts, relocation, bond/ikatan dinas or document retention only when stated. Compare them with confirmed must-haves. Terms not mentioned are questions, not automatic passes or failures.
- Evaluate languages required **for the role**, not the ad's language. An empty/placeholder Languages table is an incomplete profile, not proof the person speaks no languages: ask before hard-rejecting. Once the table is confirmed, apply the standard Language Gate. Undeclared required languages fail; a declared language with an uncertain level match is flagged.
- A posting rarely proves company culture. When the required numeric behavioral score lacks evidence, use a transparent neutral **50**, label it `unverified / belum diketahui`, and explain it is a neutral placeholder rather than evidence of friction. Do not infer a good culture from brand reputation. The fit score is not a probability of getting hired.
- Draft only from verified candidate facts. Keep the chosen CV language, follow the employer/posting's cover-letter instructions, and preserve official qualification names. Use a profile-appropriate template; no invented personal identity, age, photo, religion or marital status just to imitate a perceived local convention.

## Salary: preserve units and uncertainty

Quote the original range and keep currency, period and gross/net/THP separate. `Rp5–7 juta per bulan` means IDR 5,000,000–7,000,000 monthly; an unqualified `Rp5–7 juta` has an unknown period. Never guess the currency from a bare number. Do not compare annual and monthly figures without an explicit, shown conversion, or compare gross to a net minimum as though equivalent.

If a range overlaps a candidate's minimum, show that overlap and clarify the attainable offer; it is not automatically below the floor. Treat a salary mismatch as a hard exclusion only when the whole stated range is below a confirmed hard minimum on a comparable currency/period/basis. Hidden/negotiable salary is **belum diketahui**, not zero and not a rejection.

THR, BPJS, transport, meals, commission, bonus and other benefits are stated/not stated; never add them to an offer or assume a guaranteed amount. Distinguish base pay from total compensation and commission-only roles. This workflow does not determine legal compliance or inject an unverified UMP/UMK figure. The optional salary tool needs the user's own sourced data; it does not ship an Indonesian market salary database.

## Recruiter verification and candidate control

Surface a recruitment fee/deposit, identity mismatch, personal payment request, unclear employer, or request for sensitive documents as a concrete item to verify. Quote the evidence and check an independently located official careers channel; a signal alone is not proof a company is fraudulent. Do not collect/send KTP, KK, NPWP, bank details, OTPs or other sensitive documents as part of job discovery. Do not contact a recruiter, pay, create an account or submit an application without the user's authorization.

## Deduplication and reporting boundaries

`scrape_state.py` deduplicates identical URLs and company+title hits in the same known location. It retains different known locations and uses a URL-derived suffix only for new key collisions; it never renames old keys. Missing locations and legacy verdicts under `location` remain conservative. Place comparison is case/separator-insensitive, not geocoding; aliases like `Bandung` versus `Bandung, Jawa Barat` may need human review. Presentation can group equivalent descriptions, but every distinct retained location/URL must remain in state and accessible in the report.

The historical application tracker has no structured location column. Its company+role exclusion remains conservative across locations to avoid duplicate applications; report `already_applied`/`excluded_by_tracker` and this limitation when relevant rather than pretending the job never existed. Do not overwrite a prior application or loosen this exclusion without a tracker migration.

An absent/null/empty location, language or `eligibility_gate` decision is FLAG with a visible reason. Preserve earlier FAIL/FLAG when a fresh result omits a decision; a new explicit decision can replace it. Do not silently claim an old PASS means the new assessment succeeded. In `/rank`, confirmed non-location/non-language must-have conflicts use `eligibility_gate: FAIL` plus `eligibility_note`; they are vetoed independently of fit score. Unknown or negotiable salary/contract terms are not a FAIL. The helper enforces the reported decision, not an automatic salary parser; the scorer must ground it in the posting and confirmed profile.

In Bahasa Indonesia, summarize: jabatan/perusahaan, lokasi dan mode kerja, kontrak, gaji beserta periode/basis, tanggal/batas lamaran yang diketahui, alasan cocok, gap, hal yang perlu dikonfirmasi, and a clickable verified posting URL. Say `belum diketahui` instead of filling blanks. Distinguish source failures, incomplete records, explicit exclusions and actual closed postings. `/apply` prepares documents; drafting is not submission.
