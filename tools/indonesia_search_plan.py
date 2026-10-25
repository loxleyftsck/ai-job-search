#!/usr/bin/env python3
"""Build a bounded Indonesia job-search plan; never fetch or execute it.

Run from any directory. Roles and placement scopes must come from confirmed
candidate preferences, not from the examples in the market guide.
"""

import argparse
import itertools
import json
from pathlib import Path
import re
import shutil
import sys
import unicodedata


ROOT = Path(__file__).resolve().parent.parent
SOURCES = (
    ("jobstreet", "JobStreet", "id.jobstreet.com"),
    ("glints", "Glints", "glints.com/id"),
    ("dealls", "Dealls", "dealls.com/loker"),
    ("kalibrr", "Kalibrr", "kalibrr.id"),
    ("linkedin", "LinkedIn", "linkedin.com/jobs"),
)
LEVELS = {
    "fresh-graduate": ("fresh graduate", "lulusan baru", "entry level"),
    "internship": ("magang", "intern", "internship"),
    "junior": ("junior", "staf", "staff"),
    "senior": ("senior",),
    "supervisor": ("supervisor", "pengawas"),
}
MODES = {
    "remote": ("remote", "work from home", "WFH"),
    "hybrid": ("hybrid", "hibrida"),
    "onsite": ("on-site", "onsite", "WFO"),
}
PLACEHOLDER = re.compile(r"\b(?:YOUR_[A-Z0-9_]+|PLACEHOLDER)\b", re.IGNORECASE)
POST_FETCH_CHECKS = (
    "Confirm an actual open posting, not a listing, blog, snippet or recruiter-activity date; run posting_guard before scoring.",
    "Verify placement, commute/relocation and Indonesia remote eligibility against confirmed preferences; a search match is not a PASS.",
    "Verify actual level, education, required work languages and experience; CLI level filters are not assumed supported.",
    "Verify contract and salary currency/period/gross-net basis against confirmed must-haves; missing information stays unknown.",
    "Verify posting/deadline dates; the discovery window does not prove older postings are closed. Preserve known future deadlines.",
)


def confirmed_terms(values: list[str], label: str) -> list[str]:
    if len(values) > 8:
        raise ValueError(f"{label}: at most 8 values per plan")
    result, seen = [], set()
    for value in values:
        if any(unicodedata.category(char) in ("Cc", "Cf") for char in value):
            raise ValueError(f"{label}: control/invisible characters are not allowed")
        text = " ".join(value.split())
        if not text or not any(char.isalnum() for char in text) or len(text) > 160 or text.startswith("-"):
            raise ValueError(f"{label}: supply a non-empty value of at most 160 characters, not a flag")
        if PLACEHOLDER.search(text):
            raise ValueError(f"{label}: replace the profile placeholder with a confirmed value")
        if text.casefold() not in seen:
            result.append(text)
            seen.add(text.casefold())
    return result


def phrase(value: str) -> str:
    # Keep user text inside one search phrase; quotes/backslashes are data,
    # not a way to close the phrase and introduce a new search operator.
    return '"' + " ".join(value.replace('"', " ").replace("\\", " ").split()) + '"'


def alternatives(values: tuple[str, ...]) -> str:
    return "(" + " OR ".join(phrase(value) for value in values) + ")"


def portal_enabled(source: str) -> bool:
    if source not in ("linkedin", "freehire"):
        return True
    skill = "linkedin-search" if source == "linkedin" else "freehire-search"
    path = ROOT / ".agents" / "skills" / skill / "SKILL.md"
    if not path.exists():
        return True  # No installed CLI: web discovery is still available.
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read portal configuration: {skill}") from exc
    if not text.startswith("---\n") or "\n---" not in text:
        raise ValueError(f"invalid portal frontmatter: {skill}")
    frontmatter = text.split("\n---", 1)[0]
    flags = re.findall(r"^enabled:\s*([^\n]*)", frontmatter, re.MULTILINE)
    if not flags:
        return True
    value = flags[0].split("#", 1)[0].strip().casefold()
    if len(flags) != 1 or value not in ("true", "false"):
        raise ValueError(f"{skill}: enabled must be true or false")
    return value == "true"


def portal_argv(source: str, role: str, location: str, mode: str | None, days: int, limit: int) -> list[str]:
    skill = "linkedin-search" if source == "linkedin" else "freehire-search"
    argv = ["bun", "run", f".agents/skills/{skill}/cli/src/cli.ts", "search", "--query", role]
    if source == "linkedin":
        place = location if re.search(r"\bindonesia\b", location, re.IGNORECASE) else f"{location}, Indonesia"
        argv.extend(("--location", place))
    else:
        # Country/city form one OR-group in Freehire, not an intersection.
        # Search ID once per role, then verify the requested placements.
        argv.extend(("--country", "ID", "--no-description"))
    if mode:
        argv.extend(("--remote", mode))
    argv.extend(("--jobage", str(days), "--limit", str(limit), "--format", "json"))
    return argv


