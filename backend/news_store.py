import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
NEWS_FILE = os.path.join(DATA_DIR, "news.json")


def load_news() -> list:
    if os.path.exists(NEWS_FILE):
        try:
            with open(NEWS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_news(news_list: list):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)


def merge_news(existing: list, new_items: list) -> list:
    seen_ids = {item["id"] for item in existing}
    for item in new_items:
        if item["id"] not in seen_ids:
            existing.append(item)
            seen_ids.add(item["id"])

    existing.sort(key=lambda x: x.get("time", ""), reverse=True)
    return existing


def update_news(new_items: list) -> list:
    existing = load_news()
    merged = merge_news(existing, new_items)
    save_news(merged)
    return merged
