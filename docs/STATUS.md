# Palych — development status

## 0.6.0 candidate: compact replies

The revised core prioritizes compactness and clarity through task-specific reply
construction, single representations, necessary detail and a concrete stop rule.
It also checks supported causes, universal claims and implementation assumptions.
See [design and verification scope](COMPACT-REPLIES.md).

Original RU/EN examples and a separate 20-case regression set are included.
The previous prompt set and historical result files remain unchanged. New
controlled generation and reader comprehension tests have not been performed.
An exploratory one-response-per-case Claude Code pilot was performed on the
earlier candidate. It showed shorter replies but automatic judgments missed
content and language errors. The core and assessor rubric were revised from the
source audit; repeat runs are recorded separately by tested core hash.
These results do not establish reader comprehension or universal compliance.
The source revision does not update personal installations or establish live
hook delivery. This candidate is not yet published to main.

## 0.5.0 installation and verification history

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
