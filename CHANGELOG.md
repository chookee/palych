# Changelog

## 0.5.0 — 2026-10-11

- Make always-on the normal installation for Codex and Claude Code: generate the
  runtime rules into global instructions, without a separate skill call.
- Preserve other instructions, back up changed files, update without duplication,
  and remove only the managed block. Respect existing Codex global overrides.
- Default new hook-plugin state to on. Retain saved off states and avoid repeating
  the full core on ordinary turns; restore it at context boundaries.
- Rewrite both READMEs with an agent install prompt, example and main principles.
  Introduce the namesake as А.П. Чехов.
- Add isolated installer checks. Live-host loading and compaction remain unverified.

## 0.4.0 — 2026-10-10

- Publish the independent Palych repository; Russian display name: Палыч.
- Name chosen in honor of Anton Pavlovich Chekhov.
- Rename the runtime skill, plugin manifests, helper messages, commands and state
  directory from clear-replies to palych.
- Add natural Russian commands such as “Включи Палыча” and “Отключи Палыча”.
- Add standalone development, provenance, status and package-check documentation.
- Preserve the original MIT notice and all historical evaluation evidence.

## Before the independent repository

Clear Replies 0.3.0 compacted the core and hook payloads; 0.2.0 introduced the
optional state adapter and masked-evaluation tools. Historical measurements and
limitations remain under evals/. They are not new evaluations of this release.
