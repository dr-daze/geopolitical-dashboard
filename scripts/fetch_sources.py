#!/usr/bin/env python3
"""
fetch_sources.py
=================

This script fetches news items from the RSS feeds defined in
`config/sources.yml`.  The feeds are grouped by signal stream (battlefield,
escalation, proxy, energy_shock, market_shock).  Each item is normalised
into a common schema and written to `data/news.json`.  A `status.json`
file records the last update time and the total number of items.  The
script avoids duplicating entries by comparing URLs.

Dependencies:

* `feedparser` – for parsing RSS/Atom feeds.
* `pyyaml` – for loading the YAML configuration.

You can install these with `pip install feedparser pyyaml`.

"""
import datetime
import json
import sys
from pathlib import Path

import yaml  # type: ignore

try:
    import feedparser  # type: ignore
except ImportError:
    print(
        "The feedparser library is required to run this script."
        " Please install it with 'pip install feedparser'.",
        file=sys.stderr,
    )
    sys.exit(1)


def parse_timestamp(entry: dict) -> str:
    """Attempt to derive an ISO 8601 timestamp for a feed entry."""
    # Prefer the published date, fall back to updated, then current time
    published = entry.get("published_parsed") or entry.get("updated_parsed")
    if published:
        try:
            dt = datetime.datetime(*published[:6], tzinfo=datetime.timezone.utc)
            return dt.isoformat()
        except Exception:
            pass
    # Fallback to ISO string in `published` or `updated` if present
    for key in ("published", "updated"):
        if key in entry:
            ts = entry[key]
            # Leave as provided; downstream code may parse
            return str(ts)
    # Last resort: now
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()


def main() -> None:
    """Entrypoint for fetching RSS feeds and updating JSON files."""
    # Determine repository root from script location
    repo_dir = Path(__file__).resolve().parents[1]
    config_path = repo_dir / "config" / "sources.yml"
    data_dir = repo_dir / "data"
    data_dir.mkdir(exist_ok=True)

    # Load configuration
    with open(config_path, "r", encoding="utf-8") as f:
        sources = yaml.safe_load(f) or {}

    new_entries = []

    # Iterate over categories and sources
    for category, src_list in sources.items():
        if not isinstance(src_list, list):
            continue
        for src in src_list:
            rss = src.get("rss")
            if not rss:
                # Skip sources without RSS feeds; manual ingestion would be required
                continue
            name = src.get("name", "Unknown")
            region = src.get("region", "")
            try:
                feed = feedparser.parse(rss)
            except Exception as e:
                print(f"Failed to parse feed {rss}: {e}", file=sys.stderr)
                continue
            for entry in getattr(feed, "entries", []):
                ts = parse_timestamp(entry)
                url = entry.get("link", "").strip()
                title = entry.get("title", "").strip()
                summary = (
                    entry.get("summary")
                    or entry.get("description")
                    or entry.get("content", [{}])[0].get("value", "")
                )
                summary = summary.strip()
                new_entries.append(
                    {
                        "timestamp": ts,
                        "source": name,
                        "title": title,
                        "url": url,
                        "category": category,
                        "region": region,
                        "summary": summary,
                        "tags": [category],
                    }
                )

    # Load existing news (if any)
    news_path = data_dir / "news.json"
    existing: list = []
    if news_path.exists():
        try:
            with open(news_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    # Build a URL set for deduplication
    seen_urls = {e.get("url"): True for e in existing if e.get("url")}
    for entry in new_entries:
        url = entry.get("url")
        if url and url not in seen_urls:
            existing.append(entry)
            seen_urls[url] = True

    # Sort by timestamp descending
    def parse_ts(ts: str) -> datetime.datetime:
        try:
            return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            return datetime.datetime.min

    existing.sort(key=lambda x: parse_ts(x.get("timestamp", "")), reverse=True)

    # Write back news.json
    with open(news_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    # Update status.json
    status_path = data_dir / "status.json"
    status = {
        "last_updated": datetime.datetime.utcnow()
        .replace(tzinfo=datetime.timezone.utc)
        .isoformat(),
        "news_count": len(existing),
    }
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()