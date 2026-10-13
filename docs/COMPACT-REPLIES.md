# Compact replies: design of 0.6.0

## The change

The entrypoint now starts with three writing decisions: answer directly, choose
the smallest form that fits the request, keep only the detail that serves it.
Activation mechanics follow the writing rules. Nothing about loading or persistence
was moved into a required external reference.

The task forms specify content, not headings to print:

| Task | Content needed |
|---|---|
| Definition | Meaning and an essential distinction. |
| Explanation | Conclusion, mechanism and relevant limits. |
| Instructions | Necessary actions in order, with prerequisites and failure gates. |
| Comparison | Requested decision criteria and every requested option with its values. |
| Rewrite | Supplied facts and modality, with explanation only for a comprehension gap. |
| Progress/error | Result or effect, verification scope and a material gap/blocker. |
| Clarification | The missing input or decision that changes the answer. |

Each paragraph must answer part of the question, explain a needed connection or
retain a material condition. One representation normally suffices; a second earns
its space only if it adds understanding rather than repeats facts. A short answer
does not need headings. Length remains task-dependent.

## What the related skill contributed

[i-have-adhd](https://github.com/ayghri/i-have-adhd/blob/main/skills/i-have-adhd/SKILL.md)
was reread on 2026-10-11. Its explicit reply rules, suppression of tangents,
numbered bounded actions and pre-send pruning informed this structure. These are
independently written Palych rules; no upstream text or code is bundled.

Palych chooses the opening by the question rather than requiring an action.
It has no mandatory next step, status repetition, time estimate or list cap.
It assumes no diagnosis. Requested items, depth, uncertainty and real prohibitions
are retained. These distinctions preserve Palych's general conversational scope.

## Accuracy while shortening

Unknown causes remain unknown. Independent facts do not acquire a causal link
merely to make an explanation flow. Universal words need support from facts,
definitions or explicit requirements. System-specific behavior remains conditional
when the implementation is unknown. Those checks apply to added explanation,
not only to facts copied from the question.

The self-check now names both kinds of failure: unnecessary reading and unsupported
meaning. It is part of writing, without a second model, runtime tool or compulsory
reader survey. Optional examples remain optional.

## Focused compactness revision

The tested candidate combined overlapping wording, meaning and self-check rules
without moving runtime constraints behind external references. Detailed processes
pair each stage's action with its purpose, retaining loops and approval gates.
A preview and recap must not repeat the same process. Hypothetical scenarios and
unknowns earn space only when they affect interpretation, a decision or diagnosis.
Supplied uncertainty remains part of the source meaning to preserve.

The tested entrypoint was 762 words instead of 1048. It reduced observed input
and output tokens, but added unsupported process actions in Russian replies.
The semantic gate failed and the 1048-word core was restored. Candidate evidence
is retained separately; see development status for the masked and source-audit
results. This does not establish a causal effect of compression or reader benefit.

The global installer omits optional example pointers in both supported layouts:
the legacy `## Optional examples` section and the compact trailing pointer beginning
`Consult only relevant optional`. Preserve that boundary when changing the pointer.
Installation tests verify full required content and the final runtime check,
without depending on the prose heading for semantic preservation.

## Reader-informed repetition candidate

After rejecting the shorter core, the owner supplied a preferred human edit of
one process explanation. The next revision targets repeated meaning, noun echoes
and habitual colon links in the restored core. It does not copy the supplied
private example into public resources or broaden the claim into reader validation.
All added public examples are independently written for the package.

A heading may state the whole step; following text earns its place by adding a
purpose, condition or explanation. An overview can orient the reader, but needs
no repeated recap. Pronouns and ellipsis can reduce noun echoes when their referent
is clear; repeated names remain necessary when ambiguity would result. Stable
terminology must not become a rotation of synonyms. Colons retain their useful
roles; no punctuation or word-count quota is imposed.

Meaning, agent work and activation rules remain unchanged. The focused cases
include semantic duplicates, ambiguous actors, colon chains and literal URL/error
colons that must remain exact. No new model run was performed for this candidate.

## Corrections after the 2026-10-12 pilot

The question's language now controls the reply explicitly. Russian remains the
priority for package examples and evaluation. Definitions stay within the
concept; comparisons show all requested options using the decision criterion.
Price per unit is unnecessary when choosing minimum total price at a capacity threshold.

Assigned roles establish actions and recipients, not exclusive knowledge or
transport routes. Actor counts are checked separately from grouped stages.
Optional advice establishes no guarantee of unchanged behavior. Existing copies
are preserved during diagnosis; adding recovery changes to a supplied procedure
requires evidence of need and authorization.

The assessor rubric separates conditional examples from system facts and records
reply language independently. Locked scores stay intact; any later source audit
is separately labeled as unblinded. Schema validity does not prove model verdicts.

## Verification boundary

The [additional regression set](../evals/compact-prompts.json) has ten paired RU/EN
scenario families. The [rubric](../evals/rubric.md) states what must survive and
which expansion or compression defects to flag. Existing prompts and historical
results remain unchanged.

Offline checks establish package validity and compatibility with existing loading
routes. Original examples can be checked editorially against their stated facts.
Neither is a new controlled model comparison or evidence of improved human
comprehension. Record new runs separately using the evaluation protocol. Compare
the previous and new cores on identical questions/settings; include a no-skill
condition when checking the overall effect. Reader checks remain separate.

The 0.6.0 entry was published on 2026-10-13. Updating source or
building a plugin does not update an existing personal installation.

## Bounds and conflicting facts

A lower bound or "more than" is a condition, not an approximate value; replacing
it changes the claim. Conflicting supplied facts are reported rather than resolved
by choosing one. A broader candidate that also removed empty rhetorical moves added
about 100 words, showed no measurable effect in a masked pilot and had two semantic
regressions. Only this narrow rule was kept for retesting.
