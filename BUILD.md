# BUILD.md

Last reviewed: 2026-03-31

## How to use this file

This file is the active execution manual for the current evolution of `toolworks`.

Future agents are expected to:

- work through this file in order
- keep it current as repo reality changes
- update scope when a phase is no longer honest
- check boxes only after the work is actually done and verified
- leave stable docs such as `README.md` current-state oriented instead of turning them into future-tense plans

If the repo stops being an active build or migration target, fold any still-useful truth into stable docs and remove this file.

## Decision first

`toolworks` is **not** a candidate for a literal full-stack Bun rewrite.

This repo is currently a Python automation workshop for scripts and operational helpers, especially macOS and Outlook-driven workflows. That is a valid lane in Stephen's portfolio direction. The honest plan is to strengthen the Python automation foundation, tighten tool standards, and only add a web surface when a browser-first operator workflow clearly earns it.

Stephen's current stack direction still matters here:

- keep Python for automation, scripting, and operational tooling
- use `uv`, `pyproject.toml`, `ruff`, `pyright`, and `pytest` as the default Python quality stack
- only introduce Astro + Vue when the repo grows a real browser-facing control panel, review surface, or reporting interface
- if a web surface is added, prefer Astro for pages and Vue only where interaction earns it
- if backend logic remains operational and automation-heavy, keep Python as the backend lane unless there is a proven reason to move a specific surface elsewhere

## Current state

Today this repo is:

- a multi-tool workshop with `automation/`, `tools/`, `experiments/`, `docs/`, and `bin/`
- currently centered on Python tools with local manifests and per-tool READMEs
- carrying two active Outlook-on-macOS automation tools under `automation/`
- documented as a clean, current-state utility repo rather than a product repo

That current shape is good. The plan below evolves it without pretending it should become something else.

## Fit boundaries

### What should stay as-is

- Python-first automation and scripting
- per-tool self-contained folders
- repo-level organization by purpose rather than by language
- macOS-specific automation where that is the actual job
- promotion of mature tools into their own repos when they outgrow this workshop

### What can align with the newer web stack later

- a lightweight Astro documentation or operator surface for browsing tools, runs, reports, or templates
- Vue islands only for interactive dashboards, filters, editors, or run history inspection
- a PostgreSQL-backed service only if this repo grows shared operational state that flat files can no longer carry cleanly

### What should not be forced

- a Bun workspace monorepo just because it is the current web default
- an Elysia API for tools that are still local scripts
- a PostgreSQL dependency for tools that do not need shared durable state
- a frontend rewrite of workflows that are faster and safer as local CLI or macOS automation

## Target end state

The likely healthy end state for `toolworks` is:

1. a clean Python-first automation repo with consistent tooling and safety rails
2. strong per-tool docs, tests, and verification paths
3. clear promotion rules for when a tool should leave this repo
4. an optional web surface only if the repo develops a real need for browser-based operations, reporting, or review

## Operating rules for future agents

Before changing implementation shape, confirm whether the repo is still primarily:

- a local automation workshop
- a set of reusable CLI helpers
- an experiment staging ground
- or a product platform that now genuinely needs a browser surface

Do not assume the answer changed just because Stephen's preferred frontend stack changed.

When you complete work in a phase below:

- update this file
- check the boxes you actually finished
- tighten README or docs wording only where current-state truth needs it
- do not mark aspirational work done

## Phased plan

### Phase 1: tighten current-state repo truth

Goal: make the repo's Python automation lane explicit, consistent, and easy for future agents to extend.

Work items:

- [ ] Audit root docs for any vague or stale wording about repo purpose, structure, or status labels.
- [ ] Ensure every first-class tool folder has a local `README.md` with status, purpose, setup, usage, and verification.
- [ ] Ensure every Python tool uses a local `pyproject.toml` and `uv` workflow unless there is a documented exception.
- [ ] Add or tighten a repo-level inventory document if the root README stops being enough to understand what lives here.
- [ ] Remove or relocate loose repo-root artifacts that violate the clean workshop structure.

Acceptance criteria:

