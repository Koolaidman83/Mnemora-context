import json
import tempfile
import unittest
from pathlib import Path
from federation_adapter import FederationPolicy

class Coordinator:
    def __init__(self, nodes):
        self.db = self
        self._nodes = nodes
    def nodes(self):
        return self._nodes
    def active_counts(self):
        return {}
    def node_score(self, n, cap):
        return n.get('metrics', {}).get('ram_available_mb', 0)

class TestPolicy(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root/'nodes.json').write_text(json.dumps({'nodes': [
            {'id': 'mike6', 'region': 'us-east', 'visibility': 'private', 'status': 'unknown'},
            {'id': 'pacific', 'region': 'ap-southeast', 'visibility': 'collaborative', 'status': 'planned'}]}))
        (root/'policy.json').write_text((Path(__file__).parent/'policy.json').read_text())
        self.p = FederationPolicy(root/'nodes.json', root/'policy.json')
        self.mike = {'node_id': 'mike6', 'online': True, 'capabilities': ['python'], 'metrics': {'ram_available_mb': 300}}
        self.pacific = {'node_id': 'pacific', 'online': True, 'capabilities': ['python'], 'metrics': {'ram_available_mb': 5000}}
    def tearDown(self):
        self.tmp.cleanup()
    def test_known_node(self):
        self.assertEqual(self.p.allowed(self.mike, 'python'), (True, 'allowed'))
    def test_private_placement(self):
        self.assertEqual(self.p.allowed(self.mike, 'python', 'private-memory'), (True, 'allowed'))
    def test_planned_denied(self):
        self.assertEqual(self.p.allowed(self.pacific, 'python')[1], 'planned-node')
    def test_unknown_denied(self):
        self.assertEqual(self.p.allowed(dict(self.mike, node_id='unregistered'), 'python')[1], 'unregistered-node')
    def test_offline_denied(self):
        self.assertEqual(self.p.allowed(dict(self.mike, online=False), 'python')[1], 'offline')
    def test_unknown_workload_denied(self):
        self.assertEqual(self.p.allowed(self.mike, 'python', 'secret')[1], 'unknown-workload')
    def test_target_cannot_bypass_policy(self):
        self.assertIsNone(self.p.choose(Coordinator([self.mike, self.pacific]), 'python', target_node='pacific'))
    def test_choose(self):
        self.assertEqual(self.p.choose(Coordinator([self.mike, self.pacific]), 'python')['node_id'], 'mike6')

if __name__ == '__main__':
    unittest.main(verbosity=2)
