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

The next candidate combines overlapping wording, meaning and self-check rules
without moving runtime constraints behind external references. Detailed processes
pair each stage's action with its purpose, retaining loops and approval gates.
A preview and recap must not repeat the same process. Hypothetical scenarios and
unknowns earn space only when they affect interpretation, a decision or diagnosis.
Supplied uncertainty remains part of the source meaning to preserve.

The entrypoint is 762 words instead of 1048. This is a static size change, not a
token or comprehension result. The focused paired pilot uses fresh controls and
reports native usage separately; its outcome is recorded in development status.

The global installer omits optional example pointers in both supported layouts:
the legacy `## Optional examples` section and the compact trailing pointer beginning
`Consult only relevant optional`. Preserve that boundary when changing the pointer.
Installation tests verify full required content and the final runtime check,
without depending on the prose heading for semantic preservation.

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

The 0.6.0 entry is an unreleased candidate until publication. Updating source or
building a plugin does not update an existing personal installation.
