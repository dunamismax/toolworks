#!/usr/bin/env python3
"""
campaign-emailer: Send templated marketing emails via Outlook on macOS.

Reads an Excel campaign tracker, finds the next batch of un-emailed contacts,
fills in the email template (HTML with signature), and sends via AppleScript-driven Outlook.

Usage:
    python3 campaign_emailer.py                  # send next 10
    python3 campaign_emailer.py --count 5        # send next 5
    python3 campaign_emailer.py --dry-run        # preview without sending
    python3 campaign_emailer.py --status         # show tracker status
    python3 campaign_emailer.py --test           # send one test to personal email
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import openpyxl

# --- Configuration ---

TRACKER_PATH = (
    "/Users/sawyer/Library/CloudStorage/OneDrive-ImagingServicesInc/"
    "OneDrive - Work Desktop/07-Marketing/Campaign-Tracker/"
    "contacts-campaign-tracker.xlsx"
)

TEMPLATE_PATH = (
    "/Users/sawyer/Library/CloudStorage/OneDrive-ImagingServicesInc/"
    "OneDrive - Work Desktop/06-Email-Templates/Stephen/"
    "Marketing - Comprehensive Coverage Offer - Standard.emltpl"
)

FROM_EMAIL = "ssawyer@imagingservices.net"
CC_EMAIL = "support@imagingservices.net"
SUBJECT = "Protect your X-Ray operations with Comprehensive Support + Cloud Backup + RMM"
TEST_EMAIL = "stephenvsawyer@gmail.com"

# Column indices (0-based)
COL_COMPANY = 1    # Company Name
COL_CONTACT = 2    # Contact Name
COL_EMAIL = 4      # Email Address
COL_EMAILED = 6    # Emailed (TRUE/FALSE)
COL_DATE = 7       # Date Emailed
COL_STATUS = 15    # Status

# Contact names to skip (use company name instead)
SKIP_NAMES = {
    "reception", "receptionist", "front desk", "doctor", "dr.", "dr",
    "office", "admin", "manager", "staff", "team", "billing",
    "office manager", "front office", "n/a", "na", "none", "",
}


def clean_contact_name(name: str) -> str:
    """Clean up a contact name by removing parenthetical notes and extra whitespace."""
    if not name:
        return ""
    # Remove parenthetical notes like "(business email)" or "(owner)"
    cleaned = re.sub(r'\s*\([^)]*\)\s*', ' ', name)
    return cleaned.strip()


def is_generic_name(name: str) -> bool:
    """Check if a contact name is generic and should be replaced with company name."""
    if not name:
        return True
    cleaned = clean_contact_name(name).lower()
    if cleaned in SKIP_NAMES:
        return True
    if cleaned in ("dr.", "dr", "doctor"):
        return True
    return False


def parse_html_template() -> str:
    """Extract the HTML body from the .emltpl file."""
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the HTML section
    html_match = re.search(
        r'Content-Type: text/html.*?\n\n(.*?)(?=\n--=)',
        content,
        re.DOTALL
    )
    if not html_match:
        print("ERROR: Could not extract HTML body from template", file=sys.stderr)
        sys.exit(1)

    html = html_match.group(1)
    # Decode quoted-printable soft line breaks
    html = html.replace("=\n", "")
    # Decode =XX hex sequences
    html = re.sub(
        r'=([0-9A-Fa-f]{2})',
        lambda m: bytes.fromhex(m.group(1)).decode('utf-8', errors='replace'),
        html
    )
    return html


def personalize_html(html: str, contact_name: str | None, company_name: str) -> str:
    """Replace [[Practice Name]] in the HTML template with the appropriate name."""
    if contact_name and not is_generic_name(contact_name):
        clean_name = clean_contact_name(contact_name)
        # Use contact name — replace "[[Practice Name]]</strong> team" with just the name
        html = re.sub(
            r'Hello\s*<strong>\[\[Practice Name\]\]</strong>\s*team,',
            f'Hello <strong>{clean_name}</strong>,',
            html,
            flags=re.IGNORECASE
        )
        # Also handle any plain-text version that might exist
        html = re.sub(
            r'Hello \[\[Practice Name\]\] team,',
            f'Hello {clean_name},',
            html,
            flags=re.IGNORECASE
        )
    else:
        # Use company name, keep "team"
        html = re.sub(
            r'\[\[Practice Name\]\]',
            company_name.strip(),
            html,
            flags=re.IGNORECASE
        )
    return html


def send_html_via_applescript(to_email: str, cc_email: str, subject: str, html_body: str) -> bool:
    """Send an HTML email via Outlook using AppleScript with a temp HTML file."""
    # Write HTML to a temp file (avoids escaping nightmares in AppleScript strings)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_body)
        html_path = f.name

    try:
        # AppleScript that reads HTML from file and sends via Outlook
        script = f'''
        set htmlFile to POSIX file "{html_path}"
        set htmlContent to read htmlFile as «class utf8»

        tell application "Microsoft Outlook"
            set newMessage to make new outgoing message with properties {{subject:"{subject}", content:htmlContent}}
            make new to recipient at newMessage with properties {{email address:{{address:"{to_email}"}}}}
            make new cc recipient at newMessage with properties {{email address:{{address:"{cc_email}"}}}}
            send newMessage
        end tell
        '''

        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"  AppleScript error: {result.stderr.strip()}", file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print("  AppleScript timed out", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  AppleScript exception: {e}", file=sys.stderr)
        return False
    finally:
        os.unlink(html_path)


def get_pending_rows(ws, max_count: int) -> list[dict]:
    """Find the next batch of un-emailed contacts."""
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=False):
        vals = [cell.value for cell in row]
        emailed = vals[COL_EMAILED]

        if emailed is False or (isinstance(emailed, str) and emailed.upper() == "FALSE"):
            email_addr = vals[COL_EMAIL]
            if not email_addr or not isinstance(email_addr, str) or "@" not in email_addr:
                continue

            rows.append({
                "row_num": row[0].row,
                "company": vals[COL_COMPANY] or "Unknown Company",
                "contact": vals[COL_CONTACT],
                "email": email_addr.strip(),
            })

            if len(rows) >= max_count:
                break
    return rows


def update_tracker(ws, row_num: int):
    """Mark a row as emailed in the tracker."""
    ws.cell(row=row_num, column=COL_EMAILED + 1, value=True)
    ws.cell(row=row_num, column=COL_DATE + 1, value=datetime.now().strftime("%Y-%m-%d"))
    ws.cell(row=row_num, column=COL_STATUS + 1, value="In Progress")


def show_status():
    """Show current tracker status."""
    wb = openpyxl.load_workbook(TRACKER_PATH, read_only=True)
    ws = wb.active

    total = 0
    emailed = 0
    remaining = 0
    next_row = None

    for row in ws.iter_rows(min_row=2, values_only=False):
        vals = [cell.value for cell in row]
        if vals[COL_EMAIL]:
            total += 1
            e = vals[COL_EMAILED]
            if e is True or (isinstance(e, str) and e.upper() == "TRUE"):
                emailed += 1
            else:
                remaining += 1
                if next_row is None:
                    next_row = {
                        "row": row[0].row,
                        "company": vals[COL_COMPANY],
                        "contact": vals[COL_CONTACT],
                        "email": vals[COL_EMAIL],
                    }

    wb.close()

    print(f"Campaign Tracker Status")
    print(f"  Total contacts:    {total}")
    print(f"  Emailed:           {emailed}")
    print(f"  Remaining:         {remaining}")
    if next_row:
        print(f"  Next up (row {next_row['row']}): {next_row['contact'] or next_row['company']} <{next_row['email']}>")


def send_test(html_template: str):
    """Send a test email to personal address using the next pending contact's data."""
    wb = openpyxl.load_workbook(TRACKER_PATH, read_only=True)
    ws = wb.active

    # Get next pending contact for realistic test data
    pending = get_pending_rows(ws, 1)
    wb.close()

    if not pending:
        print("No pending contacts to use as test data.")
        return

    contact = pending[0]
    html = personalize_html(html_template, contact["contact"], contact["company"])

    print(f"Sending TEST email to {TEST_EMAIL}")
    print(f"  Using data from row {contact['row_num']}: {contact['company']}")
    print(f"  Contact: {contact['contact'] or '(none)'}")

    greeting_match = re.search(r'Hello\s*(?:<strong>)?(.+?)(?:</strong>)?\s*(?:team)?,', html)
    if greeting_match:
        print(f"  Greeting: Hello {greeting_match.group(1)}")

    success = send_html_via_applescript(TEST_EMAIL, CC_EMAIL, f"[TEST] {SUBJECT}", html)
    if success:
        print(f"  → Test sent ✓ (tracker NOT updated)")
    else:
        print(f"  → Test FAILED ✗")


