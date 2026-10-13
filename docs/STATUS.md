# Palych — development status

## Palych versus no skill; combined rules — 2026-10-13

Exploratory masked pilots on `claude-sonnet-5-5` (effort medium, isolated Claude Code
2.1.287 subscription sessions, same-model assessors, judgments locked before
unblinding). Reader comprehension was not tested.

No skill versus `main` 466fb77 (SHA-256 `3b176dce…a6828`): 30 RU/EN cases from the
compact, bounds/conflicts and reassurance sets, three fresh replies per condition,
180 replies and 15 assessor sessions. Locked results: 86 Palych preferences, 1
no-skill preference, 3 ties. Semantic failures: 45 without Palych, 3 with it; one
Palych regression (`en-depth`, an unsupported "cannot be undone" claim). Palych
replies were 45.4% fewer output tokens and 47.9% fewer characters, in both languages.
Input tokens rose by about 2600 per request because the core is sent each time;
cached-input pricing and subscription debits were not measured.

Combined rules: the pre-merge core (`eba7a41f…efc92`) versus `main` on eight cases
with earlier failures (unknown-reason, deadline, conflict, optional-backup; RU/EN),
three replies each. The `main` replies were reused from the no-skill pilot. Locked
results: 13 `main`, 4 pre-merge, 7 ties; semantic failures 12 versus 4. The pre-merge
core chose one conflicting term in 5 of 6 conflict replies, `main` in none. All three
`main` regressions are in `optional-backup`, where "the app works without it" persists.

## Actors, promises and next steps — 2026-10-13

After the no-reassurance pilot, one clause was added: do not add actors, promises
or next steps the source does not state (1100 → 1113 words), SHA-256
`5161ced213ad40e116ffe7a4a56c4780f9428b1bc089e34d7619af942e3c9bd5`. It targets the
remaining candidate failures: an invented "developers will not require it" and an
added "fix the problem before trying again".

A focused three-repetition exploratory pilot on unknown-reason and deadline (RU/EN,
24 fresh replies, two same-model assessor sessions, locked before unblinding) gave
5 candidate preferences, 4 current-core preferences and 3 ties. The assessor marked
1 current and 3 candidate failures; the source audit confirms two candidate failures
(an invented "developers" subject, an added "ask the organizers") and treats the
literal reading of "before 09:40" as an assessor error. Both cores wrote "fix the
problem and pass the check first". The clause showed no measurable effect on the
targeted additions. Input tokens +1.79%, output −4.82%, characters −5.22%.
The clause was removed; the core returns to the tested no-reassurance version,
SHA-256 `adaa8b2c40d8e0224166adfc568c4a4ca8b7cdda16a030d8c613c35709011d0c`.

## No-reassurance candidate prepared — 2026-10-12

In both 2026-10-12 Claude pilots, both cores sometimes turned an optional update into
a guarantee ("nothing will break", "you can safely skip it") despite the existing
rule. The candidate restates the rule with these surface forms (1082 → 1100 words), SHA-256
`adaa8b2c40d8e0224166adfc568c4a4ca8b7cdda16a030d8c613c35709011d0c`.
Original example lines and a four-case [reassurance set](../evals/reassurance-prompts.json)
were added.

A three-repetition exploratory masked pilot on `claude-sonnet-5-5` (effort medium,
isolated Claude Code 2.1.287 subscription sessions) used the four focused cases,
unknown-reason, and roles/deadline/conflict guards in RU and EN: 72 fresh replies,
six same-model assessor sessions, judgments locked before unblinding. Locked results:
19 candidate preferences, 7 current-core preferences, 10 ties. Semantic failures:
13 current, 5 candidate, including 4 candidate regressions.

In the 18 targeted replies the current core added an unsupported reassurance 8 times,
the candidate once. Candidate regressions: an invented "developers will not require
it" actor and promise (`ru-unknown-reason`, twice), "the device will keep working"
(`ru-optional-backup`), an added "fix or ask before trying again" (`en-deadline`).
The assessor passed similar current-core phrases, so the regressions partly reflect
assessor inconsistency; the invented actor appears only in candidate replies.
The fixed semantic gate is formally not met. Input tokens +1.17%, output +2.28%,
answer characters +1.66%. Reader comprehension untested.

