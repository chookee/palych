# Context payloads — 0.3.0

These are static reference counts, not host usage or comprehension measurements.
[Measurements](results/token-counts-2026-10-10.json) include compared text hashes.
Both hook variants use the same synthetic paths, host and session ID.

| Text | 0.2.0 | 0.3.0 | Fewer reference tokens |
|---|---:|---:|---:|
| Standalone core | 2298 | 1162 | 49.43% |
| Active SessionStart, full core | 2508 | 1310 | 47.77% |
| Repeated enable in one context | 2508 | 159 | 93.66% |
| Off SessionStart | 234 | 155 | 33.76% |

First activation in 0.3.0 emits 1319 tokens, including its saved acknowledgement.
Ordinary UserPromptSubmit messages emit nothing, as in 0.2.0. SessionStart
always restores the full active core; suppression applies only to repeated
activation with the same core hash between context boundaries.

Counts use a local Unicode pretokenizer and greedy byte-pair merges with the
public o200k_base vocabulary. The old-core count matches the previous audit,
the known vector `hello world` matches IDs 24912 and 2375, and byte/text round
trips are checked. This is a reference implementation, not the native Codex
or Claude tokenizer. It excludes message wrappers, hidden reasoning, cache
accounting, tools and the rest of the conversation.

Algorithm sources: [OpenAI tokenizer definition](https://github.com/openai/tiktoken/blob/main/tiktoken_ext/openai_public.py)
and [educational BPE implementation](https://github.com/openai/tiktoken/blob/main/tiktoken/_educational.py).
The vocabulary SHA-256 is recorded in the measurements.

The core retains sufficient explanation without a reply-length cap. Examples
are consulted selectively; self-checking is silent; saved control acknowledgements
avoid a duplicate helper call. Actual platform savings, live event delivery,
automatic skill loading alongside hooks and comprehension remain unmeasured.
