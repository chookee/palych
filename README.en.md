# Palych / Палыч

Named in honor of Anton Pavlovich Chekhov.

Repository: [ponomr/palych](https://github.com/ponomr/palych).

[Русский](README.md)

A standalone agent skill for understandable conversational replies in Russian
and English. It helps the reader find the answer, understand the wording, and
follow the explanation. Russian is the primary supported language.

## Use

Place the `palych` folder in your host's skills directory, keeping
`SKILL.md` and the folder structure. Invoke the skill by name using the
mechanism your host supports. For example, ask:

> Enable palych for this conversation.

If your host does not support skills, provide the contents of `SKILL.md` as
conversation instructions. The host controls installation and loading.
Installation alone does not guarantee activation.

After loading, the rules apply until you explicitly turn them off, including
after a topic change. To stop: “Turn off palych.” Retention after context
compaction depends on the host. The optional adapter described below stores
mode outside that context; without it, reload the skill if instructions are lost.

## Behavior

The answer comes first. Unfamiliar concepts are explained at first use.
The agent makes the link between the evidence and the conclusion explicit and
chooses a structure that fits the request. A clearer reply can be shorter or
need more explanation.

The rules cover replies, questions, and progress updates. Follow the conversation
language or an explicit language request; do not automatically produce a translation.

The skill does not set the style of emails, reports, posts, or other artifacts,
including reusable text delivered inside a chat. Artifacts follow their own
task. Palych applies to the explanation around them.

## Accuracy and boundaries

Preserve conditions, exceptions, uncertainty, and exact values. Leave code,
commands, paths, identifiers, and direct quotations intact. There are no fixed
word limits, mandatory next steps, or required time estimates.

The skill assumes no diagnosis and claims no full Easy-to-read compliance.
It needs no other skill, tool, service, or API.

## Resources and evaluation

- [Agent instructions](SKILL.md).
- Examples: [Russian](references/examples.ru.md), [English](references/examples.en.md).
- [Sources and adaptations](references/sources.md).
- [Evaluation tasks and protocol](evals/README.md).
- [Development observations](evals/observations.md).

All examples were written for this package. Editorial review and agent smoke
tests do not establish improved comprehension by readers. Observations record
what was checked and what remains untested. Reader testing happens during
development, not after every reply.

## Persistent mode and stronger evaluation

The optional [host adapter](adapters/README.md) builds local Codex or Claude Code
plugins from this standalone source. It stores a session's on/off state and an
optional always-on default, then restores the core on `SessionStart`, including
`compact`. A saved off state overrides the default. Building is not installation
or hook trust; the core remains usable without Python or a plugin.

Agent-work rules clarify consequences and existing authorization, change the
investigation after repeated failed fixes, and keep available work with the
agent. They grant no permissions and impose no per-turn status ritual.

The suite now includes 20 prompts. The [blind protocol](evals/blind-protocol.md)
and offline helper mask condition names, lock judgments before disclosure and
track semantic failures separately. A full run requires three repetitions of
every case under the same observed configuration. Exploratory pilots with
unavailable model parameters are explicitly marked. The separate
[reader check](evals/reader-check.md) tests unaided understanding rather than
replacing it with editorial scores.

## License

[MIT](LICENSE) covers the original package materials. Linked publications keep
their own rights and terms.

## Context usage

Version 0.3.0 consolidates related rules and removes repeated instructions.
Examples are consulted only for a specific wording problem; evaluation resources
are for development. Repeated activation through the adapter emits a short
acknowledgement; context changes still restore the complete core. The silent
self-check remains part of composing a reply, without a separate model call.

Stop once the request is answered. Preserve causal explanations, exact values
and necessary conditions without word limits. A smaller instruction payload
does not imply the same percentage reduction in platform usage limits.

Static measurements: [context payloads](evals/token-usage.md).

## Development and history

[Development](docs/DEVELOPMENT.md) · [Status](docs/STATUS.md) · [Origin](docs/ORIGIN.md) · [Changelog](CHANGELOG.md).