- [ ] A new agent can identify every maintained tool, its status, and how to run or verify it from current docs.
- [ ] Root docs describe the repo as it exists today, not as a speculative future product.
- [ ] The repo root stays clean and consistent with `docs/conventions.md`.

### Phase 2: standardize Python quality gates

Goal: make each maintained Python tool feel like it belongs to one coherent workshop.

Work items:

- [ ] Add `ruff format --check` or equivalent formatting verification where missing.
- [ ] Add `pyright` configuration and checks for maintained Python tools where typing value outweighs friction.
- [ ] Normalize `pytest` coverage for maintained tools that contain real logic.
- [ ] Add shared guidance for `.python-version`, interpreter targets, and local dev bootstrap if drift appears across tools.
- [ ] Introduce a small repo-level verification helper only if it reduces duplication without hiding per-tool truth.

Acceptance criteria:

- [ ] Maintained Python tools expose clear lint, format, type-check, and test commands.
- [ ] Verification commands are documented next to the tool they validate.
- [ ] New Python tools can copy an obvious, repeatable quality baseline.

### Phase 3: harden operational safety and maintainability

Goal: reduce the chance that useful automation becomes fragile or risky.

Work items:

- [ ] Add dry-run paths for any tool that can perform irreversible or externally visible actions.
- [ ] Add fixtures, sample inputs, or template examples for tools that currently rely too heavily on live personal data.
- [ ] Separate config from code where current scripts still hard-code too much environment-specific state.
- [ ] Add logging, summaries, or machine-readable output where operational debugging is currently weak.
- [ ] Document platform constraints clearly for macOS-specific tools.

Acceptance criteria:

- [ ] Maintainers can validate behavior without touching production data whenever practical.
- [ ] Tool-specific environment assumptions are visible and documented.
- [ ] Operational tools fail clearly and predictably when prerequisites are missing.

### Phase 4: decision gate for any web surface

Goal: only add a browser-facing layer if the repo has genuinely outgrown pure CLI and local automation workflows.

Decision triggers that justify this phase:

- repeated need to browse job history, artifacts, templates, or run outcomes in a browser
- need for non-terminal users to inspect or operate parts of the system
- growing shared state that is awkward to manage through flat files and one-off scripts
- a portfolio reason to demonstrate a real operator UI around the tooling

Work items:

- [ ] Write a short architecture note explaining why a web surface is now warranted.
- [ ] Decide whether the backend should stay Python with an Astro frontend or whether a separate service is justified.
- [ ] If a frontend is added, use Astro for page ownership and add Vue only for interaction-heavy areas.
- [ ] Keep any new web surface separate from the existing automation tools so the Python lane stays clear.
- [ ] Define deployment and local-run expectations before building a UI that nobody can operate reliably.

Acceptance criteria:

- [ ] The reason for adding a web surface is concrete, documented, and not trend-driven.
- [ ] The chosen frontend and backend split matches the actual job to be done.
- [ ] Existing CLI and automation workflows remain first-class rather than becoming second-rate leftovers.

### Phase 5: promotion and portfolio shaping

Goal: keep `toolworks` lean by graduating tools that deserve their own identity.

Work items:

- [ ] Define clear promotion criteria for when a tool should move into its own repo.
- [ ] Tag candidate tools as `stay here`, `promote later`, or `archive` during periodic repo review.
- [ ] For promoted tools, leave behind a short pointer so the workshop inventory stays understandable.
- [ ] Archive or remove abandoned experiments before they rot into fake surface area.
- [ ] Periodically re-evaluate whether `toolworks` should remain a mixed workshop or split by domain.

Acceptance criteria:

- [ ] The repo stays focused instead of becoming a graveyard of unrelated scripts.
- [ ] Important tools have a credible path to standalone ownership.
- [ ] Archived or promoted work is clearly labeled so future agents do not misread repo truth.

## Notes for the next agent who touches this repo

- Default to improving the Python automation lane first.
- Treat Astro + Vue as an optional companion surface, not the repo's presumed destiny.
- Keep README and local tool docs grounded in present reality.
- If you finish enough of this plan that the repo is no longer in an active build phase, remove `BUILD.md` and fold the remaining truth into stable docs.
