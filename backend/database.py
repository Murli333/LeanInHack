"""
ScamLens SQLite Database Layer
Provides persistent storage, ACID transactions, and thread-safe operations for scan lifecycle management.
"""
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).resolve().parent / "scamlens.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db():
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    steps TEXT NOT NULL,
                    result TEXT,
                    error TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status)")
    finally:
        conn.close()


def save_scan(scan_dict: Dict[str, Any]):
    conn = get_db_connection()
    try:
        now = datetime.now(timezone.utc).isoformat()
        steps_json = json.dumps(scan_dict.get("steps", []))
        result_json = json.dumps(scan_dict.get("result")) if scan_dict.get("result") else None
        
        with conn:
            conn.execute("""
                INSERT INTO scans (id, type, content, title, status, created_at, updated_at, steps, result, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    type = excluded.type,
                    content = excluded.content,
                    title = excluded.title,
                    status = excluded.status,
                    updated_at = excluded.updated_at,
                    steps = excluded.steps,
                    result = excluded.result,
                    error = excluded.error
            """, (
                scan_dict["id"],
                scan_dict["type"],
                scan_dict["content"],
                scan_dict["title"],
                scan_dict["status"],
                scan_dict.get("createdAt") or now,
                now,
                steps_json,
                result_json,
                scan_dict.get("error")
            ))
    finally:
        conn.close()


def get_scan(scan_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
        row = cur.fetchone()
        if not row:
            return None
        
        steps = json.loads(row["steps"]) if row["steps"] else []
        result = json.loads(row["result"]) if row["result"] else None
        
        return {
            "id": row["id"],
            "type": row["type"],
            "content": row["content"],
            "title": row["title"],
            "status": row["status"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "steps": steps,
            "result": result,
            "error": row["error"]
        }
    finally:
        conn.close()


def list_scans(query: Optional[str] = None, scan_type: Optional[str] = None, risk: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        sql = "SELECT * FROM scans WHERE 1=1"
        params = []
        
        if scan_type and scan_type != "all":
            sql += " AND type = ?"
            params.append(scan_type)
            
        if query and query.strip():
            sql += " AND (title LIKE ? OR content LIKE ?)"
            q_like = f"%{query.strip()}%"
            params.extend([q_like, q_like])
            
        sql += " ORDER BY created_at DESC LIMIT 100"
        
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        
        scans = []
        for row in rows:
            steps = json.loads(row["steps"]) if row["steps"] else []
            result = json.loads(row["result"]) if row["result"] else None
            
            # Apply risk filter in Python since result is JSON
            if risk and risk != "all":
                if not result or result.get("riskLevel") != risk:
                    continue
                    
            scans.append({
                "id": row["id"],
                "type": row["type"],
                "content": row["content"],
                "title": row["title"],
                "status": row["status"],
                "createdAt": row["created_at"],
                "updatedAt": row["updated_at"],
                "steps": steps,
                "result": result,
                "error": row["error"]
            })
        return scans
    finally:
        conn.close()


def delete_scan(scan_id: str) -> bool:
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
            return cur.rowcount > 0
    finally:
        conn.close()


def delete_all_scans():
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("DELETE FROM scans")
    finally:
        conn.close()


def get_stats() -> Dict[str, int]:
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT result FROM scans")
        rows = cur.fetchall()
        total = len(rows)
        high_risk = 0
        for r in rows:
            if r["result"]:
                try:
                    res_obj = json.loads(r["result"])
                    if res_obj and res_obj.get("riskLevel") == "high":
                        high_risk += 1
                except Exception:
                    pass
        return {"total": total, "highRisk": high_risk}
    finally:
        conn.close()


# Initialize schema on module load
init_db()
