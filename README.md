# New_paper

CID and the lancet infectious disease new paper

Daily email digest of new articles from *The Lancet Infectious Diseases* and
*Clinical Infectious Diseases*, summarized with OpenAI, with each summary also
logged as a row in a Google Sheet. Runs automatically via GitHub Actions.

## How it works

1. `src/fetch_papers.py` queries the PubMed E-utilities API for articles
   published in the configured journals (`config.yaml`) within the last
   `days_back` days.
2. `src/state.py` filters out articles already emailed (tracked in
   `data/seen_ids.json`).
3. `src/summarize.py` sends each new abstract to the OpenAI API and gets back
   a plain-language summary broken into five sections: Introduction, Methods,
   Results, Discussion, Conclusion. If `OPENAI_API_KEY` isn't set (or the API
   call fails), it falls back to the raw abstract under "Introduction" with
   the other sections left blank.
4. `src/email_digest.py` builds an HTML digest (with the five sections per
   article) and sends it via Gmail SMTP.
5. `src/sheets_output.py` appends one row per new article — journal, title,
   authors, link, and the five section summaries — to a Google Sheet, using a
   Google service account. This step is optional: if `GOOGLE_SHEETS_ID` /
   `GOOGLE_SERVICE_ACCOUNT_JSON` aren't set, it's skipped and the email still
   sends normally.
6. `.github/workflows/daily-digest.yml` runs this daily at 12:00 UTC (and on
   manual trigger), then commits the updated `seen_ids.json` back to the repo.

## One-time setup

### 1. Push this repo to GitHub

```
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Get a Gmail App Password

Regular Gmail passwords won't work for SMTP. You need an **App Password**:

1. Enable 2-Step Verification on your Google account:
   https://myaccount.google.com/security
2. Go to https://myaccount.google.com/apppasswords
3. Create an app password (name it e.g. "developer-desk"), copy the 16-character code.

### 3. Get an OpenAI API key (optional but recommended)

1. Go to https://platform.openai.com/api-keys
2. Create a new secret key.
3. Without this, the digest still works but emails the raw PubMed abstract
   instead of an OpenAI-generated summary.

### 4. Set up Google Sheets output (optional but recommended)

Each new article's summary can also be appended as a row to a Google Sheet.
Since this runs unattended in GitHub Actions, it authenticates with a
**service account** rather than an interactive login:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and
   create (or select) a project.
2. Enable the **Google Sheets API**: APIs & Services → Library → search
   "Google Sheets API" → Enable.
3. Create a service account: IAM & Admin → Service Accounts → Create Service
   Account (no project-level roles are required).
4. Open the service account → Keys → Add Key → JSON, and download the key
   file.
5. Note the service account's `client_email` from the downloaded JSON (looks
   like `xxxx@xxxx.iam.gserviceaccount.com`).
6. Open the target Google Sheet, click **Share**, and grant that
   `client_email` **Editor** access.
7. Copy the spreadsheet ID — the long string between `/d/` and `/edit` in the
   sheet's URL.
8. Without this step, the digest still works — it just skips the sheet
   append and logs a note.

### 5. Add GitHub repo secrets

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name                   | Value                                          |
|--------------------------------|------------------------------------------------|
| `OPENAI_API_KEY`               | Your OpenAI API key (optional)                  |
| `GMAIL_ADDRESS`                | The Gmail address you'll send from              |
| `GMAIL_APP_PASSWORD`           | The 16-character app password from step 2       |
| `RECIPIENT_EMAIL`              | Where the digest should be sent                 |
| `GOOGLE_SHEETS_ID`             | Spreadsheet ID from step 4 (optional)           |
| `GOOGLE_SERVICE_ACCOUNT_JSON`  | Full contents of the service account JSON key (optional) |

### 6. Trigger it

- It runs automatically every day at 12:00 UTC.
- To test immediately: go to the **Actions** tab → "Daily Infectious Disease
  Digest" → **Run workflow**.

## Customizing

- Edit `config.yaml` to change journals, lookback window, result cap, or the
  OpenAI model used.
- Edit the cron schedule in `.github/workflows/daily-digest.yml` to change
  the time of day (cron times are in UTC).

## Local testing

```
pip install -r requirements.txt
cp .env.example .env   # fill in your values
export $(cat .env | xargs)   # or use a tool like `direnv`
python src/main.py
```

Note: the `export $(cat .env | xargs)` trick doesn't handle multi-line or
space-containing values, so if you're testing Google Sheets output locally,
paste `GOOGLE_SERVICE_ACCOUNT_JSON` as a single-line (minified) JSON string in
`.env`. GitHub Actions secrets don't have this restriction — paste the key
file there as-is.
