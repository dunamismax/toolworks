# Conventions

## Tool structure

Every tool in this repo follows the same rules:

1. Gets its own folder under `tools/`, `automation/`, or `experiments/`
2. Has a `README.md` with status, purpose, setup, usage, and verification
3. Declares status: `stable`, `active`, `experimental`, or `archived`
4. Is self-contained and carries its own manifest when it has dependencies

## Organization

Organize by purpose, not language:

- `tools/` - durable utilities you expect to keep using
- `automation/` - scheduled or operational jobs
- `experiments/` - prototypes and unproven ideas
- `bin/` - tiny entrypoints or wrappers (optional)

## Python tools

- Prefer a local `pyproject.toml`
- Prefer `uv` for dependency management and command execution
- Keep verification commands next to the tool they validate

## Promotion

If a tool becomes important enough to deserve releases, docs, and outside users, promote it into its own repo.

## Root cleanliness

The repo root stays clean. No loose scripts. Everything goes in a folder.
