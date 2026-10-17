#!/usr/bin/env python3
"""Compare visible reply length in local Claude Code sessions before and after a cutover.

Reads Claude Code transcripts and prints aggregate counts only; no message text
reaches the output. A session belongs to the period of its first timestamp, so
the cutover should be the moment the always-on core was installed. This is an
observational comparison: tasks, models and other loaded skills differ between
periods, and the script does not check which instructions each session loaded.

A turn starts at a prompt the user typed and ends before the next one. Per turn:

- visible: characters of all assistant text blocks (progress messages and the
  final reply), excluding tool calls and thinking;
- final: characters of the last text block;
- messages: number of assistant text blocks;
- output: output tokens of the turn's main-thread API requests (text, tool
  calls and thinking together);
- slash: prose slash chains such as "result/effect" per 1000 words, outside code
  spans, paths and URLs.

Intervals are 95% percentile bootstraps over sessions for the difference in
medians (after minus before).
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import re
import statistics
import time

CODE = re.compile(r'```.*?```|`[^`\n]*`', re.S)
NON_PROSE = re.compile(r'\S*(?:://|\\)\S*|\S*/\S*/\S*|\S*\.\w{1,5}\b\S*|\[[^\]]*\]\([^)]*\)')
SLASH = re.compile(r'(?<![\w/])([^\W\d_]{3,})/([^\W\d_]{3,})(?![\w/])')
WORD = re.compile(r'[^\W_]+')
CYRILLIC = re.compile('[а-яё]', re.I)
SKIP_PREFIXES = ('<', 'This session is being continued', '[Request interrupted')


def prompt_text(record):
    """Text of a prompt the user typed, or None for tool results and injected messages."""
    if record.get('type') != 'user' or record.get('isMeta') or record.get('isCompactSummary') \
            or record.get('isSidechain') or record.get('isVisibleInTranscriptOnly'):
        return None
    content = (record.get('message') or {}).get('content')
    if isinstance(content, list):
        if any(part.get('type') == 'tool_result' for part in content if isinstance(part, dict)):
            return None
        content = '\n'.join(part.get('text', '') for part in content
                            if isinstance(part, dict) and part.get('type') == 'text')
    if not isinstance(content, str):
        return None
    text = content.strip()
    if not text or text.startswith(SKIP_PREFIXES):
        return None
    return text


def slash_chains(text):
    prose = NON_PROSE.sub(' ', CODE.sub(' ', text))
    return len(SLASH.findall(prose)), len(WORD.findall(prose))


def session_turns(path):
    """First timestamp, cwd and the per-turn measures of one transcript."""
    start = cwd = None
    turns, current, seen = [], None, set()
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            stamp = record.get('timestamp')
            if stamp and start is None:
                start = stamp
            cwd = cwd or record.get('cwd')
            text = prompt_text(record)
            if text is not None:
                current = {'russian': bool(CYRILLIC.search(text)), 'texts': [], 'output': 0, 'models': set()}
                turns.append(current)
                continue
            if current is None or record.get('type') != 'assistant' or record.get('isSidechain'):
                continue
            message = record.get('message') or {}
            if message.get('model') == '<synthetic>':
                continue
            for part in message.get('content') or []:
                if isinstance(part, dict) and part.get('type') == 'text' and part.get('text', '').strip():
                    current['texts'].append(part['text'])
            key = record.get('requestId') or message.get('id')
            usage = message.get('usage')
            if usage and key not in seen:
                seen.add(key)
                current['output'] += usage.get('output_tokens') or 0
                current['models'].add(message.get('model'))
    measured = []
    for turn in turns:
        if not turn['texts']:
            continue
        chains, words = slash_chains('\n'.join(turn['texts']))
        measured.append({'russian': turn['russian'], 'visible': sum(len(t) for t in turn['texts']),
                         'final': len(turn['texts'][-1]), 'messages': len(turn['texts']),
                         'output': turn['output'], 'chains': chains, 'words': words,
                         'models': sorted(m for m in turn['models'] if m)})
    return start, cwd, measured


def median_diff_interval(before, after, key, draws=2000, seed=7):
    """Bootstrap the difference in turn medians, resampling whole sessions."""
    if not before or not after:
        return None
    rng = random.Random(seed)
    diffs = []
    for _ in range(draws):
        b = [t[key] for s in rng.choices(before, k=len(before)) for t in s]
        a = [t[key] for s in rng.choices(after, k=len(after)) for t in s]
        if a and b:
            diffs.append(statistics.median(a) - statistics.median(b))
    diffs.sort()
    return [diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs)) - 1]]


def summarize(sessions):
    turns = [t for s in sessions for t in s]
    if not turns:
        return {'sessions': len(sessions), 'turns': 0}
    words = sum(t['words'] for t in turns)
    models = {}
    for turn in turns:
        for model in turn['models']:
            models[model] = models.get(model, 0) + 1
    result = {'sessions': len(sessions), 'turns': len(turns),
              'russian_turns': sum(t['russian'] for t in turns),
              'slash_chains': sum(t['chains'] for t in turns), 'words': words,
              'slash_per_1000_words': round(1000 * sum(t['chains'] for t in turns) / words, 2) if words else None,
              'turn_models': dict(sorted(models.items(), key=lambda item: -item[1]))}
    for key in ('visible', 'final', 'messages', 'output'):
        values = [t[key] for t in turns]
        result[key] = {'median': statistics.median(values), 'mean': round(statistics.fmean(values))}
    return result


def compare(before, after):
    result = {'before': summarize(before), 'after': summarize(after)}
    result['median_diff_95'] = {key: median_diff_interval(before, after, key)
                                for key in ('visible', 'final', 'messages', 'output')}
    return result


def parse_time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--cutover', required=True, help='ISO time the core was installed, e.g. 2026-10-13T07:58Z')
    parser.add_argument('--days', type=float, default=14, help='days before the cutover to include')
    parser.add_argument('--claude', default='~/.claude/projects')
    parser.add_argument('--cwd', action='append', default=[],
                        help='keep only sessions whose cwd starts with this path (repeatable)')
    parser.add_argument('--exclude-cwd', action='append', default=[],
                        help='drop sessions whose cwd contains this text (repeatable)')
    parser.add_argument('--model', help='keep only turns answered by this model alone')
    args = parser.parse_args()
    cutover = parse_time(args.cutover)
    floor = cutover.timestamp() - args.days * 86400
    groups = {'before': [], 'after': []}
    for path in sorted(Path(args.claude).expanduser().glob('*/*.jsonl')):
        if path.stat().st_mtime < floor:
            continue
        start, cwd, turns = session_turns(path)
        cwd = cwd or ''
        if args.model:
            turns = [t for t in turns if t['models'] == [args.model]]
        roots = [str(Path(root).expanduser()) for root in args.cwd]
        if not start or not turns or any(text in cwd for text in args.exclude_cwd) \
                or (roots and not any(cwd == root or cwd.startswith(root + '/') for root in roots)):
            continue
        moment = parse_time(start)
        if moment.timestamp() < floor:
            continue
        groups['after' if moment >= cutover else 'before'].append(turns)
    result = {'cutover': args.cutover, 'days_before': args.days, 'generated': time.strftime('%Y-%m-%d'),
              'filters': {'cwd': args.cwd, 'exclude_cwd': args.exclude_cwd, 'model': args.model},
              'all': compare(groups['before'], groups['after'])}
    for label, russian in (('russian_prompts', True), ('other_prompts', False)):
        pick = lambda sessions: [s for s in ([t for t in s if t['russian'] == russian] for s in sessions) if s]
        result[label] = compare(pick(groups['before']), pick(groups['after']))
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
