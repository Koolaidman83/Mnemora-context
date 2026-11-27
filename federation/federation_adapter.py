"""Mnemora Fabric v0.3 federation policy adapter. Python stdlib only.

Read-only with respect to Fabric's database. This module never executes jobs,
starts services, or exposes memory. It filters the coordinator's node records.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

DEFAULT_POLICY = {
    'schema_version': '0.2.0',
    'default_deny': True,
    'node_overrides': {},
    'workloads': {
        'general': {'allowed_regions': ['*'], 'allowed_visibilities': ['private', 'collaborative'], 'minimum_ram_mb': 0},
        'private-memory': {'allowed_regions': ['us-east'], 'allowed_visibilities': ['private'], 'minimum_ram_mb': 0},
        'collaborative-memory': {'allowed_regions': ['*'], 'allowed_visibilities': ['collaborative'], 'minimum_ram_mb': 0},
    },
}

class FederationPolicy:
    def __init__(self, registry_path: str | Path, policy_path: str | Path):
        self.registry = json.loads(Path(registry_path).read_text())
        self.policy = json.loads(Path(policy_path).read_text())
        self.nodes = {n['id']: n for n in self.registry['nodes']}
        if len(self.nodes) != len(self.registry['nodes']):
            raise ValueError('duplicate registry node IDs')

    def metadata(self, node_id: str) -> dict[str, Any] | None:
        node = self.nodes.get(node_id)
        if node is None:
            return None
        result = dict(node)
        result.update(self.policy.get('node_overrides', {}).get(node_id, {}))
        return result

    def allowed(self, node: dict[str, Any], capability: str, workload: str = 'general') -> tuple[bool, str]:
        if not node.get('online'):
            return False, 'offline'
        if capability not in node.get('capabilities', []):
            return False, 'missing-capability'
        meta = self.metadata(node.get('node_id', ''))
        if meta is None:
            return False, 'unregistered-node'
        if meta.get('status') == 'planned':
            return False, 'planned-node'
        rules = self.policy.get('workloads', {}).get(workload)
        if not rules:
            return False, 'unknown-workload'
        regions = rules.get('allowed_regions', [])
        if '*' not in regions and meta.get('region') not in regions:
            return False, 'region-denied'
        if meta.get('visibility') not in rules.get('allowed_visibilities', []):
            return False, 'visibility-denied'
        minimum = rules.get('minimum_ram_mb', 0)
        ram = node.get('metrics', {}).get('ram_available_mb')
        if minimum and (not isinstance(ram, (int, float)) or ram < minimum):
            return False, 'insufficient-or-unknown-ram'
        return True, 'allowed'

    def choose(self, coordinator: Any, capability: str, workload: str = 'general',
               exclude: set[str] | None = None, target_node: str | None = None) -> dict[str, Any] | None:
        """Use existing Fabric scoring, with federation eligibility applied first.

        Call this from the coordinator's dispatcher only after integration review.
        """
        excluded = set(exclude or ())
        active = coordinator.active_counts()
        candidates = []
        for node in coordinator.db.nodes():
            nid = node['node_id']
            if nid in excluded or (target_node and nid != target_node):
                continue
            if not self.allowed(node, capability, workload)[0]:
                continue
            score = coordinator.node_score(node, capability) - active.get(nid, 0) * 1000000
            candidates.append((score, nid, node))
        candidates.sort(key=lambda entry: (-entry[0], entry[1]))
        return candidates[0][2] if candidates else None
