# Палыч / Palych

Named in honor of А.П. Чехов (A.P. Chekhov).

Palych helps an agent answer clearly: the main point first, followed by enough
explanation to understand it. Russian is the primary language; English is also
supported. After installation, the rules apply to every reply, question and
progress update. No separate skill invocation is needed.

[Русский](README.md)

## Install

Paste this message into your agent's chat:

```text
Install Palych from https://github.com/ponomr/palych using INSTALL.md.
Enable it for all replies without a separate invocation. Preserve my other instructions.
```

The agent will choose the Codex or Claude Code installation. Start a new
conversation afterward. Manual installation, updates and removal are in
[INSTALL.md](INSTALL.md).

## Example

**Question:** “What is a cache, and why do I see an old page after a website update?”

**Without Palych:**

> The client may be serving a cached resource. Perform client-side cache invalidation.

**With Palych:**

> Your browser may be showing an old copy of the page it saved earlier.
> These saved copies are called a cache. They help websites load faster.
>
> Try reloading the page without using the saved copy. If the page still looks
> the same, the cause may be in the website's settings.

This is an illustrative edit written for the package. It does not prove that a
particular model will always answer this way or that readers understand it better.

## Main principles

- Lead with the answer. Keep conditions that change the conclusion nearby.
- Use familiar words and concrete actions. Explain necessary terms at first use.
- Explain enough to preserve causes and connections between ideas.
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
