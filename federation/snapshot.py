#!/usr/bin/env python3
"""Read-only, sanitized snapshot of Fabric v0.3's node table.
No network access, no changes to Fabric, no secrets or raw URLs exported.
"""
import argparse
import json
import sqlite3
import time
from pathlib import Path


def snapshot(db_path, registry_path, timestamp=None, age=120):
    timestamp = int(time.time()) if timestamp is None else int(timestamp)
    registry = json.loads(Path(registry_path).read_text())
    declared = registry.get('nodes', [])
    if not isinstance(declared, list):
        raise ValueError('nodes must be a list')
    # Only explicitly declared public aliases can appear in the snapshot.
    aliases = {n['id']: n for n in declared if isinstance(n, dict) and isinstance(n.get('id'), str)}
    if len(aliases) != len(declared):
        raise ValueError('invalid or duplicate registry IDs')
    uri = Path(db_path).resolve().as_uri() + '?mode=ro'
    with sqlite3.connect(uri, uri=True, timeout=3) as conn:
        rows = conn.execute('SELECT node_id, last_seen FROM nodes').fetchall()
    last_seen = {str(node): int(seen) for node, seen in rows}
    output = []
    for alias, definition in sorted(aliases.items()):
        if definition.get('visibility') == 'private':
            # Private nodes are represented only by their explicitly published alias.
            pass
        seen = last_seen.get(alias)
        observed = seen is not None and 0 <= timestamp - seen <= age
        output.append({
            'id': alias,
            'region': definition.get('region', 'unspecified'),
            'roles': definition.get('roles', []),
            'observed_recently': bool(observed),
            'deployment': 'planned' if definition.get('status') == 'planned' else 'registered',
        })
    return {'schema_version': '0.1.0', 'generated_at_unix': timestamp,
            'freshness_seconds': age, 'source': 'fabric-v0.3-read-only', 'nodes': output}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=True, help='Existing coordinator fabric.sqlite3')
    p.add_argument('--registry', default=str(Path(__file__).with_name('nodes.json')))
    p.add_argument('--out', required=True)
    p.add_argument('--max-age', type=int, default=120)
    a = p.parse_args()
    if a.max_age < 1 or a.max_age > 3600:
        p.error('--max-age must be between 1 and 3600')
    data = snapshot(a.db, a.registry, age=a.max_age)
    target = Path(a.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + '.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n')
    temp.replace(target)
    print('SNAPSHOT_OK', len(data['nodes']), 'declared nodes', '->', target)


if __name__ == '__main__':
    main()
