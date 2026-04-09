# BUILD.md

Last reviewed: 2026-04-09

## Working contract for future agents

This file is the active execution manual for `toolworks` while the repo is still being actively shaped.

Future agents are expected to:

- work through this file before making structural or migration-heavy changes
- keep it current when repo truth, sequencing, or scope changes
- check boxes only after work is actually done and verified
- leave stable docs such as `README.md` and tool-local READMEs current-state oriented
- remove this file once it stops being an honest, maintained build tracker

If this file becomes stale, fix it or remove it. Do not let it rot into fake truth.

## Decision first

`toolworks` should stay a **Python-first automation workshop**.

A literal rewrite into Stephen's default full-stack web lane would be a poor fit for the repo as it exists today.

This repo currently earns its keep as a place for:

- automation scripts
- CLI helpers
- operational jobs
- experiments that may later graduate into their own repos

That already fits Stephen's current portfolio direction.

## Alignment with Stephen's current stack

Stephen's current web-first default still matters here, but only where it is honestly applicable.

### What stays in the Python lane

- local automation
- macOS and Outlook scripting
- task-focused CLI utilities
- operational helpers that are faster and safer in the terminal
- per-tool local manifests and verification

For this lane, the default baseline is:

- `uv`
- local `pyproject.toml`
- `ruff`
- `pyright`
- `pytest`

### What can align with the web lane later

Only if a tool grows into a real browser-first product or operator surface:

- Bun for the runtime of a dedicated web surface
- Astro for page ownership
- Vue only where interaction clearly earns it
- plain CSS by default
- PostgreSQL only when shared durable state is genuinely needed
- Docker Compose and Caddy when deployment becomes part of the real job

### What should not be forced here

- a Bun workspace conversion for the whole repo
- an Elysia API for scripts that are still local tools
- PostgreSQL for tools that do not need shared relational state
- a dashboard just because the preferred portfolio stack now includes one
- a fake browser layer that exists only to match a trend

## Repo truth today

Today `toolworks` is:

- a workshop repo with `automation/`, `tools/`, `experiments/`, `docs/`, and `bin/`
- organized by purpose, not language
- currently centered on Python automation
- carrying active Outlook-on-macOS email tooling
- intentionally lightweight and not pretending to be a product platform

That is the baseline this plan should protect.

## Preferred evolution path

The real path forward is:

1. keep the workshop clean
2. standardize quality and safety for Python tools
3. improve docs and repeatability
4. promote any tool that becomes product-shaped into its own repo
5. only build a web surface when there is an actual browser-first need

## Rules for structural decisions

Before adding framework weight, answer these questions:

1. Is this still just a local or operator-facing tool?
2. Does the workflow actually need a browser?
3. Would the tool be clearer as its own repo?
4. Is shared durable state now a real requirement?

If the answers are mostly no, stay in the Python lane.

If the answers are mostly yes, the likely next move is to spin that tool out into its own repo that can use the full web stack cleanly.

## Phased plan

### Phase 1: protect current-state repo truth

Goal: keep the repo honest, readable, and easy for the next agent to understand.

Work items:

- [ ] Audit root docs for stale or vague language about repo purpose, structure, and tool status.
- [ ] Ensure each maintained tool folder has a local `README.md` with status, purpose, setup, usage, and verification.
- [ ] Ensure each maintained Python tool uses a local `pyproject.toml` and `uv` workflow unless a documented exception exists.
- [ ] Keep the root inventory accurate as tools are added, archived, or promoted.
- [ ] Remove or relocate loose root artifacts that violate the workshop structure.

Acceptance criteria:

- [ ] A new agent can identify every maintained tool and run or verify it from current docs.
- [ ] Root docs describe present reality instead of speculative future product plans.
- [ ] Repo structure still matches `docs/conventions.md`.

### Phase 2: standardize the Python quality baseline

Goal: make maintained Python tools feel like one coherent workshop instead of unrelated scripts.

