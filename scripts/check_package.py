#!/usr/bin/env python3
"""Offline checks for the standalone skill, documentation and public evidence."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')


def check():
    raw = subprocess.check_output(['git', 'ls-files', '--cached', '--others',
                                   '--exclude-standard', '-z'], cwd=ROOT)
    files = sorted({Path(item.decode()) for item in raw.split(b'\0') if item})
    errors = []
    for relative in files:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            errors.append(f'{relative}: not a regular file')
            continue
        if path.suffix.lower() == '.png':
            if not path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
                errors.append(f'{relative}: invalid PNG signature')
            continue
        try:
            text = path.read_text(encoding='utf-8')
            if path.suffix == '.json':
                json.loads(text)
        except (UnicodeError, ValueError) as error:
            errors.append(f'{relative}: invalid UTF-8 or JSON: {error}')
            continue
        if path.suffix == '.md':
            for match in LINK.finditer(text):
                raw_target = match.group(1).split(maxsplit=1)[0].strip('<>')
                parsed = urlsplit(raw_target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                if not (path.parent / unquote(parsed.path)).exists():
                    errors.append(f'{relative}: broken link {raw_target}')
        for prefix in ('/' + 'Users/', '/' + 'home/'):
            if re.search(re.escape(prefix) + r'[A-Za-z0-9_.-]+/', text):
                errors.append(f'{relative}: machine-specific private path in public package')
    core = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    lines = core.splitlines()
    if not lines or lines[0] != '---' or '---' not in lines[1:]:
        errors.append('SKILL.md: missing frontmatter')
    else:
        front = '\n'.join(lines[1:lines.index('---', 1)])
        if not re.search(r'^name: palych$', front, re.MULTILINE):
            errors.append('SKILL.md: expected name palych')
        if not re.search(r'^description: \S', front, re.MULTILINE):
            errors.append('SKILL.md: missing description')
    if re.search(r'\b(?:TODO|TBD|PLACEHOLDER)\b', core):
        errors.append('SKILL.md: unfinished instruction')
    # Skill installers scan the root and agent skill folders, so host copies stay
    # deep under packages/ and the root SKILL.md remains the only visible skill.
    for relative in files:
        if relative.name.lower() == 'skill.md' and relative != Path('SKILL.md') and (
                relative.parts[0] != 'packages' or len(relative.parts) < 4):
            errors.append(f'{relative}: second discoverable skill outside packages/')
    spec = importlib.util.spec_from_file_location('build_packages', ROOT / 'scripts' / 'build_packages.py')
    packages = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(packages)
    errors.extend(packages.drift(ROOT))
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Validated {len(files)} standalone files: frontmatter, JSON, links, public paths and generated packages.')
    return 0


if __name__ == '__main__':
    raise SystemExit(check())
