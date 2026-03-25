#!/usr/bin/env python3
"""
campaign-emailer: Send templated marketing emails via Outlook on macOS.

Reads an Excel campaign tracker, finds the next batch of un-emailed contacts,
fills in the email template, and sends via AppleScript-driven Outlook.

Usage:
    python3 campaign_emailer.py                  # send next 10
    python3 campaign_emailer.py --count 5        # send next 5
    python3 campaign_emailer.py --dry-run        # preview without sending
    python3 campaign_emailer.py --status         # show tracker status
"""

import argparse
import os
import re
import subprocess
import sys
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


def is_generic_name(name: str) -> bool:
    """Check if a contact name is generic and should be replaced with company name."""
    if not name:
        return True
    cleaned = name.strip().lower()
    if cleaned in SKIP_NAMES:
        return True
    # "Dr. LastName" is fine, but standalone "Dr." or "Doctor" is not
    if cleaned in ("dr.", "dr", "doctor"):
        return True
    return False


def parse_template() -> str:
    """Extract the plain-text body from the .emltpl file."""
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the plain text section (between Content-Type: text/plain and the next boundary)
    # The template uses quoted-printable encoding
    plain_match = re.search(
        r'Content-Type: text/plain.*?\n\n(.*?)(?=\n--=)',
        content,
        re.DOTALL
    )
    if not plain_match:
        print("ERROR: Could not extract plain text body from template", file=sys.stderr)
        sys.exit(1)

    body = plain_match.group(1)
    # Decode quoted-printable soft line breaks
    body = body.replace("=\n", "")
    # Decode common QP entities
    body = body.replace("=E2=80=99", "'")
    body = body.replace("=E2=80=93", "–")
    body = body.replace("=E2=80=94", "—")
    body = body.replace("=C2=A0", " ")
    # Decode any remaining =XX sequences
    body = re.sub(r'=([0-9A-Fa-f]{2})', lambda m: bytes.fromhex(m.group(1)).decode('utf-8', errors='replace'), body)
    return body


def personalize_body(body: str, contact_name: str | None, company_name: str) -> str:
    """Replace [[Practice Name]] with the appropriate greeting."""
    if contact_name and not is_generic_name(contact_name):
        # Use contact name, remove "team"
        greeting = f"Hello {contact_name.strip()},"
    else:
        # Use company name with "team"
        greeting = f"Hello {company_name.strip()} Team,"

    # Replace the template placeholder line
    body = re.sub(
        r'Hello \[\[Practice Name\]\] team,',
        greeting,
        body,
        flags=re.IGNORECASE
    )
    return body


def send_via_applescript(to_email: str, subject: str, body: str) -> bool:
    """Send an email via Outlook using AppleScript."""
    # Escape special characters for AppleScript
    escaped_body = body.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    escaped_subject = subject.replace("\\", "\\\\").replace('"', '\\"')
    escaped_to = to_email.replace("\\", "\\\\").replace('"', '\\"')

    script = f'''
    tell application "Microsoft Outlook"
        set newMessage to make new outgoing message with properties {{subject:"{escaped_subject}", plain text content:"{escaped_body}"}}
        make new to recipient at newMessage with properties {{email address:{{address:"{escaped_to}"}}}}
        make new cc recipient at newMessage with properties {{email address:{{address:"{CC_EMAIL}"}}}}
        send newMessage
    end tell
    '''

    try:
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


def get_pending_rows(ws, max_count: int) -> list[dict]:
    """Find the next batch of un-emailed contacts."""
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=False):
        vals = [cell.value for cell in row]
        emailed = vals[COL_EMAILED]

        # Check for FALSE (boolean or string)
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
        if vals[COL_EMAIL]:  # has an email address
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


def main():
    parser = argparse.ArgumentParser(description="Send campaign emails via Outlook")
    parser.add_argument("--count", "-n", type=int, default=10, help="Number of emails to send (default: 10)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Preview emails without sending")
    parser.add_argument("--status", "-s", action="store_true", help="Show tracker status and exit")
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

    # Parse the email template
    template_body = parse_template()

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
        # Personalize
        body = personalize_body(template_body, contact["contact"], contact["company"])
        greeting_preview = body.split("\n")[0]

        print(f"  Row {contact['row_num']}: {contact['company']}")
        print(f"    To: {contact['email']}")
        print(f"    Greeting: {greeting_preview}")

        if args.dry_run:
            print(f"    → [DRY RUN] Would send")
            sent += 1
        else:
            success = send_via_applescript(contact["email"], SUBJECT, body)
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
