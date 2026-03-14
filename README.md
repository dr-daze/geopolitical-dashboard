# Geopolitical Intelligence Dashboard

This repository contains a minimal yet functional **Geopolitical Intelligence Dashboard**.  The system ingests open‑source news and market data, categorises the information into strategic signal streams and exposes the results through a static web interface.  The architecture is intentionally simple and relies only on free data feeds to stay within the constraints of typical free‑tier cloud hosting.

## Overview

The dashboard is organised around the three major signal streams identified in the problem statement:

1. **Battlefield updates** – situational awareness and territorial developments drawn from trusted military analysis outlets.
2. **Escalation signals** – monitoring of troop deployments, weapons shipments and alliance posture changes.
3. **Economic shocks** – watching energy and financial markets for early warning of systemic stress.

Incoming items are normalised into a common JSON schema and stored in the `data/` directory.  The front‑end in `site/` reads these JSON files and renders four panels: battlefield updates, escalation signals, energy shock monitor and financial stress indicators.  A simple filter bar lets you narrow results by category or region.  Automation is handled by a GitHub Actions workflow under `.github/workflows/update.yml`, which fetches fresh data on a regular schedule.

## Directory structure

```
geopolitical-dashboard/
├── data/              # JSON data files written by the update scripts
│   ├── news.json      # normalised news items
│   ├── markets.json   # energy and market indicators
│   └── status.json    # status metadata such as last update timestamps
├── config/            # configuration files
│   └── sources.yml    # declarative list of sources and their categories
├── scripts/           # update and classification scripts
│   ├── fetch_sources.py    # fetches news items from RSS feeds
│   ├── classify_signals.py # assigns additional tags to news items
│   └── fetch_markets.py    # downloads market data using yfinance
├── site/              # static dashboard
│   ├── index.html     # main HTML page
│   ├── app.js         # JavaScript for dynamic rendering and filtering
│   └── styles.css     # simple styling
└── .github/
    └── workflows/
        └── update.yml # GitHub Actions workflow for scheduled updates
```

## JSON schema

Every news entry in `news.json` follows this schema:

```json
{
  "timestamp": "2026-03-14T12:34:56Z",   // ISO 8601 UTC timestamp of the event or publication
  "source": "Institute for the Study of War", // human‑readable name of the origin
  "title": "ISW update: Russian advances in Avdiivka", // short headline
  "url": "https://example.com/article",  // canonical URL for the item
  "category": "battlefield",              // primary signal stream: battlefield, escalation, proxy, energy_shock or market_shock
  "region": "Russia‑Ukraine",             // region or theatre of conflict
  "summary": "A brief text summary of the event", // plain‑text summary or description
  "tags": ["battlefield", "Russia", "Ukraine"] // list of tags for further filtering
}
```

The `markets.json` file holds an array of market indicator objects with at least `timestamp`, `symbol`, `name` and `price` fields.  `status.json` stores metadata like the last update timestamp and the number of news items processed.

## Configuration

The `config/sources.yml` file specifies the news sources used for each signal stream.  You can add or remove sources by editing this file.  Each source block includes a `name`, an optional `rss` feed URL and a default `region`.  Additional metadata can be added as needed by the ingestion scripts.

## Updating

The scripts in `scripts/` can be run manually or by GitHub Actions.  They are designed to be idempotent: running them multiple times will not duplicate existing entries.  When run as part of the scheduled workflow, the scripts will fetch new items, classify them, update `news.json`, update `markets.json` and write a `status.json` file.  The workflow commits any changes back to the repository.

## Live dashboard

To view the dashboard locally, serve the `site/` directory with any static file server (e.g. `python -m http.server`).  When hosted via GitHub Pages or a similar service, the dashboard will automatically read the JSON files and display the latest data.

## References

The dashboard draws upon a number of open sources for its data.  For example, reports note that the Strait of Hormuz normally carries roughly a fifth of the world’s daily oil and liquefied natural gas supply, so disruptions there can trigger major energy price spikes【85717772307401†L30-L34】.  Argus Media describes how their freight services provide daily shipping indexes and market analysis for crude and gas markets, allowing industry participants and analysts to understand shipping costs and risks【472414531983570†L351-L365】.  These kinds of energy and freight indicators inform the energy shock and financial stress panels in the dashboard.