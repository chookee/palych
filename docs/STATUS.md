# Palych — current status

This page holds the current state and open limits. Dated records with commands,
versions, hashes and raw numbers are in the
[development log](history/STATUS-LOG.md); add new records there, newest first,
and update this page when a limit changes.

## Hosts

| Host | Route | Checked | Not checked |
|---|---|---|---|
| Claude Code | Plugin with a SessionStart hook, or a global instructions block | Plugin install, update 0.6.0 → 0.6.1, reinstall; core on startup, resume, clear, compact; off survives compaction (live, 2026-10-14) | Global-block route live; progress messages |
| Codex CLI | Plugin with a SessionStart hook, or a global instructions block | Plugin install and reinstall; off survives compaction; no duplicate core on resume or fork (live, 2026-10-14) | Plugin upgrade from a GitHub marketplace; whether hook trust survives an update; fork in off mode or after a core change |
| Hermes | Skill folder `skills/palych`, preloaded with `hermes -s palych` | Install from `skills/palych`, scan SAFE, files identical (v0.22.0, 2026-10-15); preloading inferred from input tokens with the former `packages/hermes/palych` path (v0.16.0, v0.22.0) | Preloading from the new path; `skills.auto_load` with Palych |
| Cursor | Always-applied rule in a local plugin | Loads as a local plugin; plain off answered without tool calls (3.24.18, one run per case) | Marketplace install; the Claude Code plugin inside Cursor |
| `npx skills` | Copies `skills/palych` | Folder install and removal (skills@1.7.2) | — |

## Known limitations

- A Codex plugin loads no rules until the user trusts its hook; Codex reports no
  error. How a user persists trust outside `--dangerously-bypass-hook-trust` was
  not checked.
- Installing both the global block and a plugin loads the rules twice, and their
  mode states can conflict. The hook does not detect the global block; choose one
  route.
- Hermes and Cursor have no hooks: off lasts only for the current conversation.
- A Codex fork taken before the parent received the core gets no core; a fork
  taken before the parent was switched off inherits off.
- The core adds input tokens to every request (about 2600 in the Claude Code
  pilot). In two weeks of local agent sessions most requests read it from the
  prompt cache: it cost 0.13–0.18 of the uncached price in Claude Code and an
  estimated 0.24–0.28 in Codex. Short chats pay the cache write over fewer
  requests. Subscription usage-limit debits were not measured.

## Quality evidence

Masked pilots on `claude-sonnet-5-5` with same-model assessors (2026-10-13):
against no skill, 86 Palych preferences, 1 no-skill preference and 3 ties over
90 pairs; semantic failures 3 with Palych versus 45 without; output tokens 45.4%
lower. Still open: unknown actors and reasons, and "optional" turning into "safe
to skip" (`optional-backup`). Three candidate rules for them failed their pilots
and were not integrated.
A shorter core that merged the role and route rules failed its pilot
(2026-10-15): it reintroduced invented routes.
A bad/good example in place of the optional and reassurance rules also
failed (2026-10-15): reassurance about skipping came back.

## Still open

- Reader comprehension testing with the intended audience.
- The complete controlled 20-case, three-repetition comparison with matching
  generation settings.
- Usage-limit debits, and output savings in agent sessions with tool loops.

Editorial scores are not reader comprehension, and fixture events are not live
host behavior. Historical evidence in `evals/results`, `evals/observations.md`
and `evals/token-usage.md` describes Clear Replies before the rename and stays
unchanged.
