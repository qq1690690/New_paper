"""Track which PMIDs have already been emailed so digests never repeat an article."""
import json
import os

_MAX_TRACKED = 5000


def load_seen_ids(path):
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_seen_ids(path, seen_ids):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    trimmed = list(seen_ids)[-_MAX_TRACKED:]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2)
