from flask import Flask, render_template, request, jsonify, send_file
from database    import create_table, get_opportunities, get_distinct, insert_opportunity
from scraper     import scrape_all
from deduplicate import deduplicate_list, remove_duplicates_from_db
from ai_tagger   import run_tagging
from export_data import export_csv, export_json

app = Flask(__name__)
create_table()


@app.route("/")
def index():
    keyword  = request.args.get("keyword", "").strip()
    opp_type = request.args.get("type", "").strip()
    source   = request.args.get("source", "").strip()
    sort     = request.args.get("sort", "asc")

    opps = get_opportunities(keyword=keyword, opp_type=opp_type, source=source, sort=sort)

    return render_template(
        "index.html",
        opportunities = opps,
        all_types     = get_distinct("type"),
        all_sources   = get_distinct("source"),
        keyword=keyword, opp_type=opp_type, source=source, sort=sort,
        total=len(opps),
    )


@app.route("/scrape")
def manual_scrape():
    keyword = request.args.get("keyword", "AI startup")
    raw     = scrape_all(keyword)
    clean   = deduplicate_list(raw)
    saved   = sum(1 for o in clean if insert_opportunity(o))
    remove_duplicates_from_db()
    run_tagging()
    return jsonify({"status": "ok", "scraped": len(raw), "inserted": saved})

@app.route("/export/csv")
def download_csv():
    path = export_csv(
        keyword  = request.args.get("keyword", ""),
        opp_type = request.args.get("type", ""),
        source   = request.args.get("source", ""),
    )
    if not path:
        return "No data", 404
    return send_file(path, as_attachment=True, download_name="opportunities.csv")


@app.route("/export/json")
def download_json():
    path = export_json(
        keyword  = request.args.get("keyword", ""),
        opp_type = request.args.get("type", ""),
        source   = request.args.get("source", ""),
    )
    if not path:
        return "No data", 404
    return send_file(path, as_attachment=True, download_name="opportunities.json")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)