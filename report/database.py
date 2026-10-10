"""Traçabilité : chaque campagne et chaque verdict sont enregistrés dans SQLite."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT UNIQUE, started_at TEXT, mode TEXT, serial_number TEXT,
    firmware TEXT, git_commit TEXT, passed INTEGER, n_tests INTEGER, n_failed INTEGER
);
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT, test_id TEXT, title TEXT, verdict TEXT, criterion TEXT, measures_json TEXT,
    FOREIGN KEY (run_id) REFERENCES campaigns(run_id)
);
"""


def save_campaign(db_path: Path, meta: dict, results: list) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.executescript(SCHEMA)
        failed = sum(not r.passed for r in results)
        con.execute(
            "INSERT OR REPLACE INTO campaigns (run_id, started_at, mode, serial_number, firmware, git_commit,"
            " passed, n_tests, n_failed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (meta["run_id"], meta["started_at"], meta["mode"], meta["serial_number"], meta["firmware"],
             meta["git_commit"], int(failed == 0), len(results), failed))
        con.execute("DELETE FROM results WHERE run_id = ?", (meta["run_id"],))
        con.executemany(
            "INSERT INTO results (run_id, test_id, title, verdict, criterion, measures_json)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            [(meta["run_id"], r.test_id, r.title, r.verdict, r.criterion,
              json.dumps(r.measures, ensure_ascii=False, default=float)) for r in results])
