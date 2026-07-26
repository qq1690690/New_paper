"""Append summarized articles as rows to a Google Sheet via a service account."""
import json
import os
from datetime import datetime, timezone

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_HEADER = [
    "Date",
    "Journal",
    "Title",
    "Authors",
    "Link",
    "Introduction",
    "Methods",
    "Results",
    "Discussion",
    "Conclusion",
]


def _get_client():
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        return None

    import gspread
    from google.oauth2.service_account import Credentials

    info = json.loads(creds_json)
    credentials = Credentials.from_service_account_info(info, scopes=_SCOPES)
    return gspread.authorize(credentials)


def append_articles(articles):
    """Append each article as a row to the configured Google Sheet.

    Returns False (no-op) if GOOGLE_SHEETS_ID or GOOGLE_SERVICE_ACCOUNT_JSON
    aren't set, so the pipeline degrades gracefully rather than failing.
    """
    sheet_id = os.environ.get("GOOGLE_SHEETS_ID")
    client = _get_client()
    if not sheet_id or not client:
        print("Google Sheets output not configured; skipping sheet append.")
        return False

    if not articles:
        return False

    sheet = client.open_by_key(sheet_id).sheet1
    if not sheet.row_values(1):
        sheet.append_row(_HEADER)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = []
    for article in articles:
        authors = ", ".join(article["authors"][:5])
        if len(article["authors"]) > 5:
            authors += ", et al."
        sections = article["sections"]
        rows.append(
            [
                today,
                article["journal"],
                article["title"],
                authors,
                article["link"],
                sections["introduction"],
                sections["methods"],
                sections["results"],
                sections["discussion"],
                sections["conclusion"],
            ]
        )

    sheet.append_rows(rows, value_input_option="RAW")
    return True
