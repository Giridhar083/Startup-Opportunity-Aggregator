# deduplicate.py — removes duplicate opportunities before and after DB insert

import sqlite3
from config import DB_NAME


def deduplicate_list(opps):
    """Remove dupes from a list by checking the link field."""
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
    """Keep only the first row for each (title, organizer, deadline) combo."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM opportunities
        WHERE id NOT IN (
            SELECT MIN(id) FROM opportunities
            GROUP BY title, organizer, deadline
        )
    """)
    print(f"[Dedup] removed {cur.rowcount} DB duplicates")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    remove_duplicates_from_db()