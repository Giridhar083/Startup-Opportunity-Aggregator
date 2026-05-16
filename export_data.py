import csv
import json
import os
from datetime import datetime
from database import get_opportunities
from config import EXPORT_FOLDER


def _ensure_folder():
    os.makedirs(EXPORT_FOLDER, exist_ok=True)


def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def export_csv(keyword="", opp_type="", source=""):
    rows = get_opportunities(keyword=keyword, opp_type=opp_type, source=source)
    if not rows:
        return None

    _ensure_folder()
    path = os.path.join(EXPORT_FOLDER, f"opportunities_{_timestamp()}.csv")

    fieldnames = ["id", "title", "type", "organizer", "location", "deadline", "link", "source", "tags"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"[Export] CSV → {path} ({len(rows)} rows)")
    return path


def export_json(keyword="", opp_type="", source=""):
    rows = get_opportunities(keyword=keyword, opp_type=opp_type, source=source)
    if not rows:
        return None

    _ensure_folder()
    path = os.path.join(EXPORT_FOLDER, f"opportunities_{_timestamp()}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f"[Export] JSON → {path} ({len(rows)} rows)")
    return path


if __name__ == "__main__":
    from database import create_table
    create_table()
    print(export_csv())
    print(export_json())