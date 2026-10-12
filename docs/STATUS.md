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

## Repetition candidate prepared — 2026-10-12

The owner supplied a human-preferred edit of one Russian publication explanation
and identified missing brevity, repeated meanings/terms and overused colon links.
This is specific reader editorial feedback, not a blinded comparison or evidence
of improved comprehension across readers.

The next candidate is a narrow revision of the restored 1048-word core. It merges
semantic duplicates, joins a step's action and purpose, lets a heading carry a
complete step, and removes previews/recaps that add no information. Pronouns or
ellipsis reduce nearby noun echoes only when unambiguous; terminology stays stable.
Ordinary sentence links prefer full stops/conjunctions, keeping useful colons.

The meaning-preservation, agent-work and activation sections are byte-for-byte
unchanged. No broad compression of the accuracy rules was repeated. Original
RU/EN examples and a focused repetition set support the new rules. The core
grew from 1048 to 1082 words; shorter generated replies or token savings have not
been established. No new model calls were made for this candidate. The preceding
75-request pilot does not validate these changes. Main and personal installation
remain unchanged; reader comprehension and fresh model evaluation are pending.

## Shorter-core pilot completed; candidate rejected — 2026-10-12

A 762-word candidate (5938 bytes) was compared with the current 1048-word core
(7628 bytes) on `gpt-6.1-sol`, medium effort, default tier. Twelve new RU/EN tasks
plus the four existing cache-cost and detailed-process tasks were repeated twice
per condition: 64 fresh replies in distinct threads. Neither control was reused.
Local instruction sources, other skills and tool use were excluded and verified;
hidden provider instructions and sampling settings remain unavailable. Generation
was interrupted and resumed, so hidden provider state across the pause is unknown.

Eight fresh assessor sessions judged 32 masked pairs before the mapping was
opened. Locked results: 4 candidate preferences, 1 current-core preference and
27 ties; the assessor found one candidate semantic regression. The subsequent
unblinded source audit confirmed it and found the same unsupported author-to-editor
handoff in the second Russian publication reply. A third candidate reply assigned
an unprovided handoff to the request sender. The audit also found an unsupported
return-action actor in one current-core English publication reply. These findings
are separate from the unchanged locked judgments; neither measures human reading.

Candidate input tokens were 202297 versus 212025 (-4.59%); reported output tokens
5142 versus 5697 (-9.74%). RU output -13.53%, EN output -4.68%. Answer characters
fell 10.17%. Each candidate input was 304 tokens smaller. Cached input varied and
is included in input totals; subscription debit, failed-turn usage and native
transport retry consumption were not measured. Savings do not override a meaning
failure or establish that compression caused the errors.

The fixed semantic gate failed: the candidate was rejected and the original core
restored, SHA-256
`e3ad8877c3028afc6d422686a2b46fd166a32a6ee6118d37fa47f5a9fd0185dc`.
The rejected candidate remains recoverable in history and separate evidence,
SHA-256 `74c8fe86b0d083f1799d3d020f71d0ea2429688b4fdbeddbc766027fa5cd548a`.
Installer compatibility, heading-independent tests and the 12 new fixtures remain.

Exactly 75 logical model requests were logged: 64 completed replies, 8 completed
assessor sessions and 3 failed/incomplete operations (stream timeout, capacity,
usage limit), each followed by one authorized retry. Native reconnection attempts
are recorded separately and their provider count/cost is unknown. Two process
launches were blocked by permission-review timeouts; the restricted environment
also refused nested sandbox setup. A narrower reviewed launch succeeded, then
usage-limit recovery was resumed at the owner's request. The total cap did not
change; a send guard refuses request 76. All jobs completed; no further runs.

35 installer/adapter/builder tests and 17 blind-tool tests passed before the live
pilot. The final restored package is verified separately. Runtime hooks, automatic
compaction and reader comprehension were not retested here. Main and personal
installations remain unchanged; raw host logs remain outside the public package.

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