Work items:

- [ ] Add `ruff format --check` or equivalent formatting checks where missing.
- [ ] Add `pyright` checks where the tool's logic is substantial enough to benefit from typing.
- [ ] Tighten `pytest` coverage for maintained tools with real branching or data handling.
- [ ] Normalize Python version guidance and local bootstrap steps if drift appears across tools.
- [ ] Add a small repo-level helper only if it reduces duplication without hiding per-tool truth.

Acceptance criteria:

- [ ] Maintained Python tools expose documented lint, format, type-check, and test commands.
- [ ] Verification remains local and obvious at the tool level.
- [ ] New tools have a clear baseline to copy.

### Phase 3: harden operational safety

Goal: reduce the risk of fragile or unsafe automation.

Work items:

- [ ] Add dry-run paths wherever a tool can send messages, mutate files, or trigger external side effects.
- [ ] Add fixtures, templates, or sample inputs where current testing depends too much on live personal data.
- [ ] Move environment-specific values out of code when they are still too hard-coded.
- [ ] Improve failure output, summaries, or logging where diagnosis is currently weak.
- [ ] Document macOS-specific and Outlook-specific constraints clearly in tool docs.

Acceptance criteria:

- [ ] Maintainers can validate behavior safely without touching production data whenever practical.
- [ ] Tool prerequisites are explicit.
- [ ] External-action tools fail clearly and predictably when prerequisites are missing.

### Phase 4: decide whether a tool should graduate

Goal: identify when a workshop tool has outgrown this repo.

Graduation triggers:

- repeated use beyond one-off personal automation
- real need for releases, versioning, or outside users
- real need for browser-based review or operations
- durable shared state that no longer fits simple local files
- portfolio value as a standalone product or polished demo

Work items:

- [ ] Define promotion criteria in repo docs or a short architecture note.
- [ ] Review maintained tools and tag them as `stay here`, `promote later`, or `archive`.
- [ ] For any candidate that needs a browser-first surface, decide whether it should leave this repo before adding UI code.
- [ ] Leave a clear pointer behind when a tool is promoted out.
- [ ] Remove or archive dead experiments before they become misleading surface area.

Acceptance criteria:

- [ ] `toolworks` stays a focused workshop instead of becoming a junk drawer.
- [ ] Product-shaped tools have a credible path out of this repo.
- [ ] Archived and promoted work is labeled clearly enough that future agents do not misread repo truth.

### Phase 5: only then consider a web surface

Goal: use Stephen's preferred full-stack web lane honestly, not performatively.

This phase should only begin after a specific tool has clearly become browser-first. In most cases, that should happen in a dedicated repo rather than at the root of `toolworks`.

Work items:

- [ ] Write a short note explaining why a browser-first product now exists and why it belongs here or should move out.
- [ ] If the tool stays here temporarily, keep the web surface isolated from the Python workshop structure.
- [ ] Use Bun, Astro, plain CSS, and Vue only where interaction clearly earns it.
- [ ] Choose the backend lane honestly: Python if it remains automation-heavy, or Bun plus Elysia only if that is now the cleanest fit.
- [ ] Define local run, verification, and deployment shape before shipping UI code.

Acceptance criteria:

- [ ] The reason for adding a web surface is documented and concrete.
- [ ] The frontend and backend choices match the actual job.
- [ ] Existing CLI and automation workflows remain first-class until a tool is fully promoted or replaced.

## Done means

When you complete work against this file:

- update the relevant checkboxes
- update current-state docs if repo truth changed
- run the smallest useful verification for the touched area
- keep this file honest, or remove it if it no longer should exist

## Notes for the next agent

- Default to the Python automation lane.
- Treat Stephen's Bun and Astro web stack as the default for standalone browser-first products, not for every utility repo by force.
- When a tool becomes product-shaped, promotion is usually cleaner than growing a web platform inside this workshop.
