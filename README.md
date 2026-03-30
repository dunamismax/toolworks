# Toolworks

Automation, CLI helpers, and working experiments.

A curated workshop for scripts, small tools, and automation that earn their keep.

## Source of truth

Current-state usage, setup, and verification live in the root README plus each tool's local README.

## Inventory

| Name | Type | Language | Status | Purpose | Run |
| --- | --- | --- | --- | --- | --- |
| [campaign-emailer](./automation/campaign-emailer/) | automation | Python | active | Send templated marketing emails via Outlook on macOS | `cd automation/campaign-emailer && uv run campaign_emailer.py --count 10` |
| [work-emailer](./automation/work-emailer/) | automation | Python | active | Send one-off post-call follow-up emails via Outlook on macOS | `cd automation/work-emailer && uv run work_emailer.py --tailscale recipient@example.com` |

## Structure

- `tools/` - durable utilities you expect to keep using
- `automation/` - scheduled or operational jobs
- `experiments/` - prototypes, weird ideas, things not yet proven
- `docs/` - repo-wide conventions and inventory
- `bin/` - tiny helper entrypoints or wrappers

## Rules

- Every tool gets its own folder and README
- Every tool declares a status: `stable`, `active`, `experimental`, or `archived`
- Each tool folder is self-contained with its own manifest if needed
- If a tool outgrows this repo, promote it to its own repo

## Verification

For Python tools, keep dependencies and checks local to the tool folder.

For `campaign-emailer`, use:

```bash
cd automation/campaign-emailer
uv sync --group dev
uv run ruff check .
uv run pytest
```

For `work-emailer`, use:

```bash
cd automation/work-emailer
uv sync --group dev
uv run ruff check .
uv run pytest
```

## License

[MIT](./LICENSE)
