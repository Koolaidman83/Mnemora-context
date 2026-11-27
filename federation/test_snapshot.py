import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from snapshot import snapshot

class SnapshotTests(unittest.TestCase):
    def test_sanitized_and_freshness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / 'fabric.sqlite3'
            with sqlite3.connect(db) as c:
                c.execute('CREATE TABLE nodes (node_id text, url text, capabilities text, metrics text, meta text, last_seen integer)')
                c.executemany('INSERT INTO nodes VALUES (?,?,?,?,?,?)', [
                    ('mike6', 'http://192.168.1.31:8793', '[]', '{"secret":"NO"}', '{}', 990),
                    ('other-private', 'http://secret:8793', '[]', '{}', '{}', 1000),
                ])
            reg = root / 'nodes.json'
            reg.write_text(json.dumps({'nodes': [
                {'id':'mike6', 'region':'us-east', 'roles':['memory-primary'], 'status':'unknown'},
                {'id':'mnemora-pacific', 'region':'ap-southeast', 'roles':[], 'status':'planned'}]}))
            result = snapshot(db, reg, timestamp=1000, age=120)
            encoded = json.dumps(result)
            self.assertTrue(result['nodes'][0]['observed_recently'])
            self.assertFalse(result['nodes'][1]['observed_recently'])
            self.assertNotIn('192.168', encoded)
            self.assertNotIn('other-private', encoded)
            self.assertNotIn('secret', encoded)
    def test_old_heartbeat_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root/'db.sqlite3'
            with sqlite3.connect(db) as c:
                c.execute('CREATE TABLE nodes (node_id text, last_seen integer)')
                c.execute('INSERT INTO nodes VALUES (?,?)', ('tcl', 100))
            reg = root/'nodes.json'
            reg.write_text('{"nodes":[{"id":"tcl"}]}')
            self.assertFalse(snapshot(db,reg,timestamp=300)['nodes'][0]['observed_recently'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
