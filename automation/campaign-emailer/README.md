# campaign-emailer

**Status:** active

Send templated marketing emails via Outlook on macOS. The tool reads an Excel campaign tracker, finds the next batch of un-emailed contacts, personalizes the email body, sends via AppleScript-driven Outlook, and updates the tracker.

## What It Does

1. Opens the campaign tracker Excel file
2. Finds the next N contacts with `Emailed = FALSE`
3. Personalizes the email template greeting from contact or company data
4. Sends through macOS Outlook using AppleScript
5. Updates the tracker with `Emailed = TRUE`, `Date Emailed = today`, and `Status = In Progress`

## Greeting Logic

- Real contact name: `Hi Michael,`
- Doctor title: `Hi Dr. Jane,`
- Generic or missing contact with usable company: `Hi Atlas Orthogonal Chiropractic team,`
- No usable contact or company: `Hi there,`

## Setup

This tool now carries its own local Python manifest.

```bash
cd automation/campaign-emailer
uv sync --group dev
```

## Configuration

The script keeps sensible defaults for Stephen's current environment, but you can override them with environment variables when needed:

- `CAMPAIGN_EMAILER_TRACKER_PATH`
- `CAMPAIGN_EMAILER_TEMPLATE_PATH`
- `CAMPAIGN_EMAILER_CC_EMAIL`
- `CAMPAIGN_EMAILER_SUBJECT`
- `CAMPAIGN_EMAILER_TEST_EMAIL`

The default tracker path still points at the current OneDrive campaign workbook.

## Requirements

- macOS with Microsoft Outlook installed and configured
- Python 3.10+
- `openpyxl` via the local `pyproject.toml`
- Campaign tracker Excel file available at the configured path
- HTML email template available at the configured path

## Usage

```bash
# Send next 10 emails
uv run campaign_emailer.py

# Send next 5
uv run campaign_emailer.py --count 5

# Preview without sending or writing to the tracker
uv run campaign_emailer.py --dry-run

# Check tracker status
uv run campaign_emailer.py --status

# Send one test email to the configured test inbox
uv run campaign_emailer.py --test
```

## Verification

```bash
uv run ruff check .
uv run pytest
```

## Via OpenClaw

Tell Scry: "knock out 10 campaign emails" or "campaign emailer" or "send campaign emails"
