![Anton Chekhov with a fountain pen at his desk — Palych banner](assets/chekhov-banner.png)

# Палыч / Palych

Named in honor of А.П. Чехов (A.P. Chekhov).

Palych helps an agent answer compactly and clearly: the main point first, followed
by the explanation the reader needs. Russian is the primary language; English is also
supported. After installation, the rules apply to every reply, question and
progress update. No separate skill invocation is needed.

[Русский](README.md)

## Install

Paste this message into your agent's chat:

```text
Install Palych from https://github.com/ponomr/palych using INSTALL.md.
Enable it for all replies without a separate invocation. Preserve my other instructions.
```

The agent will choose the route for its host: global instructions or a plugin
for Codex and Claude Code, an extension for Gemini CLI, a skill for Hermes or a
rule for Cursor. Start a new conversation afterward. Manual installation, updates and removal are in
[INSTALL.md](INSTALL.md).

## Main principles

- Follow the question's language; Russian remains the development priority.
- Lead with the answer. Keep conditions that change the conclusion nearby.
- Match the form to the question: definition, explanation, instructions, comparison or progress.
- Explain each point once. Add reference material or diagnostics when the task needs them.
- Use familiar words and concrete actions. Explain necessary terms at first use.
- Preserve connections between ideas; keep unknown causes unknown.
- Use the same name for the same concept. Replace ambiguous pronouns with names.
- Preserve exact meaning: numbers, negations, limits and uncertainty.
- Choose structure for the task. No mandatory word limit, next action or repeated status.

For agent work, Palych separates completed work from verified results and explains
errors without inventing a cause. Documents such as emails and reports follow
the user's requested style.

## Controls

“Turn off palych” disables it for this conversation. “Enable palych” turns it back
on. To disable the default for new conversations, remove the installer block as
described in [INSTALL.md](INSTALL.md). The plugin has separate
[persistent mode controls](adapters/README.md).

Palych adapts selected Easy-to-read guidance for chat. It assumes no reader
diagnosis and makes no claim of compliance with the full methodology.
[Sources](references/sources.md) · [Checks and limits](docs/STATUS.md) ·
[Development](docs/DEVELOPMENT.md). License: [MIT](LICENSE).

## Example

**Question:** “Why does caching sometimes make a response faster and sometimes not?”

In this example, the cache stores completed results. If a result is missing,
the service computes it again.

**Without Palych:**

> Caching reduces latency on a cache hit. A cache miss triggers computation.
> Check TTL, eviction policy, hit rate and the invalidation mechanism.

**With Palych:**

> A cache can make a response faster when the result is already stored and
> retrieving it takes less time than computing it again.
>
> If the result is missing, the computation still happens, with the cache lookup
> adding extra time. That request can therefore be slightly slower.

This is an illustrative edit written for the package. It does not prove that a
particular model will always answer this way or that readers understand it better.

## Sample skill test results

Blind comparison on 13 October 2026: `claude-sonnet-5-5` replies without Palych and
with Palych from `main` 466fb77. 30 tasks in Russian and English, 3 replies per task,
90 pairs. The same model judged the pairs without knowing which reply was which.

| Measure | Without Palych | With Palych |
|---|---:|---:|
| Pair wins | 1 | 86 |
| Ties | 3 | 3 |
| Meaning errors | 45 | 3 |
| Output tokens | 38,284 | 20,918 (−45%) |
| Reply characters | 98,562 | 51,390 (−48%) |
| Input tokens per request | ~690 | ~3,300 |

A meaning error is an invented guarantee, picking one of conflicting facts or another
distortion of the task. Input tokens grow because the core is sent with every request.
This is an exploratory pilot, not a test of reader comprehension. Details are in
[STATUS.md](docs/STATUS.md).
