# Startup Opportunity Aggregator

A web scraping pipeline that collects startup-related opportunities (grants, accelerators, funding) from multiple public sources, stores them in SQLite, removes duplicates, and displays them in a searchable dashboard.

---

## 🚀 Live Deployment (Render)

### Option A — One-click via render.yaml

1. Push this repo to GitHub.
2. Go to [https://dashboard.render.com](https://dashboard.render.com) → **New → Blueprint**.
3. Connect your GitHub repo — Render will detect `render.yaml` automatically.
4. Click **Apply** and wait ~3 minutes for the build.
5. Your dashboard will be live at the URL Render provides (e.g. `https://startup-opportunity-aggregator.onrender.com`).

> **Note:** The free tier spins down after 15 minutes of inactivity. The first request after sleep may take ~30 seconds to wake up.

### Option B — Manual Render setup

1. Push the repo to GitHub.
2. Render dashboard → **New → Web Service** → connect repo.
3. Set **Runtime** to **Docker**.
4. Set **Port** to `10000`.
5. Under **Disks** → add a disk: mount path `/app/data`, size 1 GB (keeps the SQLite DB persistent between deploys).
6. Click **Create Web Service**.

### Trigger first scrape

After deploy, visit:
```
https://<your-render-url>/scrape?keyword=AI+startup
```

The scheduler also runs automatically every 6 hours in the background.

---

## 🐳 Local Docker (original setup)

```bash
docker-compose up --build -d
```

Dashboard: **http://localhost:5000**

---

## 💻 Local without Docker

```bash
pip install -r requirements.txt
python app.py
```

Dashboard: **http://localhost:10000**

> The scheduler and Flask server run together in one process — no separate `scheduler_job.py` needed.

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
├── app.py              # Flask dashboard + embedded APScheduler
├── scraper.py          # RSS scrapers for both sources
├── database.py         # SQLite setup, queries, migration
├── deduplicate.py      # Remove duplicates (list + DB level)
├── ai_tagger.py        # Auto-tag: work mode, stage, funding
├── scheduler_job.py    # Standalone scheduler (Docker Compose only)
├── export_data.py      # Export to CSV / JSON
├── config.py           # Centralized settings
├── templates/
│   └── index.html      # Dashboard UI
├── static/
│   └── style.css       # Styling
├── requirements.txt
├── Dockerfile          # Single-service build (Render compatible)
├── render.yaml         # Render Blueprint config
├── docker-compose.yml  # Multi-container local dev setup
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
- Manual scrape trigger via `/scrape?keyword=...`
- Scheduled auto-scrape every 6 hours (runs in-process via APScheduler BackgroundScheduler)
- Single-service Render deployment (no separate scheduler container needed)

---

## Render vs Docker Compose — Architecture Difference

| | Docker Compose (local) | Render (production) |
|-|------------------------|---------------------|
| Web server | `web` container | Single web service |
| Scheduler | Separate `scheduler` container | `BackgroundScheduler` inside the web process |
| Port | 5000 | 10000 (Render default) |
| DB storage | `./data` volume mount | Render Persistent Disk at `/app/data` |

On Render, the `BlockingScheduler` in `scheduler_job.py` is not used. Instead, `app.py` starts a `BackgroundScheduler` in a daemon thread so the scraper runs on schedule within the same process as Flask.

---

## Scraping Challenges & How They Were Handled

**1. No dedicated startup opportunity API**
Most platforms (Devpost, YC, Startup India) have no public API or use JavaScript rendering. Solution: Google News RSS with targeted queries aggregates from hundreds of publishers in real time.

**2. Duplicate entries across scrape runs**
Handled at two levels — a `UNIQUE` constraint on the `link` column blocks exact duplicates on insert; a post-insert SQL cleanup removes rows with the same `title + organizer + deadline`.

**3. Schema changes on existing database**
The `tags` column was added after initial deployment. Fixed with an `ALTER TABLE` migration that runs safely on every startup and is silently skipped if the column already exists.

**4. Containerized network restrictions**
Some government APIs (MyScheme.gov.in) block requests from cloud IPs. The scraper handles this with try/except — if a source fails, the pipeline continues without crashing.

**5. Missing deadline dates**
RSS feeds don't always include application deadlines. `entry.published` (article publish date) is used as a proxy deadline, which at minimum shows when the opportunity was announced.

**6. Render ephemeral filesystem**
Render's default filesystem resets on every deploy, wiping SQLite data. Fixed by mounting a Render Persistent Disk at `/app/data` so the database survives restarts and redeploys.

---

## Bonus Features Completed

- AI auto-tagging (work mode, startup stage, funding type)
- Export to CSV and JSON
- Docker with multi-container setup (local dev)
- Single-service Render deployment (production)
- Basic anti-scraping via User-Agent header in config
