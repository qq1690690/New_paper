"""Orchestrate: fetch new articles -> summarize -> email -> record seen PMIDs."""
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(__file__))

from email_digest import send_digest
from fetch_papers import fetch_recent_articles
from state import load_seen_ids, save_seen_ids
from summarize import summarize_articles

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seen_ids.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def require_env(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main():
    config = load_config()

    sender = require_env("GMAIL_ADDRESS")
    app_password = require_env("GMAIL_APP_PASSWORD")
    recipient = os.environ.get(config.get("recipient_env", "RECIPIENT_EMAIL")) or sender

    seen_ids = load_seen_ids(STATE_PATH)

    articles = fetch_recent_articles(
        config["journals"], config["days_back"], config["max_results_per_journal"]
    )
    new_articles = [a for a in articles if a["pmid"] not in seen_ids]

    if not new_articles:
        print("No new articles found; skipping email.")
        return

    summarize_articles(new_articles, config["model"])
    send_digest(recipient, sender, app_password, new_articles)

    seen_ids.update(a["pmid"] for a in new_articles)
    save_seen_ids(STATE_PATH, seen_ids)

    print(f"Sent digest with {len(new_articles)} article(s) to {recipient}.")


if __name__ == "__main__":
    main()
