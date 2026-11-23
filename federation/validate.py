#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parent

nodes = json.loads((root / "nodes.json").read_text())
memory = json.loads((root / "memory-protocol.json").read_text())

assert nodes["schema_version"] == "0.1.0"
assert memory["schema_version"] == "0.1.0"

ids = [n["id"] for n in nodes["nodes"]]
assert len(ids) == len(set(ids)), "Duplicate node IDs"

for node in nodes["nodes"]:
    assert node["id"]
    assert node["region"]
    assert node["roles"]
    assert node["capabilities"]
    assert node["status"] in {
        "online", "offline", "unknown", "planned"
    }

security = memory["security"]
assert security["deny_by_default"] is True
assert security["authentication_required"] is True
assert security["private_memory_replication"] == "disabled"
assert security["collaborative_writes"] == "staging-only"

tools = [t["name"] for t in memory["tools"]]
assert len(tools) == len(set(tools))

print("MNEMORA FEDERATION VALIDATION: PASS")
print("Registered nodes:", len(ids))
print("Memory tools:", len(tools))
print("Private replication: disabled")