def main():
    parser = argparse.ArgumentParser(description="Send campaign emails via Outlook")
    parser.add_argument("--count", "-n", type=int, default=10, help="Number of emails to send (default: 10)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Preview emails without sending")
    parser.add_argument("--status", "-s", action="store_true", help="Show tracker status and exit")
    parser.add_argument("--test", "-t", action="store_true", help="Send one test to personal email")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    # Verify files exist
    if not os.path.exists(TRACKER_PATH):
        print(f"ERROR: Tracker not found: {TRACKER_PATH}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(TEMPLATE_PATH):
        print(f"ERROR: Template not found: {TEMPLATE_PATH}", file=sys.stderr)
        sys.exit(1)

    # Parse the HTML email template
    html_template = parse_html_template()

    if args.test:
        send_test(html_template)
        return

    # Open tracker (read-write)
    wb = openpyxl.load_workbook(TRACKER_PATH)
    ws = wb.active

    # Get pending rows
    pending = get_pending_rows(ws, args.count)
    if not pending:
        print("No pending contacts found. All caught up!")
        wb.close()
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Processing {len(pending)} email(s)...\n")

    sent = 0
    failed = 0

    for contact in pending:
        html = personalize_html(html_template, contact["contact"], contact["company"])

        # Extract greeting for display
        greeting_match = re.search(r'Hello\s*(?:<strong>)?(.+?)(?:</strong>)?\s*(?:team)?,', html)
        greeting_preview = f"Hello {greeting_match.group(1)}" if greeting_match else "(unknown)"

        print(f"  Row {contact['row_num']}: {contact['company']}")
        print(f"    To: {contact['email']}")
        print(f"    Greeting: {greeting_preview}")

        if args.dry_run:
            print(f"    → [DRY RUN] Would send")
            sent += 1
        else:
            success = send_html_via_applescript(contact["email"], CC_EMAIL, SUBJECT, html)
            if success:
                update_tracker(ws, contact["row_num"])
                print(f"    → Sent ✓")
                sent += 1
            else:
                print(f"    → FAILED ✗")
                failed += 1

        print()

    # Save tracker if we actually sent
    if not args.dry_run and sent > 0:
        wb.save(TRACKER_PATH)
        print(f"Tracker updated ({sent} rows marked TRUE).")

    wb.close()

    print(f"\nDone. Sent: {sent}, Failed: {failed}")


if __name__ == "__main__":
    main()
