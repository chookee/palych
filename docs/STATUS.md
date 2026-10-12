# Palych — development status

## 0.6.0 candidate: compact replies

The revised core prioritizes compactness and clarity through task-specific reply
construction, single representations, necessary detail and a concrete stop rule.
It also checks supported causes, universal claims and implementation assumptions.
See [design and verification scope](COMPACT-REPLIES.md).

Original RU/EN examples and separate regression sets are included.
The previous prompt set and historical result files remain unchanged. Reader
comprehension tests have not been performed; model pilots are recorded below.
An exploratory one-response-per-case Claude Code pilot was performed on the
earlier candidate. It showed shorter replies but automatic judgments missed
content and language errors. The core and assessor rubric were revised from the
source audit; repeat runs are recorded separately by tested core hash.
These results do not establish reader comprehension or universal compliance.
The source revision does not update personal installations or establish live
hook delivery. This candidate is not yet published to main.

## Shorter-core pilot in progress — 2026-10-12

The draft runtime core is 762 words (5938 bytes), down from 1048 words (7628
bytes). Runtime constraints remain self-contained. Installer tests cover both
optional-pointer layouts and required final self-check retention; 35
installer/adapter/builder tests and 17 blind-tool tests passed. Both plugins built.

The fixed plan contains 12 new RU/EN tasks plus the four existing RU/EN cache-cost
and detailed-process tasks, two fresh replies per condition: 64 replies and
eight masked assessor sessions. Current and candidate controls are both fresh.
The total limit is 75 logical model requests, including at most three manual
transient retries. Two repetitions and unexposed provider/sampling fields make
this an exploratory editorial pilot, not a full controlled run or reader test.

56 replies were saved. One subsequent turn lost its stream, attempted native
reconnections, fell back to HTTPS and timed out without a completed reply. Its
usage is unknown. Relaunching the isolated process was blocked twice because
automatic permission review did not finish before its deadline. The restricted
environment also refused nested sandbox setup. Eight replies and all eight
assessor sessions remain. No quality verdict, input/output savings claim or
keep decision has been made. Native transport reconnections are distinct from
the logical request limit and may have unexposed consumption.

Draft core SHA-256:
`74c8fe86b0d083f1799d3d020f71d0ea2429688b4fdbeddbc766027fa5cd548a`.
The earlier actual-compaction result below tested the preceding core, not this
draft. Main and personal installations remain unchanged. Raw replies and the
bounded continuation command are retained outside the public package.

## Focused Codex follow-up — 2026-10-12

The comparison rule was tested on `gpt-6.1-sol`, medium effort, with six new
RU/EN prompts and three fresh replies per condition. All 18 masked pairs tied;
both cores preserved the requested values. In the 12 full comparisons per core,
the conclusion preceded the table in 10 candidate replies versus 3 controls.
All six candidate choice-only replies retained the requested two-sentence form.

Twenty further candidate replies were compared with saved current-core controls.
The known English seven-plan omission was repaired; one Russian cache explanation
had more avoidable detail. No new semantic regressions were found by the masked
assessor or the subsequent unblinded source audit. Reused controls and unavailable
provider settings limit causal conclusions; this does not establish an overall
compactness improvement or reader comprehension.

Two eight-turn Codex conversations completed actual manual compaction after turn
six. The candidate core was supplied once through developer instructions; it was
not reinjected. Post-compaction replies retained the memo's exact deadline,
timezone, file-size boundary and failed-check prohibition. RU/EN switching and
the one-word override worked. This tests the injected core in a short conversation,
not personal installation, global-instructions loading, plugin hooks or automatic
compaction near the context limit.

In those conversations, the candidate's reported input tokens were 27.1% higher
and output tokens 7.8% higher than the no-skill control. Cached input varied;
subscription debit and separately attributable compaction consumption were not
measured. Loading the core once does not remove its cost in later input contexts.
Candidate core SHA-256:
`e3ad8877c3028afc6d422686a2b46fd166a32a6ee6118d37fa47f5a9fd0185dc`.
Raw host logs and model replies remain outside the public package.

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
