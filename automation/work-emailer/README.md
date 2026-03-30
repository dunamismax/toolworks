# work-emailer

**Status:** active

Send one-off post-call follow-up emails through Outlook on macOS using durable HTML templates.

## What it does

- selects one follow-up template directly from the command line
- applies the correct default subject for that template
- renders a pure HTML email body with the standard Imaging Services signature
- sends through Microsoft Outlook on macOS using AppleScript
- supports optional greeting personalization and dry-run previews

## Templates

- `--tailscale` - remote access follow-up
- `--windows10upgrade` - Windows lifecycle and upgrade follow-up
- `--cloudbackup` - cloud backup only follow-up
- `--coverage150credit` - support package follow-up with a $150 credit
- `--coverage300credit` - support package follow-up with a $300 credit

## Setup

```bash
cd automation/work-emailer
uv sync --group dev
```

## Usage

```bash
uv run work_emailer.py --tailscale stephenvsawyer@gmail.com
uv run work_emailer.py --windows10upgrade stephenvsawyer@gmail.com
uv run work_emailer.py --coverage150credit stephenvsawyer@gmail.com
uv run work_emailer.py --coverage300credit stephenvsawyer@gmail.com --name Stephen
uv run work_emailer.py --cloudbackup stephenvsawyer@gmail.com --company Example Animal Hospital
```

## Helpful options

```bash
# Preview without sending
uv run work_emailer.py --tailscale stephenvsawyer@gmail.com --name Stephen --dry-run

# Override the greeting line directly
uv run work_emailer.py --cloudbackup stephenvsawyer@gmail.com --greeting "Hello Stephen,"

# Skip CC for a one-off send
uv run work_emailer.py --coverage150credit stephenvsawyer@gmail.com --no-cc

# See available templates
uv run work_emailer.py --list-templates
```

## Requirements

- macOS with Microsoft Outlook installed and signed in
- Python 3.10+
- Outlook allowed to send through AppleScript

## Verification

```bash
uv run ruff check .
uv run pytest
```
