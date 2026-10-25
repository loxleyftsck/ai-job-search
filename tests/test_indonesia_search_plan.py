"""Exercise the query planner's public CLI without network or candidate files."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "indonesia_search_plan.py"


class IndonesiaSearchPlanTests(unittest.TestCase):
    def run_plan(self, *args, expect=0, env=None, tool=TOOL):
        proc = subprocess.run(
            [sys.executable, str(tool), *args],
            cwd=ROOT,
            capture_output=True,
            encoding="utf-8",
            env=env,
        )
        self.assertEqual(proc.returncode, expect, proc.stderr)
        if expect == 2:
            self.assertIn("error:", proc.stderr)
        return proc

    def plan(self, *args):
        return json.loads(self.run_plan(*args, "--web-only").stdout)

    def test_local_boards_have_real_scopes_and_no_claim_of_execution(self):
        plan = self.plan("--role", "Admin", "--location", "Bandung")
        self.assertFalse(plan["executed"])
        searches = {item["source"]: item for item in plan["searches"]}
        for source, scope in {
            "jobstreet": "site:id.jobstreet.com",
            "glints": "site:glints.com/id",
            "dealls": "site:dealls.com/loker",
            "kalibrr": "site:kalibrr.id",
            "linkedin": "site:linkedin.com/jobs",
        }.items():
            with self.subTest(source=source):
                self.assertIn(scope, searches[source]["query"])
                self.assertIn('"Admin"', searches[source]["query"])
                self.assertIn('"Bandung"', searches[source]["query"])
                self.assertEqual(searches[source]["mechanism"], "websearch")
                self.assertNotIn("argv", searches[source])
        self.assertNotIn("freehire", searches)

    def test_blank_missing_and_placeholder_inputs_do_not_emit_a_plan(self):
        cases = [
            [], ["--location", "Bandung"], ["--role", "Admin"],
            ["--role", " ", "--location", "Bandung"],
            ["--role", "Admin", "--location", ""],
            ["--role", "[YOUR_PRIMARY_JOB_TITLE_1]", "--location", "Bandung"],
            ["--role", "Admin", "--location", "[YOUR_CITY]"],
            ["--role", "Admin\nsite:example.org", "--location", "Bandung"],
            ["--role", '""', "--location", "Bandung"],
            ["--role", "...", "--location", "Bandung"],
            ["--role", "Admin", "--location", '""'],
        ]
        for args in cases:
            with self.subTest(args=args):
                proc = self.run_plan(*args, "--web-only", expect=2)
                self.assertEqual(proc.stdout, "")

    def test_remote_uses_indonesia_without_home_city_restriction(self):
        plan = self.plan("--role", "Akuntansi", "--location", "Bandung", "--mode", "remote")
        self.assertTrue(plan["verification_required"])
        for search in plan["searches"]:
            self.assertEqual(search["location"], "Indonesia")
            self.assertIn('"Indonesia"', search["query"])
            self.assertNotIn("Bandung", search["query"])
            self.assertIn("remote", search["query"])

    def test_remote_can_plan_without_a_home_city(self):
        plan = self.plan("--role", "Customer Service", "--mode", "remote")
        self.assertEqual(plan["selected"], 5)
        self.assertEqual(plan["locations"], ["Indonesia"])

    def test_fresh_graduate_variants_and_level_verification_are_visible(self):
        plan = self.plan("--role", "Accounting", "--location", "Surabaya", "--level", "fresh-graduate")
        self.assertIn("lulusan baru", plan["searches"][0]["query"])
        self.assertIn("fresh graduate", plan["searches"][0]["query"])
        self.assertIn("level", " ".join(plan["post_fetch_checks"]).lower())

    def test_budget_and_offsets_preserve_every_deferred_search(self):
        args = ["--role", "Admin", "--role", "Accounting", "--location", "Bandung", "--location", "Surabaya"]
        first = self.plan(*args, "--max-searches", "7")
        second = self.plan(*args, "--max-searches", "7", "--offset", "7")
        third = self.plan(*args, "--max-searches", "7", "--offset", "14")
        self.assertEqual((first["total"], first["selected"], first["deferred"], first["next_offset"]), (20, 7, 13, 7))
        self.assertEqual((third["selected"], third["deferred"], third["next_offset"]), (6, 0, None))
        combined = first["searches"] + second["searches"] + third["searches"]
        self.assertEqual(len({item["query"] for item in combined}), 20)

    def test_duplicate_terms_are_normalized_without_duplicate_queries(self):
        plan = self.plan("--role", " Admin ", "--role", "admin", "--location", " Bandung ", "--location", "BANDUNG")
        self.assertEqual(plan["roles"], ["Admin"])
        self.assertEqual(plan["locations"], ["Bandung"])
        self.assertEqual(plan["total"], 5)

    def test_tech_source_is_opt_in(self):
        plan = self.plan("--role", "Data Analyst", "--location", "Jakarta", "--tech")
        freehire = [item for item in plan["searches"] if item["source"] == "freehire"]
        self.assertEqual(len(freehire), 1)
        self.assertIn("site:freehire.me/jobs", freehire[0]["query"])
        self.assertEqual(freehire[0]["mechanism"], "websearch")

    def test_missing_bun_falls_back_without_invoking_other_programs(self):
        env = dict(os.environ, PATH="")
        plan = json.loads(self.run_plan("--role", "Admin", "--location", "Bandung", env=env).stdout)
        self.assertFalse(plan["bun_available"])
        self.assertTrue(all(item["mechanism"] == "websearch" for item in plan["searches"]))

    def test_cli_plans_keep_untrusted_values_as_individual_arguments(self):
        with TemporaryDirectory() as directory:
            executable = Path(directory) / ("bun.exe" if os.name == "nt" else "bun")
            executable.write_text("This file must never be executed.", encoding="utf-8")
            executable.chmod(0o755)
            env = dict(os.environ, PATH=directory)
            role = 'Admin "B2B"; $(never-execute)'
            plan = json.loads(self.run_plan(
                "--role", role, "--location", "Jakarta", "--tech", "--mode", "hybrid", "--level", "junior", env=env
            ).stdout)
            searches = {item["source"]: item for item in plan["searches"]}
            self.assertTrue(plan["bun_available"])
            for source in ("linkedin", "freehire"):
                argv = searches[source]["argv"]
                self.assertIsInstance(argv, list)
                self.assertEqual(argv[argv.index("--query") + 1], role)
                self.assertEqual(argv[argv.index("--remote") + 1], "hybrid")
                self.assertNotIn("--level", argv)
                self.assertNotIn("--seniority", argv)
                self.assertTrue((ROOT / argv[2]).is_file())
            argv = searches["linkedin"]["argv"]
            self.assertEqual(argv[argv.index("--location") + 1], "Jakarta, Indonesia")
            argv = searches["freehire"]["argv"]
            self.assertEqual(argv[argv.index("--country") + 1], "ID")
            self.assertNotIn("--city", argv)
            self.assertEqual(searches["freehire"]["placement_scopes"], ["Jakarta"])

    def test_freehire_country_discovery_runs_once_and_retains_all_placements(self):
        with TemporaryDirectory() as directory:
            executable = Path(directory) / ("bun.exe" if os.name == "nt" else "bun")
            executable.write_text("Must never run.", encoding="utf-8")
            executable.chmod(0o755)
            env = dict(os.environ, PATH=directory)
            places = ["Bandung, Jawa Barat", "Surabaya, Jawa Timur"]
            args = ["--role", "Data Analyst", "--tech"]
            for place in places:
                args.extend(("--location", place))
            plan = json.loads(self.run_plan(*args, env=env).stdout)
            freehire = [item for item in plan["searches"] if item["source"] == "freehire"]
            self.assertEqual(len(freehire), 1)
            self.assertEqual(plan["total"], 11)
            self.assertEqual(freehire[0]["placement_scopes"], places)
            self.assertEqual(freehire[0]["location"], "Indonesia")
            self.assertNotIn("--city", freehire[0]["argv"])

    def test_disabled_portals_are_skipped_before_planning_cli_or_web(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tools").mkdir()
            tool = root / "tools" / TOOL.name
            shutil.copyfile(TOOL, tool)
            for portal in ("linkedin-search", "freehire-search"):
                folder = root / ".agents" / "skills" / portal
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text("---\nname: example\nenabled: false # user's choice\n---\n", encoding="utf-8")
            for flags in ([], ["--web-only"]):
                with self.subTest(flags=flags):
                    plan = json.loads(self.run_plan("--role", "Developer", "--location", "Bandung", "--tech", *flags, tool=tool).stdout)
                    self.assertEqual({item["source"] for item in plan["searches"]}, {"jobstreet", "glints", "dealls", "kalibrr"})
                    self.assertEqual(set(plan["disabled_sources"]), {"linkedin", "freehire"})

    def test_invalid_numeric_and_enum_flags_are_rejected(self):
        for flags in (("--offset", "-1"), ("--max-searches", "0"), ("--max-searches", "201"),
                      ("--limit", "0"), ("--days", "9999"), ("--mode", "anywhere"), ("--level", "expert")):
            with self.subTest(flags=flags):
                self.run_plan("--role", "Admin", "--location", "Bandung", *flags, expect=2)

    def test_text_output_and_utf8_survive_windows_legacy_encoding(self):
        env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        proc = self.run_plan("--role", "行政アシスタント", "--location", "Bandung", "--web-only", "--format", "text", env=env)
        self.assertIn("行政アシスタント", proc.stdout)
        self.assertIn("JobStreet", proc.stdout)
        self.assertNotIn("UnicodeEncodeError", proc.stderr)


if __name__ == "__main__":
    unittest.main()