def build_plan(args, bun_available: bool) -> dict:
    roles = confirmed_terms(args.role, "role")
    supplied_locations = confirmed_terms(args.location or [], "location")
    if not supplied_locations and args.mode != "remote":
        raise ValueError("location: confirm a placement scope with --location (or choose --mode remote)")
    locations = ["Indonesia"] if args.mode == "remote" else supplied_locations
    candidates = SOURCES + (("freehire", "Freehire", "freehire.me/jobs"),) if args.tech else SOURCES
    disabled = [source for source, _, _ in candidates if not portal_enabled(source)]
    sources = [source for source in candidates if source[0] not in disabled]
    include_cli = bun_available and not args.web_only
    searches, planned = [], set()
    for role, location, (source, name, scope) in itertools.product(roles, locations, sources):
        placement_scopes = locations if source == "freehire" else [location]
        if source == "freehire":
            location = "Indonesia"
        identity = (source, role, location)
        if identity in planned:
            continue
        planned.add(identity)
        terms = [f"site:{scope}", phrase(role), phrase(location)]
        if args.level:
            terms.append(alternatives(LEVELS[args.level]))
        if args.mode:
            terms.append(alternatives(MODES[args.mode]))
        item = {
            "source": source,
            "name": name,
            "role": role,
            "location": location,
            "placement_scopes": placement_scopes,
            "query": " ".join(terms),
            "recency_days": args.days,
            "mechanism": "websearch",
        }
        if include_cli and source in ("linkedin", "freehire"):
            argv = portal_argv(source, role, location, args.mode, args.days, args.limit)
            if (ROOT / argv[2]).is_file():
                item.update(mechanism="cli", argv=argv, cwd=str(ROOT))
        searches.append(item)

    total = len(searches)
    selected = searches[args.offset:args.offset + args.max_searches]
    end = args.offset + len(selected)
    notes = [
        "This is an unexecuted discovery plan, not fetched or ranked job results.",
        "Each query is also the WebSearch fallback for its CLI. Use recency_days only if the search tool supports it; otherwise inspect dates client-side.",
        "Local-board sources have no installed scraping CLI in this checkout. Freehire is tech-only and opt-in.",
        "Level and mandatory requirements remain post-fetch checks; no unsupported portal flags are generated.",
        "CLI results may be broader than web queries. Verify every requested placement, level and work-mode preference before scoring.",
        "Freehire searches country ID once per role; its country/city facets are OR, so placement_scopes are checked after fetching.",
    ]
    if args.mode == "remote":
        notes.append("Remote uses Indonesia-wide discovery; a home city does not restrict remote jobs. Verify actual Indonesia eligibility and any office travel.")
    if not bun_available and not args.web_only:
        notes.append("Bun is unavailable on PATH; all sources use WebSearch fallback. No CLI was run.")
    return {
        "market": "ID",
        "executed": False,
        "verification_required": True,
        "bun_available": bun_available,
        "disabled_sources": disabled,
        "roles": roles,
        "requested_locations": supplied_locations,
        "locations": locations,
        "mode": args.mode,
        "level": args.level,
        "offset": args.offset,
        "total": total,
        "selected": len(selected),
        "deferred": max(0, total - end),
        "next_offset": end if end < total else None,
        "searches": selected,
        "post_fetch_checks": list(POST_FETCH_CHECKS),
        "notes": notes,
    }


def bounded_integer(low: int, high: int):
    def parse(value: str) -> int:
        try:
            number = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError("expected an integer") from None
        if not low <= number <= high:
            raise argparse.ArgumentTypeError(f"expected {low}..{high}")
        return number
    return parse


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--role", action="append", required=True, help="confirmed target title; repeat for variants")
    parser.add_argument("--location", action="append", help="confirmed placement scope; required except for remote")
    parser.add_argument("--mode", choices=MODES, help="confirmed work mode; remote uses Indonesia-wide discovery")
    parser.add_argument("--level", choices=LEVELS, help="web keywords; actual seniority still requires verification")
    parser.add_argument("--tech", action="store_true", help="include Freehire for a relevant tech search")
    parser.add_argument("--days", type=int, choices=(1, 7, 14, 30), default=14)
    parser.add_argument("--limit", type=bounded_integer(1, 50), default=20, help="per-CLI result cap, not guaranteed yield")
    parser.add_argument("--max-searches", type=bounded_integer(1, 200), default=20)
    parser.add_argument("--offset", type=bounded_integer(0, 10000), default=0)
    parser.add_argument("--web-only", action="store_true", help="plan only WebSearch even when Bun is available")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    try:
        plan = build_plan(args, bun_available=shutil.which("bun") is not None)
    except ValueError as exc:
        parser.error(str(exc))
    if args.format == "json":
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(f"Rencana pencarian Indonesia: {plan['selected']}/{plan['total']} pencarian; belum dijalankan.")
        for index, item in enumerate(plan["searches"], start=args.offset + 1):
            print(f"\n{index}. {item['name']} — {item['role']} — {item['location']} ({item['mechanism']})")
            print(item["query"])
        if plan["next_offset"] is not None:
            print(f"\nTersisa {plan['deferred']} pencarian. Lanjutkan dengan --offset {plan['next_offset']}.")
        if plan["disabled_sources"]:
            print("\nPortal nonaktif dilewati: " + ", ".join(plan["disabled_sources"]))
        print("\nHasil, lokasi/remote, level, kontrak dan gaji tetap perlu diverifikasi sebelum dinilai.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
