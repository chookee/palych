#!/usr/bin/env python3
"""Estimate how often an always-on core is read from the prompt cache.

Reads local Claude Code transcripts and Codex rollouts and prints aggregate
counts only; no message text reaches the output. The core sits in the first
request's context, after the host's shared system prefix, so each later request
in a session falls into one of three classes:

- warm: its cached input covers the whole first request, so the core was read
  from the cache;
- cold: its cached input does not exceed the first request's cached input (the
  host prefix shared across sessions), so the core was written or sent uncached;
- ambiguous: in between; the cache boundary may fall before or after the core.

The first request of a session counts as cold. Claude price multipliers relative
to base input: cache read 0.1 (0.05 on Opus 5.5, 0.025 on Fable 5.1 and Mythos
5.1), 5-minute write 1.25, 1-hour write 2, uncached 1. Codex reports no write
premium; its cached-read multiplier is a parameter.
"""
import argparse
import json
from pathlib import Path
import sys
import time

READ = 0.1
READ_BY_MODEL = {'claude-opus-5-5': 0.05, 'claude-fable-5-1': 0.025, 'claude-mythos-5-1': 0.025}
WRITE = {'1h': 2.0, '5m': 1.25, 'none': 1.0}


def claude_requests(path):
    """Usage of each main-thread API request in a Claude Code transcript, in order."""
    seen, requests = set(), []
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            if '"usage"' not in line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            message = record.get('message') or {}
            usage = message.get('usage')
            key = record.get('requestId') or message.get('id')
            if record.get('type') != 'assistant' or record.get('isSidechain') or not usage or key in seen:
                continue
            if message.get('model') == '<synthetic>':
                continue
            seen.add(key)
            detail = usage.get('cache_creation') or {}
            ttl = ('1h' if detail.get('ephemeral_1h_input_tokens') else
                   '5m' if detail.get('ephemeral_5m_input_tokens') or usage.get('cache_creation_input_tokens') else 'none')
            cached = usage.get('cache_read_input_tokens') or 0
            total = cached + (usage.get('cache_creation_input_tokens') or 0) + (usage.get('input_tokens') or 0)
            requests.append({'cached': cached, 'total': total, 'ttl': ttl,
                             'read': READ_BY_MODEL.get(message.get('model'), READ),
                             'output': usage.get('output_tokens') or 0})
    return requests


def codex_requests(path):
    """Usage of each API request in a Codex rollout, in order."""
    requests, last_total = [], None
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            if '"token_count"' not in line:
                continue
            try:
                payload = json.loads(line).get('payload') or {}
            except ValueError:
                continue
            info = payload.get('info') or {}
            usage, total = info.get('last_token_usage'), info.get('total_token_usage')
            # Codex repeats the last count on some events; a request changes the running total.
            if payload.get('type') != 'token_count' or not usage or total == last_total:
                continue
            last_total = total
            requests.append({'cached': usage.get('cached_input_tokens') or 0,
                             'total': usage.get('input_tokens') or 0, 'ttl': 'none',
                             'output': usage.get('output_tokens') or 0})
    return requests


def classify(requests):
    """Label requests warm, cold or ambiguous against the session's first request."""
    if not requests:
        return []
    first = requests[0]
    labels = ['first']
    for request in requests[1:]:
        if request['cached'] >= first['total']:
            labels.append('warm')
        elif request['cached'] <= first['cached']:
            labels.append('cold')
        else:
            labels.append('ambiguous')
    return labels


def summarize(sessions, read=None):
    """Aggregate classes and the core's average price multiplier (low and high bound)."""
    counts = {'first': 0, 'warm': 0, 'cold': 0, 'ambiguous': 0}
    low = high = output = 0.0
    requests_total = 0
    for requests in sessions:
        for request, label in zip(requests, classify(requests)):
            counts[label] += 1
            requests_total += 1
            output += request['output']
            write = WRITE[request['ttl']]
            read_price = read if read is not None else request.get('read', READ)
            if label == 'warm':
                low += read_price
                high += read_price
            elif label == 'ambiguous':
                low += read_price
                high += write
            else:
                low += write
                high += write
    sessions = [s for s in sessions if s]
    return {
        'sessions': len(sessions),
        'requests': requests_total,
        'requests_per_session': round(requests_total / len(sessions), 1) if sessions else 0,
        'classes': counts,
        'core_multiplier_low': round(low / requests_total, 3) if requests_total else None,
        'core_multiplier_high': round(high / requests_total, 3) if requests_total else None,
        'mean_output_tokens': round(output / requests_total) if requests_total else None,
    }


def recent(root, pattern, days, exclude=()):
    cutoff = time.time() - days * 86400
    return sorted(path for path in Path(root).expanduser().glob(pattern)
                  if path.stat().st_mtime >= cutoff and not any(part in path.parts for part in exclude))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--days', type=float, default=14, help='only logs modified in this many days')
    parser.add_argument('--claude', default='~/.claude/projects')
    parser.add_argument('--codex', default='~/.codex/sessions')
    parser.add_argument('--codex-read', type=float, default=READ,
                        help='Codex cached-input price relative to base input (assumption)')
    args = parser.parse_args()
    claude = [claude_requests(p) for p in recent(args.claude, '*/*.jsonl', args.days, ('subagents',))]
    codex = [codex_requests(p) for p in recent(args.codex, '**/rollout-*.jsonl', args.days)]
    result = {'days': args.days,
              'claude_code': summarize(claude),
              'codex': {**summarize(codex, args.codex_read), 'cached_read_multiplier': args.codex_read}}
    json.dump(result, sys.stdout, indent=2)
    print()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
