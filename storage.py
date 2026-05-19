"""本地SQLite存储 — 数据持久化."""

import sqlite3, json
from datetime import datetime
from typing import Optional


class Storage:
    def __init__(self, db_path: str = "gateway.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS device_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                device_type TEXT NOT NULL,
                sheep_id TEXT,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_device_ts ON device_readings(device_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_sheep_ts ON device_readings(sheep_id, timestamp);
        """)
        self.conn.commit()

    def insert(self, device_type: str, data_obj) -> int:
        d = data_obj.__dict__ if hasattr(data_obj, '__dict__') else data_obj
        cur = self.conn.execute(
            "INSERT INTO device_readings (device_id, device_type, sheep_id, data, timestamp) VALUES (?, ?, ?, ?, ?)",
            (d.get("device_id", ""), device_type, d.get("sheep_id", ""),
             json.dumps(d, ensure_ascii=False), d.get("timestamp", datetime.now().isoformat())),
        )
        self.conn.commit()
        return cur.lastrowid

    def query(self, device_id: str = None, sheep_id: str = None, limit: int = 100) -> list[dict]:
        sql = "SELECT * FROM device_readings WHERE 1=1"
        params = []
        if device_id:
            sql += " AND device_id = ?"
            params.append(device_id)
        if sheep_id:
            sql += " AND sheep_id = ?"
            params.append(sheep_id)
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(sql, params).fetchall()
        return [{"id": r[0], "device_id": r[1], "device_type": r[2],
                 "sheep_id": r[3], "data": json.loads(r[4]), "timestamp": r[5]} for r in rows]

    def stats(self) -> dict:
        total = self.conn.execute("SELECT COUNT(*) FROM device_readings").fetchone()[0]
        types = self.conn.execute(
            "SELECT device_type, COUNT(*) FROM device_readings GROUP BY device_type"
        ).fetchall()
        return {"total_readings": total, "by_type": dict(types)}

    def close(self):
        self.conn.close()
