import sqlite3
from config import DB_NAME


def deduplicate_list(opps):
    seen = set()
    clean = []
    for opp in opps:
        link = opp.get("link", "")
        if link and link not in seen:
            seen.add(link)
            clean.append(opp)
    print(f"[Dedup] {len(opps)} → {len(clean)} (removed {len(opps) - len(clean)})")
    return clean


def remove_duplicates_from_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # delete rows with duplicate links, keep the first one
    cur.execute("""
        DELETE FROM opportunities
        WHERE id NOT IN (
            SELECT MIN(id) FROM opportunities GROUP BY link
        )
    """)
    print(f"[Dedup] removed {cur.rowcount} duplicates from DB")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    remove_duplicates_from_db()