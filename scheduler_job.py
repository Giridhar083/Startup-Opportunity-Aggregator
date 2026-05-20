from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

from config import SCRAPE_INTERVAL_HOURS  # Updated import
from database import create_table, insert_opportunity
from scraper import scrape_all
from deduplicate import deduplicate_list, remove_duplicates_from_db
from ai_tagger import run_tagging


def run_pipeline():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] pipeline starting...")

    raw = scrape_all()
    clean = deduplicate_list(raw)

    saved = sum(1 for o in clean if insert_opportunity(o))
    print(f"[Pipeline] saved {saved} new opportunities")

    remove_duplicates_from_db()
    run_tagging()

    print("[Pipeline] done\n")


if __name__ == "__main__":
    create_table()
    run_pipeline()

    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, "interval", hours=SCRAPE_INTERVAL_HOURS)

    print(f"Scheduler running, next scrape in {SCRAPE_INTERVAL_HOURS} hours. Ctrl+C to stop.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("Stopped.")
