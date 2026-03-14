#!/usr/bin/env python3
"""
classify_signals.py
====================

This script reads the aggregated news items from `data/news.json` and
assigns additional tags based on simple keyword heuristics.  These tags
help refine the categorisation beyond the primary `category` field.  If
new tags are added, they are merged into the existing tag list.  The
script writes the updated list back to `data/news.json`.

The heuristics are intentionally lightweight and can be expanded to use
more sophisticated natural‑language processing in the future.  For
example, you could integrate OpenAI embeddings or a custom classifier
when the budget allows.
"""
import json
import re
from pathlib import Path


def apply_classification(entry: dict) -> list[str]:
    """Return a list of additional tags for a news entry."""
    text = f"{entry.get('title', '')} {entry.get('summary', '')}"
    text_lower = text.lower()
    tags: list[str] = []
    # Battlefield heuristics
    if re.search(r"\b(offensive|battle|frontline|shelling|advance|assault)\b", text_lower):
        tags.append("battlefield")
    # Escalation heuristics
    if re.search(r"\b(deployment|troop|naval|missile|mobilization|alliance)\b", text_lower):
        tags.append("escalation")
    # Proxy conflict heuristics
    if re.search(r"\b(hezbollah|houthi|militia|wagner|proxy)\b", text_lower):
        tags.append("proxy")
    # Energy shock heuristics
    if re.search(r"\b(brent|oil price|crude|lng|tanker|shipping|insurance)\b", text_lower):
        tags.append("energy_shock")
    # Market shock heuristics
    if re.search(r"\b(stock|futures|market|volatility|index)\b", text_lower):
        tags.append("market_shock")
    return tags


def main() -> None:
    repo_dir = Path(__file__).resolve().parents[1]
    news_path = repo_dir / "data" / "news.json"
    if not news_path.exists():
        print(f"News file not found: {news_path}")
        return
    with open(news_path, "r", encoding="utf-8") as f:
        items = json.load(f)
    for item in items:
        additional = apply_classification(item)
        existing_tags = set(item.get("tags", []))
        for tag in additional:
            if tag not in existing_tags:
                existing_tags.add(tag)
        item["tags"] = sorted(existing_tags)
    with open(news_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()