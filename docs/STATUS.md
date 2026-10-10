# Palych 0.5.0 — development status

The default installation now adds Palych's runtime rules to Codex or Claude Code
user instructions. This makes the rules available from the first reply without
an explicit skill invocation. See [INSTALL.md](../INSTALL.md).

The plugin route is an alternative: fresh state defaults to on, saved off states
survive upgrades, and the core is restored at SessionStart boundaries. Ordinary
prompts do not repeat the core. Use one route at a time.

## Local verification

34 installer/adapter/builder tests and 17 blind-tool tests passed. Installer tests
use temporary configuration directories, including both hosts, custom paths,
Codex global overrides, exact preservation of existing bytes, backups, idempotent
updates, removal, refusal of edited/linked instructions and failed atomic writes.
Hook tests cover startup without activation, compact/resume/clear/fork restoration,
saved off overrides, existing off defaults, deduplication and unchanged ordinary
prompts. These tests do not establish live-host event delivery or model behavior.

The offline package checker validated 45 source files: frontmatter, JSON, links
and absence of private machine paths. Both plugin variants are built from the
same source. Core SHA-256: `d1ef198edc671d249b138a3771bd8b6f9be857155b3bf5f7a0ff0109fd717ce1`.

## Still open

- Actual host loading, instruction-size limits and mode retention after real
  compaction. Global instructions shape behavior; they are not enforced settings.
- Reader comprehension testing with the intended audience.
- The complete controlled 20-case, three-repetition comparison with observed
  matching generation settings.
- Actual platform token/usage-limit measurements. Keeping one runtime block and
  avoiding repeated hook injection prevents duplicates; it does not establish
  subscription savings or eliminate repeated input-context costs.

Earlier masked and editorial pilots are described in
[historical observations](../evals/observations.md). Their limits remain in force.
Static counts in [token-usage.md](../evals/token-usage.md) describe Clear Replies
0.3.0 before the rename. Historical evidence is unchanged.

Developing and publishing an installer does not install Palych into personal
agent environments. No personal settings were changed for these tests.
