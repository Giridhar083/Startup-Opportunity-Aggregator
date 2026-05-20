import sqlite3
from config import DB_NAME

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = connect_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT,
            type      TEXT,
            organizer TEXT,
            location  TEXT,
            deadline  TEXT,
            link      TEXT UNIQUE,
            source    TEXT,
            tags      TEXT
        )
    """)
    conn.commit()
    try:
        conn.execute("ALTER TABLE opportunities ADD COLUMN tags TEXT")
        conn.commit()
    except:
        pass
    conn.close()

def insert_opportunity(data):
    conn = connect_db()
    try:
        conn.execute("""
            INSERT INTO opportunities
              (title, type, organizer, location, deadline, link, source, tags)
            VALUES
              (:title, :type, :organizer, :location, :deadline, :link, :source, :tags)
        """, data)
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_opportunities(keyword="", opp_type="", source="", sort="asc"):
    query = "SELECT * FROM opportunities WHERE 1=1"
    params = []

    if keyword:
        query += " AND (title LIKE ? OR organizer LIKE ? OR location LIKE ?)"
        like = f"%{keyword}%"
        params.extend([like, like, like])

    if opp_type:
        query += " AND type = ?"
        params.append(opp_type)

    if source:
        query += " AND source = ?"
        params.append(source)

    query += f" ORDER BY deadline {'ASC' if sort == 'asc' else 'DESC'}"

    conn = connect_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_distinct(column):
    conn = connect_db()
    rows = conn.execute(
        f"SELECT DISTINCT {column} FROM opportunities WHERE {column} IS NOT NULL"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_untagged():
    conn = connect_db()
    rows = conn.execute(
        "SELECT * FROM opportunities WHERE tags IS NULL OR tags = ''"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_tags(row_id, tags):
    conn = connect_db()
    conn.execute("UPDATE opportunities SET tags = ? WHERE id = ?", (tags, row_id))
    conn.commit()
    conn.close()