# Palych development

This file governs development, not installation or reply style. For an owner
request to install Palych, follow `INSTALL.md` and the owner's existing installation
workflow. Runtime instructions are in `skills/palych/SKILL.md`.

- The standalone skill in `skills/palych/` is the canonical source; keep the
  repository root free of SKILL.md, because skill installers copy the whole folder
  of the first SKILL.md they find. Host packages under `packages/`
  and the plugin catalogs are generated from it and committed (catalogs
  must point at published Git paths). Never edit them by hand: change the source,
  run `python3 scripts/build_packages.py` and commit both. The package check
  fails when a generated file differs from the source.
- The core needs no tools or other skills. Keep runtime instructions
  self-contained and references optional.
- Run these checks from the repository root:
  `python3 scripts/check_package.py`,
  `python3 -m unittest discover -s adapters -p 'test_*.py'`,
  `python3 -m unittest discover -s evals -p 'test_*.py'`.
- Historical files in `evals/results`, `observations.md` and `token-usage.md` describe
  Clear Replies before the rename. Keep their raw contents and hashes intact;
  record new evidence separately with the tested revision or skill hash.
- Never report an editorial score as reader comprehension or a fixture event as
  successful live-host compaction. Current limitations are in `docs/STATUS.md`;
  dated records go to `docs/history/STATUS-LOG.md`.
- For releases, update the builder's manifest version and `CHANGELOG.md`, run the
  checks, build both host variants into new directories and verify their contents.
  Installation, live evaluations and publication have separate authorization.
