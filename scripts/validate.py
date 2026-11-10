"""Check both catalogs agree with the vendored plugins."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def validate(root: Path) -> list[str]:
    errors = []
    try:
        claude = json.loads((root / '.claude-plugin/marketplace.json').read_text(encoding='utf-8'))
        codex = json.loads((root / '.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
        sources = json.loads((root / 'sources.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return [f'Unreadable catalog or sources.json: {exc}']
    if claude.get('name') != codex.get('name'):
        errors.append('Claude and Codex catalogs must share one marketplace name')
    names = {p['name'] for p in sources.get('plugins', [])}
    on_disk = {p.name for p in (root / 'plugins').iterdir() if p.is_dir()} if (root / 'plugins').is_dir() else set()
    if names != on_disk:
        errors.append(f'plugins/ {sorted(on_disk)} does not match sources.json {sorted(names)}')
    for host, catalog, source_of in (
            ('claude', claude, lambda e: e.get('source')),
            ('codex', codex, lambda e: (e.get('source') or {}).get('path'))):
        for entry in catalog.get('plugins', []):
            name, src = entry.get('name'), source_of(entry)
            if src != f'./plugins/{name}':
                errors.append(f'{host} catalog: {name} source must be ./plugins/{name}')
                continue
            manifest = root / src / f'.{host}-plugin/plugin.json'
            if not manifest.is_file():
                errors.append(f'{host} catalog: {manifest.relative_to(root)} missing')
                continue
            data = json.loads(manifest.read_text(encoding='utf-8'))
            if data.get('name') != name:
                errors.append(f'{manifest.relative_to(root)}: name must be {name}')
            if not re.fullmatch(r'\d+\.\d+\.\d+\S*', str(data.get('version', ''))):
                errors.append(f'{manifest.relative_to(root)}: needs a semver version')
            if host == 'claude' and entry.get('version') != data.get('version'):
                errors.append(f'claude catalog: {name} version must equal plugin.json version')
    for plugin in on_disk:
        if not list((root / 'plugins' / plugin).glob('skills/*/SKILL.md')) and \
                not list((root / 'plugins' / plugin).glob('agents/*.md')):
            errors.append(f'plugins/{plugin} contains no skills or agents')
    return errors


if __name__ == '__main__':
    problems = validate(ROOT)
    for p in problems:
        print(p, file=sys.stderr)
    print('Marketplace valid.' if not problems else f'{len(problems)} problem(s).')
    sys.exit(1 if problems else 0)