## Narrowed bounds/conflicts candidate — 2026-10-12

After the failed pilot only one rule was kept: keep "from", "at least" and
"more than" bounds, and name conflicting supplied facts instead of choosing one.
The other candidate rules, examples and documentation were reverted to `main`.
The core grows from 1082 to 1100 words, SHA-256 `bba312add40b81cd0727f40d3f5de7e207163e21973a09ea1d83d7a657cebaa8`.
An eight-case [bounds and conflicts set](../evals/bounds-conflicts-prompts.json)
was added.

A three-repetition exploratory masked pilot on `claude-sonnet-5-5` (effort medium,
isolated Claude Code 2.1.287 subscription sessions) used the eight focused cases and
six guards (unknown-reason, roles, deadline): 84 fresh replies, seven same-model
assessor sessions, judgments locked before unblinding. Locked results: 16 candidate
preferences, 9 current-core preferences, 17 ties. Semantic failures: 6 current,
2 candidate. The current core chose one conflicting delivery term or price in 5 of
12 conflict replies; the candidate chose none. Both cores kept every bound.

Both candidate failures are guard regressions of a pre-existing type: an unsupported
"nothing will break" guarantee (`ru-unknown-reason`, which the current core produced
in the previous pilot) and an added "fix the problem first" instruction
(`en-deadline`). The fixed semantic gate is formally not met; integration is the
owner's decision. Input tokens +1.30%, output tokens +2.75%, answer characters
+6.34%, mostly where the candidate explains a conflict. Reader comprehension untested.

## Empty-moves pilot: semantic gate failed — 2026-10-12

An exploratory masked pilot compared the current core (SHA-256 `eba7a41f…efc92`)
with the candidate (`e6990d03…22245`) on `claude-sonnet-5-5`, effort medium, through
an isolated Claude Code 2.1.287 subscription session. 32 cases (12 empty-moves,
20 compact) received one fresh reply per core: 64 processes with empty tools, MCP,
skills and hooks. Eight fresh same-model assessor sessions judged masked pairs;
judgments were locked before unblinding. One batch was re-judged before unblinding
after violating the protocol; 16 calls were rejected by an item-count schema error.

Locked results: 13 candidate preferences, 10 current-core preferences, 9 ties.
Semantic failures: 3 current, 2 candidate; both candidate failures are regressions.
`en-unknown-reason` promised unchanged behavior; `ru-roles` added a direct route as
"not through the buffer". The current core picked one conflicting delivery term in
`en-conflict`; the candidate named the conflict. A separate unblinded source audit
confirmed all five failures and found two borderline candidate statements.

Input tokens rose 6.84% (103449 → 110527) and output tokens 2.13%; answer characters
fell 2.21%. Neither core produced grading labels or manner praise, so the run shows
no measurable benefit from the empty-moves rule. The fixed semantic gate failed:
the candidate is not ready for integration. Reader comprehension was not tested.

## Empty-moves candidate prepared — 2026-10-12

Several public Russian editing skills were reviewed for principles; no text or
code from them is bundled. The candidate adds about 100 words to the core
(1082 → 1182): it removes empty rhetorical moves, keeps causal and contrast links
when shortening, replaces unsupported evaluations with facts, names failures
plainly, keeps lower bounds and "more than" conditions, and names conflicting
supplied facts. Rejected ideas included mandatory output blocks, scores, required
numbers, minimum lengths, fixed paragraph sizes and automatic rounding.

Original RU/EN examples and a 12-case [empty-moves set](../evals/empty-moves-prompts.json)
support the change. No model run was made; shorter replies, token savings and
reader comprehension are not established. A paired blind run of the current and
candidate cores is the next step. Candidate SKILL.md SHA-256:
`e6990d032eb06ed47110573becc6eecdf685c850c871d3a2472beed7e9522245`.

## 0.6.0: compact replies

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
hook delivery. Released as 0.6.0 on 2026-10-13; the release does not establish
model or reader validation.

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
75-request pilot does not validate these changes. Source integration does not
update personal installations; reader comprehension and fresh model evaluation
are pending.

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
