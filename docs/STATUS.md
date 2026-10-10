# Palych 0.4.0 — development status

Russian is the primary language; English is supported. The compact standalone
skill and optional Codex/Claude Code plugin builder are ready.

The rebrand changes identifiers, commands and the state namespace. The original
semantic rules and earlier synthetic evidence are retained. Local verification
covers package structure, JSON, links, adapter persistence/deduplication and the
blind-evaluation helper. See [development commands](DEVELOPMENT.md).

Still open:

- Reader comprehension testing with the intended audience.
- Real host installation/trust/event-delivery checks after actual compaction.
- The complete controlled 20-case, three-repetition comparison with observed
  matching generation settings.
- Actual platform token/usage-limit measurements.

Earlier masked and editorial pilots are described in
[historical observations](../evals/observations.md). Their limits remain in force.
Static counts in [token-usage.md](../evals/token-usage.md) describe Clear Replies
0.3.0 before the rename. They are not subscription savings or new-name counts.

Publication does not install the skill into a personal environment.

## Local verification for this publication

25 adapter/builder tests and 17 blind-tool tests passed. The standalone checker
validated 42 files. Both generated host plugins passed synthetic enable, repeated
enable, compact, disable and compact events. This does not establish live-host
event delivery. Core SHA-256: `6f365654c9f23997c2c66b3df1816cddd9754ce64c89b8cfcc2dc7e40e8d78ae`.

No CI workflow or personal installation is configured by this publication.
