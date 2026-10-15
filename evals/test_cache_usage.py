"""Tests for the prompt-cache estimate; all logs are synthetic."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("cache_usage", Path(__file__).with_name("cache_usage.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def claude_record(request_id, cached, written, uncached, model="claude-sonnet-5-5", ttl="1h", **extra):
    usage = {"cache_read_input_tokens": cached, "cache_creation_input_tokens": written,
             "input_tokens": uncached, "output_tokens": 10,
             "cache_creation": {f"ephemeral_{ttl}_input_tokens": written}}
    return {"type": "assistant", "requestId": request_id, "message": {"model": model, "usage": usage}, **extra}


class CacheUsageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, records):
        path = self.root / name
        path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
        return path

    def test_claude_parser_dedupes_and_skips_side_threads(self):
        path = self.write("session.jsonl", [
            claude_record("a", 1000, 3000, 5),
            claude_record("a", 1000, 3000, 5),
            claude_record("b", 4000, 200, 5, isSidechain=True),
            claude_record("c", 0, 0, 0, model="<synthetic>"),
            claude_record("d", 4000, 200, 5, model="claude-opus-5-5"),
        ])
        requests = mod.claude_requests(path)
        self.assertEqual([r["total"] for r in requests], [4005, 4205])
        self.assertEqual([r["read"] for r in requests], [0.1, 0.05])
        self.assertEqual(requests[0]["ttl"], "1h")

    def test_classify_against_first_request(self):
        first = {"cached": 1000, "total": 4000}
        later = [{"cached": 4500}, {"cached": 900}, {"cached": 2500}]
        self.assertEqual(mod.classify([first, *later]), ["first", "warm", "cold", "ambiguous"])

    def test_summarize_bounds(self):
        requests = [{"cached": 1000, "total": 4000, "ttl": "1h", "read": 0.1, "output": 10},
                    {"cached": 4000, "total": 4100, "ttl": "1h", "read": 0.1, "output": 10},
                    {"cached": 2000, "total": 4200, "ttl": "5m", "read": 0.1, "output": 10}]
        result = mod.summarize([requests])
        self.assertEqual(result["classes"], {"first": 1, "warm": 1, "cold": 0, "ambiguous": 1})
        self.assertAlmostEqual(result["core_multiplier_low"], round((2.0 + 0.1 + 0.1) / 3, 3))
        self.assertAlmostEqual(result["core_multiplier_high"], round((2.0 + 0.1 + 1.25) / 3, 3))

    def test_codex_parser_skips_repeated_totals(self):
        def event(cached, total):
            usage = {"input_tokens": 5000, "cached_input_tokens": cached, "output_tokens": 7}
            return {"type": "event_msg", "payload": {"type": "token_count", "info": {
                "last_token_usage": usage, "total_token_usage": {"input_tokens": total}}}}
        path = self.write("rollout-1.jsonl", [event(0, 5000), event(0, 5000), event(4800, 10000)])
        requests = mod.codex_requests(path)
        self.assertEqual([r["cached"] for r in requests], [0, 4800])
        self.assertEqual(mod.summarize([requests], read=0.1)["classes"]["warm"], 0)


if __name__ == "__main__":
    unittest.main()
