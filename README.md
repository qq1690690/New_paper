# New_paper

CID and the lancet infectious disease new paper

Daily email digest of new articles from *The Lancet Infectious Diseases* and
*Clinical Infectious Diseases*, summarized with Claude. Runs automatically via
GitHub Actions.

## How it works

1. `src/fetch_papers.py` queries the PubMed E-utilities API for articles
   published in the configured journals (`config.yaml`) within the last
   `days_back` days.
2. `src/state.py` filters out articles already emailed (tracked in
   `data/seen_ids.json`).
3. `src/summarize.py` sends each new abstract to the Claude API for a short
   plain-language summary. If `ANTHROPIC_API_KEY` isn't set, it falls back to
   the raw abstract.
4. `src/email_digest.py` builds an HTML digest and sends it via Gmail SMTP.
5. `.github/workflows/daily-digest.yml` runs this daily at 12:00 UTC (and on
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

### 3. Get an Anthropic API key (optional but recommended)

1. Go to https://console.anthropic.com/
2. Create an API key under Settings → API Keys.
3. Without this, the digest still works but emails the raw PubMed abstract
   instead of a Claude-generated summary.

### 4. Add GitHub repo secrets

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name          | Value                                   |
|-----------------------|------------------------------------------|
| `ANTHROPIC_API_KEY`   | Your Anthropic API key (optional)        |
| `GMAIL_ADDRESS`       | The Gmail address you'll send from       |
| `GMAIL_APP_PASSWORD`  | The 16-character app password from step 2|
| `RECIPIENT_EMAIL`     | Where the digest should be sent          |

### 5. Trigger it

- It runs automatically every day at 12:00 UTC.
- To test immediately: go to the **Actions** tab → "Daily Infectious Disease
  Digest" → **Run workflow**.

## Customizing

- Edit `config.yaml` to change journals, lookback window, result cap, or the
  Claude model used.
- Edit the cron schedule in `.github/workflows/daily-digest.yml` to change
  the time of day (cron times are in UTC).

## Local testing

```
pip install -r requirements.txt
cp .env.example .env   # fill in your values
export $(cat .env | xargs)   # or use a tool like `direnv`
python src/main.py
```
