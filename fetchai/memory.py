"""Durable per-department case memory and append-only event records.

Persistence supports inspection and later case work, not automatic execution recovery.
"""
import json
import sqlite3
import threading
import time
from pathlib import Path

class CaseMemory:
    def __init__(self, path):
        Path(path).parent.mkdir(exist_ok=True, parents=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, payload TEXT NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS memory (deal TEXT, role TEXT, payload TEXT, PRIMARY KEY(deal,role))')
        self.db.commit()

    def append(self, value):
        with self.lock:
            try:
                self.db.execute('INSERT INTO events(payload) VALUES (?)', (json.dumps(value),))
                self.db.commit()
            except sqlite3.Error:
                self.db.rollback()
                raise

    def read(self, deal, role):
        with self.lock:
            row = self.db.execute('SELECT payload FROM memory WHERE deal=? AND role=?', (deal, role)).fetchone()
        return json.loads(row[0]) if row else {'steps': [], 'open_questions': []}

    def remember(self, deal, role, step, data):
        with self.lock:
            record = self.read(deal, role)
            record['steps'].append({'at': time.time(), 'step': step, 'data': data})
            record['steps'] = record['steps'][-30:]
            try:
                self.db.execute('INSERT OR REPLACE INTO memory VALUES (?,?,?)', (deal, role, json.dumps(record)))
                self.db.commit()
            except sqlite3.Error:
                self.db.rollback()
                raise

    def snapshot(self):
        with self.lock:
            events = [json.loads(r[0]) for r in self.db.execute('SELECT payload FROM events ORDER BY id DESC LIMIT 20000')][::-1]
            memories = [{'deal': d, 'role': r, **json.loads(p)} for d,r,p in self.db.execute('SELECT * FROM memory')]
        return {'events': events, 'memories': memories}
