"""Vendor each plugin from sources.json into plugins/<name>/ and regenerate both catalogs.

Usage:
  python scripts/sync.py                      # sync all plugins at their pinned refs
  python scripts/sync.py --plugin NAME --ref vX.Y.Z   # pin a new ref, then sync it
  python scripts/sync.py --check              # fail if plugins/ or catalogs are out of date
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / 'sources.json'
MARKETPLACE = 'agent-plugins'
OWNER = 'tarrgor'
SEMVER = re.compile(r'v?(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)')
SKIP = {'.DS_Store', '__pycache__'}


def load_sources() -> dict:
    return json.loads(SOURCES.read_text(encoding='utf-8'))


def checkout(repo: str, ref: str, dest: Path) -> None:
    subprocess.run(['git', '-c', 'advice.detachedHead=false', 'clone', '--quiet', '--depth', '1', '--branch', ref, repo, str(dest)], check=True)


def select(src: Path, patterns: list[str]) -> list[Path]:
    files = set()
    for pattern in patterns:
        for path in src.glob(pattern):
            if path.is_file() and not SKIP & set(path.relative_to(src).parts) and path.suffix != '.pyc':
                files.add(path)
    return sorted(files)


def vendor(entry: dict, out: Path) -> None:
    """Write one plugin's files into out/, stamping the ref's semver into both manifests."""
    match = SEMVER.fullmatch(entry['ref'])
    if not match:
        raise ValueError(f"{entry['name']}: ref must be a semver tag such as v1.2.0, got {entry['ref']}")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / 'src'
        checkout(entry['repo'], entry['ref'], src)
        files = select(src, entry['include'])
        if not files:
            raise ValueError(f"{entry['name']}: include patterns matched no files")
        for path in files:
            target = out / path.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    for host in ('claude', 'codex'):
        manifest = out / f'.{host}-plugin/plugin.json'
        if not manifest.is_file():
            continue
        data = json.loads(manifest.read_text(encoding='utf-8'))
        if data.get('name') != entry['name']:
            raise ValueError(f"{manifest}: name {data.get('name')!r} != sources.json name {entry['name']!r}")
        data['version'] = match.group(1)
        manifest.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def catalogs(plugins_dir: Path, names: list[str]) -> dict[str, dict]:
    claude, codex = [], []
    for name in names:
        base = plugins_dir / name
        rel = f'./plugins/{name}'
        if (base / '.claude-plugin/plugin.json').is_file():
            m = json.loads((base / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
            claude.append({'name': name, 'source': rel, 'description': m.get('description', ''),
                           'version': m['version']})
        if (base / '.codex-plugin/plugin.json').is_file():
            m = json.loads((base / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
            codex.append({'name': name, 'source': {'source': 'local', 'path': rel},
                          'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
                          'category': m.get('interface', {}).get('category', 'Developer Tools')})
    return {
        '.claude-plugin/marketplace.json': {
            'name': MARKETPLACE, 'description': f"{OWNER}'s plugins for Claude.",
            'owner': {'name': OWNER}, 'plugins': claude},
        '.agents/plugins/marketplace.json': {
            'name': MARKETPLACE, 'interface': {'displayName': 'Agent Plugins'}, 'plugins': codex},
    }


def build(root: Path, sources: dict) -> None:
    """Build plugins/ and both catalogs under root."""
    names = [p['name'] for p in sources['plugins']]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate plugin names in sources.json')
    for entry in sources['plugins']:
        vendor(entry, root / 'plugins' / entry['name'])
    for rel, data in catalogs(root / 'plugins', names).items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def tree_diff(a: Path, b: Path) -> list[str]:
    """Relative paths that are missing on either side or differ in content."""
    def files(root: Path) -> dict[str, Path]:
        return {p.relative_to(root).as_posix(): p for p in root.rglob('*')
                if p.is_file() and not SKIP & set(p.relative_to(root).parts)} if root.is_dir() else {}
    fa, fb = files(a), files(b)
    return sorted(k for k in fa.keys() | fb.keys()
                  if k not in fa or k not in fb or fa[k].read_bytes() != fb[k].read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--plugin')
    parser.add_argument('--ref')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    sources = load_sources()

    if args.ref or args.plugin:
        if not (args.ref and args.plugin):
            parser.error('--plugin and --ref go together')
        entry = next((p for p in sources['plugins'] if p['name'] == args.plugin), None)
        if entry is None:
            parser.error(f'Unknown plugin {args.plugin}; add it to sources.json first')
        entry['ref'] = args.ref
        SOURCES.write_text(json.dumps(sources, indent=2) + '\n', encoding='utf-8')

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp)
            build(fresh, sources)
            stale = [f'{rel}/{path}' for rel in ('plugins', '.claude-plugin', '.agents')
                     for path in tree_diff(ROOT / rel, fresh / rel)]
        if stale:
            print('Out of date:', *stale, sep='\n  ', file=sys.stderr)
            print('Run python scripts/sync.py and commit.', file=sys.stderr)
            return 1
        print('plugins/ and catalogs match sources.json.')
        return 0

    shutil.rmtree(ROOT / 'plugins', ignore_errors=True)
    build(ROOT, sources)
    print(f"Synced {len(sources['plugins'])} plugin(s).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
