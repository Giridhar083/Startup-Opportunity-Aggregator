# Startup Opportunity Aggregator

A web scraping pipeline that collects startup-related opportunities (grants, accelerators, funding) from multiple public sources, stores them in a database, removes duplicates, and displays them in a searchable dashboard.

---

## Setup & Installation

### With Docker (Recommended)

```bash
docker-compose up --build -d
```

Dashboard runs at **http://localhost:5000**

Trigger first scrape:
```
http://localhost:5000/scrape?keyword=startup
```

### Without Docker

```bash
pip install -r requirements.txt
python scheduler_job.py 
python app.py 
```

---

## Sources Used

| Source | Type | Method | Updates |
|--------|------|--------|---------|
| [Google RSS – Global](https://news.google.com) | Accelerators / Incubators | RSS Feed | Real-time |
| [Google RSS – India](https://news.google.com) | Grants / Funding | RSS Feed | Real-time |

Both sources use Google News RSS which aggregates from hundreds of publishers. Queries are tuned for startup opportunities — new results appear automatically every 6 hours when the scheduler runs.

---

## Project Structure

```
├── scraper.py          # RSS scrapers for both sources
├── database.py         # SQLite setup, queries, migration
├── deduplicate.py      # Remove duplicates (list + DB level)
├── ai_tagger.py        # Auto-tag: work mode, stage, funding
├── scheduler_job.py    # Runs full pipeline every 6 hours
├── app.py              # Flask dashboard (search, filter, export)
├── export_data.py      # Export to CSV / JSON
├── config.py           # Centralized settings
├── templates/
│   └── index.html      # Dashboard UI
├── static/
│   └── style.css       # Styling
├── requirements.txt
├── docker-compose.yml
└── data/
    └── opportunities.db  # SQLite database (auto-created)
```

---

## Features

- Search by keyword across title, organizer, location
- Filter by opportunity type and source
- Sort by deadline (ascending / descending)
- Auto-tagging: Remote/On-site, startup stage, funding type
- Export filtered results to CSV or JSON
- Manual scrape trigger from dashboard
- Scheduled auto-scrape every 6 hours via APScheduler
- Docker setup with separate web and scheduler containers

---

## Scraping Challenges & How They Were Handled

**1. No dedicated startup opportunity API**
Most startup opportunity platforms (Devpost, Startup India, Y Combinator) either have no public API or use JavaScript rendering that blocks BeautifulSoup. Solution: used Google News RSS feeds with targeted queries to aggregate opportunity announcements from hundreds of publishers in real time.

**2. Duplicate entries across scrape runs**
Running the scraper every 6 hours with overlapping RSS results causes duplicates. Handled at two levels — a `UNIQUE` constraint on the `link` column in SQLite blocks exact duplicates on insert, and a post-insert SQL cleanup removes rows with the same `title + organizer + deadline` combination.

**3. Schema changes on existing database**
When the `tags` column was added after initial deployment, existing databases crashed on insert. Fixed with an `ALTER TABLE` migration that runs safely on every startup and skips if the column already exists.

**4. Containerized network restrictions**
Some government APIs (MyScheme.gov.in) block requests from Docker container IPs. The scraper handles this with try/except — if a source fails, the pipeline continues with remaining sources without crashing.

**5. Missing deadline dates**
RSS feeds don't always include application deadlines. Used `entry.published` (the article publish date) as a proxy deadline, which at minimum shows when the opportunity was announced.

---

## Bonus Features Completed

- AI auto-tagging (work mode, startup stage, funding type)
- Export to CSV and JSON
- Docker with multi-container setup
- Basic anti-scraping via User-Agent header in config
