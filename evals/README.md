# Evaluation / Проверка

The input sets are [single-turn prompts](prompts.json) and
[session probes](session-probes.json). They contain only synthetic public inputs.
Use the [rubric](rubric.md) for assessment and record results in
[observations](observations.md).

The additional [compactness regression set](compact-prompts.json) contains
20 original cases, ten per language. It checks task-specific reply shapes,
unsupported causes and system guarantees, cache conditions, exact restrictions,
and retention of requested options and depth. Its case criteria are in the rubric.
The original 20-case set and its historical evidence remain unchanged.

The [focused compactness set](compactness-prompts.json) adds 12 synthetic cases,
six per language: cache measurements, detailed processes, full comparisons with
unknown prices, failed checks, exact restrictions and progress updates. For a
bounded pilot, use two fresh replies per case and condition; add the existing
RU/EN `cost` and `depth` cases when testing the known repetition defects. Generate
both controls anew. Two repetitions are exploratory, below the full protocol.
Lock masked judgments before disclosure, then separately audit source meaning.
Report core size, native input/output tokens, output size and editorial preferences
separately. Smaller instructions or answers do not establish better understanding
or reduced subscription-limit debits.

The [repetition set](repetition-prompts.json) checks semantic duplicates,
unambiguous referents and repetitive colon links. Use it alongside detailed
process, full-comparison and exact-condition cases; shortening cannot hide
missing stages, changed actors or lost conditions. The rubric treats synonym
cycling and punctuation counts as different from useful compactness. The next
candidate is prepared from one owner-supplied human-preferred example; it has
not undergone a new model run or a reader comprehension study.
Give generators only each case's `prompt`; `protected` criteria stay with the
assessor. Exact colons in URLs and quoted messages remain protected literals.

The [empty-moves set](empty-moves-prompts.json) adds 12 synthetic RU/EN cases:
grading labels and placeholder explanations, causal chains under shortening,
price and count bounds, conflicting supplied facts, a plainly reported failure
and a legitimate contrast with a stated claim. It has not undergone a model run.

The [full-comparison set](full-comparison-prompts.json) adds six synthetic RU/EN
cases: complete option lists, an unknown qualifying price, and a two-sentence
choice-only request. Repeat each case three times per condition. Check individual
values and uncertainty before presentation; record answer placement separately
from clarity judgments. Choice-only requests do not require a full table.

For a focused pilot select affected families; for a full run of the additional
set, pass `--prompts evals/compact-prompts.json` to the existing masking tool.
Three repetitions make 60 pairs for this set. Generation consumes the agent's
usage limits; run the free offline package checks first. Record new results in
distinct files. Focused model checks and their limits are recorded separately in
[development status](../docs/STATUS.md); historical results remain unchanged.

## Reproducible blind checks

Use [blind-protocol.md](blind-protocol.md) and `blind_eval.py` for new comparisons.
The full set has 20 cases (14 Russian, 6 English); run each three times in each
condition. Use fresh generation contexts per case when possible. Record shared
contexts and any unavailable settings rather than claiming independence.
The helper masks conditions, balances A/B positions, validates pairs, locks
judgments before disclosure, and reports semantic regressions separately.

The original results below remain historical editorial smoke tests; do not
relabel them as blind or as a controlled comparison. Model scoring still measures
editorial proxies, not reader comprehension. Use the separate
[reader protocol](reader-check.md) for that claim.

Record language compliance separately and use the rubric's assessor calibration.
Give the assessor only judging criteria and calibration, keeping later workflow
steps out of its prompt. An assessor's claim that it performed an unblinded audit
is not evidence of that audit; verify the actual inputs and recorded operations.
Audit verdicts against raw replies after locking; keep the audit separate from
the locked score. A missed error is not repaired by silently changing an earlier
judgment. Label any later audit as unblinded and record the exact tested core hash.

## Paired reply checks

1. Select the same case IDs for both conditions. Include Russian and English.
2. Keep the model, generation settings, tools, and base instructions the same.
   Start a fresh conversation for each case when the host allows it. In a
   batched smoke test, record that the cases share a context.
3. For the baseline, provide only the case's prompt. For the skill condition,
   load only `SKILL.md`, then provide the same prompt. Do not provide the
   rubric, examples, expected answer, or the paired response to either generator.
4. Save the raw outputs with the condition and case ID outside the public
   package. If generation or settings are unavailable, record that limitation;
   do not fabricate a baseline or claim a model setting you did not observe.
5. Mask the condition labels and vary their order for assessment where possible.
   Assess semantic preservation before style. Use content criteria rather than
   matching phrases or counting words.
6. Record ties and regressions as well as improvements. Revise demonstrated
   weaknesses, then rerun the affected cases. Retain earlier results.

This protocol can be run manually with the host's existing conversation tools.
The skill has no runtime evaluator or API dependency. External paid evaluation
is optional and requires its own budget and authorization.

## Session behavior

Use `session-probes.json` in a conversation where the host actually loads the
skill. Send one turn at a time. Check topic changes, a one-reply format override,
the artifact boundary, and explicit disabling. Record the observed behavior and
the host's context-retention limits. A single batched completion cannot prove
persistence or disabling.

## Reader comprehension / Понимание читателями

Проверяйте с читателями, для которых предназначен ответ. Учитывайте их знания
темы и заявленные потребности в чтении; не делайте предположений о диагнозе.

Дайте ответ без дополнительных пояснений. Попросите пересказать основную
мысль, ответить на конкретный вопрос из рубрики и отметить непонятные места.
Не ограничивайтесь вопросом «Понятно?». Разделяйте впечатление от стиля и
правильное понимание содержания.

Запишите ошибки понимания, измените объяснение и повторите проверку.
Самопроверка агента и оценка другим агентом не заменяют участие читателей.
Для любой сохранённой обратной связи согласуйте использование и публикацию;
не включайте личные ответы читателей в публичный пакет по умолчанию.

## Recording evidence

Report the tested revision or content hash, date, case IDs, observed generator
settings, conditions, limitations, semantic failures, and the type of evaluation.
Distinguish packaging checks, editorial review, agent behavior, and reader
comprehension. An instruction-only revision remains unverified until tested.

## Persistence evidence

Run the optional adapter checks with synthetic events:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s adapters -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evals -p 'test_*.py'
```

Test enable → compact → off → compact with the always-on default active, in
separate processes sharing only saved state. Also test language changes, ordinary
prompts, quoted control phrases, corrupt state, and another session's isolation.
For a live-host integration check follow [adapter instructions](../adapters/README.md).
Record the host version and delivered hook context; a clear-looking reply is not
evidence that the hook ran. Live installation and real compaction remain a
separate verification step.
