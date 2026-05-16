import feedparser
from config import REQUEST_TIMEOUT


# Source 1: Google RSS — Global Accelerators & Incubators
def scrape_accelerators_rss():
    results = []
    print("[Global RSS] scraping...")

    rss_url = "https://news.google.com/rss/search?q=startup+accelerator+applications+open+OR+incubator+deadline&hl=en-US&gl=US&ceid=US:en"

    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:15]:
            results.append({
                "title":     entry.title,
                "type":      "Accelerator",
                "source":    "Global RSS",
                "organizer": entry.source.title if hasattr(entry, "source") else "Various",
                "location":  "Global / Remote",
                "deadline":  entry.get("published", "Check Link"),
                "link":      entry.link,
                "tags":      "",
            })
    except Exception as e:
        print(f"[Global RSS] failed: {e}")

    print(f"[Global RSS] got {len(results)} results")
    return results


# Source 2: Google RSS — Indian Startup Grants
def scrape_google_rss():
    results = []
    print("[India RSS] scraping...")

    rss_url = "https://news.google.com/rss/search?q=startup+grant+OR+funding+deadline+india&hl=en-IN&gl=IN&ceid=IN:en"

    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:15]:
            results.append({
                "title":     entry.title,
                "type":      "Grant/Funding",
                "source":    "India RSS",
                "organizer": entry.source.title if hasattr(entry, "source") else "Various",
                "location":  "Pan India",
                "deadline":  entry.get("published", "Check Link"),
                "link":      entry.link,
                "tags":      "",
            })
    except Exception as e:
        print(f"[India RSS] failed: {e}")

    print(f"[India RSS] got {len(results)} results")
    return results


def scrape_all(keyword="startup"):
    all_results = scrape_accelerators_rss() + scrape_google_rss()
    print(f"[Scraper] total: {len(all_results)}")
    return all_results


if __name__ == "__main__":
    from database import create_table, insert_opportunity
    from deduplicate import deduplicate_list
    create_table()
    raw = scrape_all()
    clean = deduplicate_list(raw)
    saved = sum(1 for o in clean if insert_opportunity(o))
    print(f"Saved {saved} new opportunities.")