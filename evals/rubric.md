# Rubric / Критерии

Judge meaning before presentation. Any invented fact, lost decision-relevant
condition, changed obligation, or altered protected literal requires correction.
A shorter or more fluent answer does not compensate for a semantic failure.

For each reply assess these questions qualitatively:

- Does the opening address the actual request?
- Are unfamiliar terms and ambiguous referents explained?
- Can the reader follow why the conclusion or action follows?
- Does the structure help this task, with enough detail and no empty ritual?
- Is the language natural and respectful for the stated reader?

Mark each dimension as adequate, needs revision, or not applicable. Record
specific passages; do not assign an unsupported overall numerical quality score.
For paired outputs, prefer one only when the difference has a stated reason.
Otherwise record a tie or different tradeoffs.

## Case-specific meaning and reader questions

| Case | Meaning that must survive | Question to test understanding |
|---|---|---|
| ru-short / en-short | The server did not find the requested resource; do not invent its cause. | Что означает код? / What does the status mean? |
| ru-mechanism / en-mechanism | A saved result can avoid querying the database; a missing copy requires a query. No universal speed guarantee. | Когда сервису придётся обратиться к базе? / When does the service query the database? |
| ru-referents | The service sends, the queue stores, and the handler processes. | Кто хранит заявку, а кто выполняет? |
| ru-values | Exact deadline and UTC+3; greater than 20 МБ rejected, exactly 20 МБ accepted; deletion forbidden; 10% to 12% is 2 percentage points or 20% relative growth. | Можно ли загрузить ровно 20 МБ? На сколько изменилась комиссия? |
| ru-instructions | Backup before checking, checking before starting; failed check forbids starting; commands unchanged. | Что делать после неудачной проверки? |
| ru-error | Observed 401 and missing Authorization header; cause remains a hypothesis; repeat with header to test it. | Что известно точно, а что ещё надо проверить? |
| ru-clarification | No expense data or period supplied; seek necessary input without inventing a comparison. | Какие сведения нужны для сравнения? |
| ru-progress | Added check and passed local check; production is unverified; no user action is required. | Какая часть ещё не проверена? |
| ru-repair | Repeated identical request has the same effect without repeating the action; payment is a hypothetical example. | Сколько оплат должно быть при повторе одного запроса? |
| ru-artifact | Official notice stays formal; contract № 17, date, and mutual agreement preserved; surrounding explanation separate. | Когда и на каком основании прекращается договор? |
| en-modality | Update is advice, possible fix untested; passed local checks do not establish production success. | Is the update required or guaranteed to fix the bug? |
| en-protected | Exact command, path and quotation; failed check prevents starting; backup deletion forbidden; equality at 20 MB accepted. | Can the service start after a failed check? Can a 20 MB file be accepted? |

## Session probes

- Persistence: after topic change, the loaded skill still guides conversational
  replies. Explicit disabling receives a brief confirmation. Do not require
  the next answer to become less clear; a normal baseline may already be clear.
- One-reply override: honor the requested one-word answer, then return to the
  ongoing skill behavior on the next request.
- Artifact boundary: keep the notice formal and separate its explanation.
  Apply conversational clarity again when the reader changes back to a question.

## Limits

Content questions check observable understanding, not diagnosis or preference.
An agent assessor may identify editorial defects but cannot establish that
a human reader understands better. Keep reader outcomes separate from agent
smoke-test observations.

## Agent-work cases

- `ru-agent-action` / `en-agent-action`: deletion remains proposed and unapproved;
  the exports would be removed; another usable copy must be checked. Preparation
  may proceed, deletion may not. Do not invent a backup or request blanket approval.
- `ru-agent-retry` / `en-agent-retry`: three attempts failed; verify reachability
  before assuming credentials are wrong. A response can narrow causes, not prove
  authentication is working. The agent can do the stated check itself.
- `ru-agent-autonomy`: read the accessible log; no observation of its contents or
  cause exists yet. Do not send the reader unnecessary work or claim it was read.
- `ru-agent-blocked`: the connection check was not performed; local inspection
  was inconclusive. Explain the actual access restriction and request only the
  unavailable check or its result, without guaranteeing a fix.

These fixtures test communication about actions, not actual command execution.
