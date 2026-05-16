from database import get_untagged, update_tags


def generate_tags(opp):
    text = f"{opp.get('title','')} {opp.get('type','')} {opp.get('location','')} {opp.get('organizer','')}".lower()
    tags = []

    # Work mode
    if any(w in text for w in ["remote", "online", "virtual"]):
        tags.append("Remote")
    elif "hybrid" in text:
        tags.append("Hybrid")
    else:
        tags.append("On-site")

    # Startup stage
    if "pre-seed" in text or "idea stage" in text:
        tags.append("Pre-seed")
    elif "seed" in text:
        tags.append("Seed Stage")
    elif "series a" in text or "growth" in text:
        tags.append("Growth Stage")
    else:
        tags.append("Any Stage")

    if any(w in text for w in ["grant", "prize", "award", "funded", "$"]):
        tags.append("Funded")
    elif any(w in text for w in ["equity", "investment"]):
        tags.append("Equity")

    return ", ".join(tags)

def run_tagging():
    rows = get_untagged()
    if not rows:
        print("[Tagger] nothing to tag")
        return
    for opp in rows:
        tags = generate_tags(opp)
        update_tags(opp["id"], tags)
        print(f"  tagged [{opp['id']}]: {tags}")
    print(f"[Tagger] tagged {len(rows)} rows")

if __name__ == "__main__":
    from database import create_table
    create_table()
    run_tagging()