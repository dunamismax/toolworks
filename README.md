# Toolworks

Automation, CLI helpers, and working experiments.

A curated workshop for scripts, small tools, and automation that earn their keep.

---

## Inventory

| Name | Type | Language | Status | Purpose | Run |
| --- | --- | --- | --- | --- | --- |
| [campaign-emailer](./automation/campaign-emailer/) | automation | Python | active | Send templated marketing emails via Outlook on macOS | `python3 campaign_emailer.py --count 10` |

## Structure

- `tools/` — durable utilities you expect to keep using
- `automation/` — scheduled or operational jobs
- `experiments/` — prototypes, weird ideas, things not yet proven
- `docs/` — repo-wide conventions and inventory
- `bin/` — tiny helper entrypoints or wrappers

## Rules

- Every tool gets its own folder and README
- Every tool declares a status: `stable`, `active`, `experimental`, or `archived`
- Each tool folder is self-contained with its own manifest if needed
- If a tool outgrows this repo, promote it to its own

## License

[MIT](./LICENSE)
