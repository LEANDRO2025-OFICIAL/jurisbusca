"""Banco de dados SQLite com FTS5 para busca de jurisprudencia."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "jurisbusca.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS acordaos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tribunal TEXT NOT NULL,
    numero TEXT,
    data_julgamento TEXT,
    relator TEXT,
    ementa TEXT,
    relatorio TEXT,
    voto TEXT,
    dispositivo TEXT,
    area TEXT,
    tema TEXT,
    url_origem TEXT,
    pdf_url TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS acordaos_fts USING fts5(
    tribunal, numero, ementa, relatorio, voto, dispositivo, area, tema,
    content='acordaos', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS acordaos_ai AFTER INSERT ON acordaos BEGIN
    INSERT INTO acordaos_fts(rowid, tribunal, numero, ementa, relatorio, voto, dispositivo, area, tema)
    VALUES (new.id, new.tribunal, new.numero, new.ementa, new.relatorio, new.voto, new.dispositivo, new.area, new.tema);
END;

CREATE TRIGGER IF NOT EXISTS acordaos_ad AFTER DELETE ON acordaos BEGIN
    INSERT INTO acordaos_fts(acordaos_fts, rowid, tribunal, numero, ementa, relatorio, voto, dispositivo, area, tema)
    VALUES ('delete', old.id, old.tribunal, old.numero, old.ementa, old.relatorio, old.voto, old.dispositivo, old.area, old.tema);
END;

CREATE TRIGGER IF NOT EXISTS acordaos_au AFTER UPDATE ON acordaos BEGIN
    INSERT INTO acordaos_fts(acordaos_fts, rowid, tribunal, numero, ementa, relatorio, voto, dispositivo, area, tema)
    VALUES ('delete', old.id, old.tribunal, old.numero, old.ementa, old.relatorio, old.voto, old.dispositivo, old.area, old.tema);
    INSERT INTO acordaos_fts(rowid, tribunal, numero, ementa, relatorio, voto, dispositivo, area, tema)
    VALUES (new.id, new.tribunal, new.numero, new.ementa, new.relatorio, new.voto, new.dispositivo, new.area, new.tema);
END;
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def insert_acordao(data: dict) -> int:
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO acordaos (tribunal, numero, data_julgamento, relator, ementa,
           relatorio, voto, dispositivo, area, tema, url_origem, pdf_url)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data.get("tribunal"),
            data.get("numero"),
            data.get("data_julgamento"),
            data.get("relator"),
            data.get("ementa"),
            data.get("relatorio"),
            data.get("voto"),
            data.get("dispositivo"),
            data.get("area"),
            data.get("tema"),
            data.get("url_origem"),
            data.get("pdf_url"),
        ),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def search(query: str, tribunal: str = None, area: str = None, limit: int = 20):
    conn = get_conn()
    sql = """
        SELECT a.id, a.tribunal, a.numero, a.data_julgamento, a.relator,
               a.ementa, a.area, a.tema, a.url_origem,
               snippet(acordaos_fts, 2, '<mark>', '</mark>', '...', 32) AS snippet
        FROM acordaos_fts f
        JOIN acordaos a ON a.id = f.rowid
        WHERE acordaos_fts MATCH ?
    """
    params = [query]
    if tribunal:
        sql += " AND a.tribunal = ?"
        params.append(tribunal)
    if area:
        sql += " AND a.area = ?"
        params.append(area)
    sql += " ORDER BY rank LIMIT ?"
    params.append(limit)
    try:
        rows = conn.execute(sql, params).fetchall()
    except Exception:
        # fallback: busca simples
        rows = conn.execute(
            "SELECT id, tribunal, numero, data_julgamento, relator, ementa, area, tema, url_origem, ementa AS snippet FROM acordaos WHERE ementa LIKE ? LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_acordao(acordao_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM acordaos WHERE id = ?", (acordao_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def count_acordaos():
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) FROM acordaos").fetchone()[0]
    conn.close()
    return n


def list_tribunais():
    conn = get_conn()
    rows = conn.execute(
        "SELECT DISTINCT tribunal FROM acordaos ORDER BY tribunal"
    ).fetchall()
    conn.close()
    return [r["tribunal"] for r in rows]


def list_areas():
    conn = get_conn()
    rows = conn.execute(
        "SELECT DISTINCT area FROM acordaos WHERE area IS NOT NULL ORDER BY area"
    ).fetchall()
    conn.close()
    return [r["area"] for r in rows]


if __name__ == "__main__":
    init_db()
    print("Banco inicializado:", DB_PATH)
    print("Total de acordãos:", count_acordaos())
