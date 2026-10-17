"""Tests for the session reply comparison; all transcripts are synthetic."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("session_replies", Path(__file__).with_name("session_replies.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def user(text, **extra):
    return {"type": "user", "timestamp": "2026-10-14T10:00:00Z", "cwd": "/w", "message": {"content": text}, **extra}


def assistant(request_id, parts, output=10, model="claude-opus-5-5", **extra):
    return {"type": "assistant", "requestId": request_id,
            "message": {"model": model, "content": parts, "usage": {"output_tokens": output}}, **extra}


def text(value):
    return {"type": "text", "text": value}


class SessionRepliesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def write(self, records):
        path = Path(self.temp.name) / "session.jsonl"
        path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
        return path

    def test_turns_skip_injected_prompts_and_count_requests_once(self):
        path = self.write([
            user("Почини тест"),
            assistant("a", [text("Смотрю.")], output=5),
            assistant("a", [{"type": "tool_use", "name": "Bash"}], output=5),
            user([{"type": "tool_result", "content": "ok"}]),
            user("<system-reminder>x</system-reminder>"),
            user("injected", isMeta=True),
            assistant("b", [text("Готово, тест проходит.")], output=7),
            assistant("c", [text("side")], isSidechain=True),
            user("Thanks"),
            assistant("d", [{"type": "tool_use", "name": "Read"}]),
        ])
        start, cwd, turns = mod.session_turns(path)
        self.assertEqual((start, cwd), ("2026-10-14T10:00:00Z", "/w"))
        self.assertEqual(len(turns), 1)  # the last turn has no visible text
        turn = turns[0]
        self.assertTrue(turn["russian"])
        self.assertEqual(turn["messages"], 2)
        self.assertEqual(turn["final"], len("Готово, тест проходит."))
        self.assertEqual(turn["visible"], len("Смотрю.") + len("Готово, тест проходит."))
        self.assertEqual(turn["output"], 12)

    def test_slash_chains_ignore_code_paths_and_urls(self):
        chains, words = mod.slash_chains(
            "ключи/сеть and result/effect; `a/b` docs/STATUS.md https://x.io/a/b ~/repos/palych и/или")
        self.assertEqual(chains, 2)
        self.assertGreater(words, 0)

    def test_interval_resamples_sessions(self):
        before = [[{"visible": 100}], [{"visible": 120}]]
        after = [[{"visible": 50}], [{"visible": 60}]]
        low, high = mod.median_diff_interval(before, after, "visible", draws=200)
        self.assertLess(high, 0)
        self.assertLessEqual(low, high)


if __name__ == "__main__":
    unittest.main()
