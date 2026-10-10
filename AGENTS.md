# Palych development

This file governs development, not installation or reply style. For an owner
request to install Palych, follow INSTALL.md and the owner's existing installation
workflow. Runtime instructions are in SKILL.md.

- The standalone skill is the canonical source. Generated Codex/Claude Code
  plugins are build artifacts; change the source and rebuild.
- The adapter supports macOS/Linux and Python 3.9+. The core needs no tools or
  other skills. Keep runtime instructions self-contained and references optional.
- Run these checks from the repository root:
  `python3 scripts/check_package.py`
  `python3 -m unittest discover -s adapters -p 'test_*.py'`
  `python3 -m unittest discover -s evals -p 'test_*.py'`
- Historical files in evals/results, observations.md and token-usage.md describe
  Clear Replies before the rename. Keep their raw contents and hashes intact;
  record new evidence separately with the tested revision or skill hash.
- Never report an editorial score as reader comprehension or a fixture event as
  successful live-host compaction. Current limitations are in docs/STATUS.md.
- For releases, update the builder's manifest version and CHANGELOG.md, run the
  checks, build both host variants into new directories and verify their contents.
  Installation, live evaluations and publication have separate authorization.
- This is a skill package, without a service deployment. No automatic sync from
  another repository; future implementation belongs here.
