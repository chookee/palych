"""Validation tests for the offline evaluation harness; all replies are synthetic."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("blind_eval", Path(__file__).with_name("blind_eval.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class BlindEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "SKILL.md"
        self.skill.write_text("Synthetic skill fixture", encoding="utf-8")
        self.prompts = self.root / "prompts.json"
        self.prompts.write_text(json.dumps({"cases": [{"id": "ru-short", "prompt": "Что означает 404?"}, {"id": "en-short", "prompt": "What does 404 mean?"}]}), encoding="utf-8")
        self.manifest = {"model": "synthetic-test-fixture", "settings": {"temperature": 0}, "tools": [], "base_instructions_sha256": "a" * 64, "skill_sha256": mod.digest(self.skill), "prompts_sha256": mod.digest(self.prompts), "verified": True, "verification_note": "Test fixture, not a measured model run"}
        metadata = {key: self.manifest[key] for key in ("model", "settings", "tools", "base_instructions_sha256")}
        self.records = [{"case_id": case, "repetition": rep, "condition": condition, "response": f"Synthetic {case} response {rep}", "metadata": copy.deepcopy(metadata)} for case in ("ru-short", "en-short") for rep in range(1, 4) for condition in ("baseline", "skill")]

    def prepare(self, records=None, name="run", **kwargs):
        directory = self.root / name
        mod.prepare(self.records if records is None else records, self.manifest, self.prompts, self.skill, directory, seed=42, **kwargs)
        return directory

    def judgments(self, directory):
        rows = mod.read(directory / "judgments-template.json")
        for row in rows:
            row["preference"] = "tie"
            row["reason"] = "Synthetic identical responses; all dimensions apply."
            for score in row["scores"].values():
                score["semantic_pass"] = True
                score["semantic_reason"] = "Synthetic test assessment"
                score["dimensions"] = {key: 2 for key in mod.DIMENSIONS}
        return rows

    def test_masking_and_deterministic_order(self):
        a, b = self.prepare(), self.prepare(name="again")
        self.assertEqual((a / "packets.json").read_bytes(), (b / "packets.json").read_bytes())
        public = (a / "packets.json").read_text()
        for marker in ("baseline", '"skill"', '"case_id"', '"repetition"', "skill_sha256"):
            self.assertNotIn(marker, public)
        labels = [pair["labels"]["A"] for pair in mod.read(a / "private-mapping.json")["mapping"].values()]
        self.assertEqual(set(labels), {"baseline", "skill"})
        self.assertEqual(len(mod.read(a / "packets.json")["pairs"]), 6)

    def test_duplicates_missing_and_unbalanced(self):
        for records in (self.records + [self.records[0]], self.records[:-1], [row for row in self.records if row["case_id"] == "ru-short"]):
            with self.subTest(records=len(records)), self.assertRaises(ValueError):
                self.prepare(records)

    def test_verified_metadata_and_real_hashes(self):
        self.manifest["verified"] = False
        with self.assertRaisesRegex(ValueError, "verified"):
            self.prepare()
        self.manifest["verified"] = True
        self.manifest["skill_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "Skill hash"):
            self.prepare()

    def test_settings_must_match_and_extra_fields_rejected(self):
        rows = copy.deepcopy(self.records)
        rows[0]["metadata"]["settings"] = {"temperature": 1}
        with self.assertRaisesRegex(ValueError, "identical"):
            self.prepare(rows)
        rows = copy.deepcopy(self.records)
        rows[0]["expected_answer"] = "leaked reference"
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            self.prepare(rows)

    def test_pilot_is_explicit(self):
        rows = [row for row in self.records if row["case_id"] == "ru-short" and row["repetition"] == 1]
        with self.assertRaisesRegex(ValueError, "three"):
            self.prepare(rows, repetitions=1)
        with self.assertRaisesRegex(ValueError, "limitation"):
            self.prepare(rows, repetitions=1, pilot=True)
        directory = self.prepare(rows, repetitions=1, pilot=True, limitation="One fixture case; no quality claim")
        self.assertTrue(mod.read(directory / "private-mapping.json")["pilot"])

    def exploratory_records(self, settings=None):
        self.manifest["model"] = None
        self.manifest["settings"] = settings
        self.manifest["observed_host_configuration"] = "Same inherited host configuration; model identifier and sampling settings not exposed; cases share a batched context."
        keys = ("model", "settings", "tools", "base_instructions_sha256", "observed_host_configuration")
        for row in self.records:
            row["metadata"] = {key: copy.deepcopy(self.manifest[key]) for key in keys}
        return copy.deepcopy(self.records)

    def test_full_run_and_regular_pilot_reject_unknown_configuration(self):
        rows = self.exploratory_records()
        for options in ({}, {"pilot": True, "limitation": "Unknown model"}):
            with self.subTest(options=options), self.assertRaisesRegex(ValueError, "observed model"):
                self.prepare(rows, **options)
        self.manifest["model"] = "synthetic-test-fixture"
        self.manifest["settings"] = {"seed": None}
        with self.assertRaisesRegex(ValueError, "Unknown generation"):
            self.prepare(rows)

    def test_exploratory_requires_pilot_observation_and_limitation(self):
        rows = self.exploratory_records()
        with self.assertRaisesRegex(ValueError, "only with --pilot"):
            self.prepare(rows, exploratory=True)
        with self.assertRaisesRegex(ValueError, "limitation"):
            self.prepare(rows, exploratory=True, pilot=True)
        del self.manifest["observed_host_configuration"]
        with self.assertRaisesRegex(ValueError, "observed_host_configuration"):
            self.prepare(rows, exploratory=True, pilot=True, limitation="Unavailable sampling")

    def test_exploratory_records_unknowns_and_report_limitations(self):
        rows = self.exploratory_records({"seed": None, "sampling": None, "context_mode": "batched"})
        directory = self.prepare(rows, exploratory=True, pilot=True, limitation="Batched cases; identifiers and sampling unavailable")
        mapping = mod.read(directory / "private-mapping.json")
        self.assertTrue(mapping["exploratory"])
        self.assertEqual(set(mapping["unknown_generation_fields"]), {"generation.model", "generation.settings.seed", "generation.settings.sampling"})
        packet_path, judgments_path, lock_path = directory / "packets.json", directory / "judgments.json", directory / "lock.json"
        mod.write_new(judgments_path, self.judgments(directory))
        mod.lock_judgments(packet_path, judgments_path, lock_path)
        result = mod.score(packet_path, judgments_path, directory / "private-mapping.json", lock_path, directory / "results.json")
        self.assertEqual(result["comparison_type"], "exploratory editorial pilot")
        self.assertTrue(result["exploratory"])
        self.assertTrue(any("not a controlled comparison" in text for text in result["limitations"]))
        self.assertNotIn("observed_host_configuration", (directory / "packets.json").read_text())

    def test_unknown_base_hash_only_allowed_in_exploratory_pilot(self):
        self.manifest["base_instructions_sha256"] = None
        for row in self.records:
            row["metadata"]["base_instructions_sha256"] = None
        for options in ({}, {"pilot": True, "limitation": "Hidden base instructions"}):
            with self.subTest(options=options), self.assertRaisesRegex(ValueError, "Unknown generation"):
                self.prepare(**options)
        self.manifest["observed_host_configuration"] = "Inherited instructions are inaccessible; visible request wrappers have condition-specific artifact paths."
        for row in self.records:
            row["metadata"]["observed_host_configuration"] = self.manifest["observed_host_configuration"]
        directory = self.prepare(exploratory=True, pilot=True, limitation="Complete inherited base inaccessible; wrappers differ in condition artifact paths")
        mapping = mod.read(directory / "private-mapping.json")
        self.assertIn("generation.base_instructions_sha256", mapping["unknown_generation_fields"])
        self.assertIsNone(mapping["manifest"]["base_instructions_sha256"])

    def test_exploratory_never_relaxes_actual_skill_or_prompt_hashes(self):
        rows = self.exploratory_records()
        for key in ("skill_sha256", "prompts_sha256"):
            original = self.manifest[key]
            self.manifest[key] = None
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "Invalid"):
                self.prepare(rows, exploratory=True, pilot=True, limitation="Model unavailable")
            self.manifest[key] = original

    def test_exploratory_cannot_hide_asymmetric_unknowns_or_observed_changes(self):
        rows = self.exploratory_records({"seed": None, "context_mode": "batched"})
        for field, value in (("model", "different-model"), ("settings", {"seed": 7, "context_mode": "batched"}), ("observed_host_configuration", "Different host configuration")):
            changed = copy.deepcopy(rows)
            changed[0]["metadata"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "identical"):
                self.prepare(changed, exploratory=True, pilot=True, limitation="Unknown sampling")

    def test_unknown_strings_and_type_mismatch_are_not_silently_equal(self):
        self.manifest["settings"]["seed"] = "unknown"
        with self.assertRaisesRegex(ValueError, "null"):
            self.prepare()
        del self.manifest["settings"]["seed"]
        rows = copy.deepcopy(self.records)
        rows[0]["metadata"]["settings"]["temperature"] = False
        with self.assertRaisesRegex(ValueError, "identical"):
            self.prepare(rows)

    def test_no_overwrite(self):
        directory = self.prepare()
        with self.assertRaises(ValueError):
            self.prepare()
        with self.assertRaises(FileExistsError):
            mod.write_new(directory / "packets.json", {})

    def test_judgment_requires_every_pair_and_anchored_scores(self):
        directory = self.prepare()
        packet = mod.read(directory / "packets.json")
        rows = self.judgments(directory)
        with self.assertRaises(ValueError):
            mod.validate_judgments(packet, rows[:-1])
        rows[0]["scores"]["A"]["dimensions"]["terms"] = 7
        with self.assertRaisesRegex(ValueError, "Dimensions"):
            mod.validate_judgments(packet, rows)

    def test_semantic_failure_cannot_win_or_hide_in_tie(self):
        directory = self.prepare()
        packet, rows = mod.read(directory / "packets.json"), self.judgments(directory)
        rows[0]["scores"]["A"]["semantic_pass"] = False
        for preference in ("A", "tie"):
            rows[0]["preference"] = preference
            with self.subTest(preference=preference), self.assertRaises(ValueError):
                mod.validate_judgments(packet, rows)
        rows[0]["preference"] = "B"
        mod.validate_judgments(packet, rows)
        rows[0]["scores"]["B"]["semantic_pass"] = False
        rows[0]["preference"] = "tie"
        mod.validate_judgments(packet, rows)

    def test_locked_aggregate_reports_regressions_and_replicates(self):
        directory = self.prepare()
        packet_path = directory / "packets.json"
        rows = self.judgments(directory)
        mapping = mod.read(directory / "private-mapping.json")
        first = mapping["mapping"][rows[0]["pair_id"]]
        skill_label = next(label for label, condition in first["labels"].items() if condition == "skill")
        baseline_label = "B" if skill_label == "A" else "A"
        rows[0]["scores"][skill_label]["semantic_pass"] = False
        rows[0]["preference"] = baseline_label
        judgments_path, lock_path = directory / "judgments.json", directory / "lock.json"
        mod.write_new(judgments_path, rows)
        mod.lock_judgments(packet_path, judgments_path, lock_path)
        result = mod.score(packet_path, judgments_path, directory / "private-mapping.json", lock_path, directory / "results.json")
        self.assertEqual(result["overall"], {"skill": 0, "baseline": 1, "tie": 5})
        self.assertEqual(result["semantic_regressions"], 1)
        self.assertEqual(result["by_case"][first["case_id"]]["semantic_regressions"], 1)
        self.assertEqual(set(result["by_repetition"]), {"1", "2", "3"})
        judgments_path.write_text(json.dumps(rows) + " ", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed after locking"):
            mod.score(packet_path, judgments_path, directory / "private-mapping.json", lock_path, directory / "other.json")

    def test_invalid_private_mapping_rejected(self):
        directory = self.prepare()
        rows = self.judgments(directory)
        judgment_path, lock_path = directory / "judgments.json", directory / "lock.json"
        mod.write_new(judgment_path, rows)
        mod.lock_judgments(directory / "packets.json", judgment_path, lock_path)
        mapping_path = directory / "private-mapping.json"
        mapping = mod.read(mapping_path)
        identities = list(mapping["mapping"].values())
        identities[1]["case_id"], identities[1]["repetition"] = identities[0]["case_id"], identities[0]["repetition"]
        mapping_path.write_text(json.dumps(mapping), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate private"):
            mod.score(directory / "packets.json", judgment_path, mapping_path, lock_path, directory / "results.json")


if __name__ == "__main__":
    unittest.main()
