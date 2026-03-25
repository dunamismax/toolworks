# campaign-emailer

**Status:** active

Send templated marketing emails via Outlook on macOS. Reads an Excel campaign tracker, finds the next batch of un-emailed contacts, personalizes the email body, sends via AppleScript-driven Outlook, and updates the tracker.

## What It Does

1. Opens the campaign tracker Excel file
2. Finds the next N contacts with `Emailed = FALSE`
3. For each: personalizes the email template with the contact or company name
4. Sends via macOS Outlook using AppleScript (no GUI interaction needed)
5. Updates the tracker: `Emailed = TRUE`, `Date Emailed = today`, `Status = In Progress`

## Name Logic

- If the contact has a real name (not "Reception", "Doctor", "Front Desk", etc.) → `Hello Michael Muto,`
- If the contact name is generic or missing → `Hello Atlas Orthogonal Chiropractic Team,`

## Usage

```bash
# Send next 10 emails
python3 campaign_emailer.py

# Send next 5
python3 campaign_emailer.py --count 5

# Preview without sending
python3 campaign_emailer.py --dry-run

# Check tracker status
python3 campaign_emailer.py --status
```

## Via OpenClaw

Tell Scry: "knock out 10 campaign emails" or "campaign emailer" or "send campaign emails"

## Requirements

- macOS with Microsoft Outlook installed and configured
- Python 3.10+
- `openpyxl` (`pip3 install openpyxl`)
- Campaign tracker Excel file at the configured OneDrive path
- Email template `.emltpl` file at the configured OneDrive path

## Configuration

Paths and column mappings are configured as constants at the top of `campaign_emailer.py`. Update them if the tracker structure or file locations change.
