# Is it Christmas?

A minimalist webpage and daily RSS 2.0 feed inspired by `isitchristmas.com`, built for Slack channel subscriptions.

- **Webpage**: Displays a giant **NO** (or **YES** on 25 December) in UK time (`Europe/London`), with a subtle status bar and one-click Slack subscribe snippet.
- **RSS Feed (`feed.xml`)**:
  - **1 Jan – 30 Nov**: Valid empty RSS feed (0 items) so Slack subscribes cleanly without posting old entries.
  - **1 Dec – 24 Dec**: Publishes one new item daily at **09:00 UK time** (`Is it Christmas? NO`).
  - **25 Dec**: Publishes `Is it Christmas? YES` at **09:00 UK time**.
  - **26 Dec – 31 Dec**: Stops publishing new items (feed stays frozen at 25 Dec so Slack stays quiet).

## Hosting on GitHub Pages

1. Push this repository to `https://github.com/knowlesy/is-it-christmas`.
2. In GitHub, open **Settings → Pages** and set **Source** to **GitHub Actions**.
3. The workflow in `.github/workflows/pages.yml` automatically deploys on push to `main` and runs on a schedule at `09:00 UTC` (= `09:00 UK GMT`) on **December 1–25 only** (25 runs/year).

> **Note on GitHub Actions minutes**: Because `knowlesy/is-it-christmas` is a **public** repository, GitHub Actions usage is free and does not consume your personal free-tier private repo minutes.

## Subscribe in Slack

In any Slack channel with the RSS app installed, run:

```text
/feed subscribe https://knowlesy.github.io/is-it-christmas/feed.xml
```

## Local Testing

Generate the RSS feed for today or any specific date:

```bash
python3 scripts/generate_feed.py --output feed.xml
python3 scripts/generate_feed.py --date 2026-12-25 --output feed.xml
```

Preview any date in the webpage by adding `?date=YYYY-MM-DD` to the URL (for example, `index.html?date=2026-12-25`).

Run the unit tests:

```bash
python3 -m unittest discover -s tests -v
```
