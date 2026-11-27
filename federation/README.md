# Mnemora Federation v0.2: Fabric v0.3 adapter

This package is a **policy-only, opt-in integration prototype**, not a running service.
It does not change Fabric files, databases, network ports, tokens, or heartbeat behavior.

## Installation

Copy `federation_adapter.py`, `policy.json`, and `test_adapter.py` into the repository's `federation/` directory alongside `nodes.json`.

Run from that directory:

```sh
python test_adapter.py
```

## Integration design

Fabric v0.3's `DB.nodes()` remains the source of live status, metrics and capabilities.
The static `nodes.json` contains policy metadata only. IDs **must match** worker `node_id`
values as reported by `/api/nodes`; mismatches are denied. No live worker is automatically
registered by this module.

The coordinator's existing `node_score()` and `active_counts()` remain authoritative
for scoring. `FederationPolicy.choose()` filters candidates first and then applies the
same score formula and active-job penalty as Fabric's `choose()`.

Example for future reviewed integration:

```python
from federation_adapter import FederationPolicy
policy = FederationPolicy('/path/to/nodes.json', '/path/to/policy.json')
selected = policy.choose(coord, capability='python', workload='general', target_node=None)
```

**Do not wire this into dispatch yet.** Fabric job payloads do not currently carry a
trusted workload classification; the coordinator must derive it from authenticated,
validated job submission before selecting a worker. Do not accept a client-supplied
`general` label as authority to dispatch private memory data.

## Security boundaries

- Registry is static and public-safe; never add private IPs, secrets or memory content.
- Deny unknown node IDs, workloads, offline nodes and planned nodes.
- This adapter is *not* authentication or memory authorization. The existing memory
  API must remain private; no private memory routes or cross-region replication are added.
- The `region` field is declarative metadata, not cryptographic location proof.
- Policy must be deployed from a trusted local copy before it protects anything.
- A separate rollout is required for worker identity verification, token scoping,
  classification enforcement, and fail-closed behavior in the dispatch loop.

## Rollback

Because the module is opt-in, rollback is simply not importing it. Existing Fabric
v0.3 files and databases are untouched.
