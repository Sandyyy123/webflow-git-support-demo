# webflow-git-support-demo

A small, runnable helper for an **ongoing Webflow + GitHub support** workflow: it
pulls a Webflow CMS collection into version-controlled JSON, diffs it against the
last committed snapshot, and gates a deploy behind a clean review so site/portal
changes are auditable in Git instead of living only inside the Webflow Designer.

Built as a demo for the kind of same-day Slack-driven support an Anja-Health-style
team needs: small requests come in, you make the change, and the change is tracked.

## Why this exists

Webflow is great for editing, but CMS edits and landing-page tweaks happen
outside of Git, so there is no history, no review, and no rollback. This tool
puts a thin Git layer around Webflow:

1. **Snapshot** every CMS item to `data/cms/<collection>.json` (stable key order).
2. **Diff** the live API state against the committed snapshot (added / changed / removed).
3. **Gate** a publish: refuse to deploy when there are uncommitted snapshot changes.

## Architecture

```
Webflow CMS API ──▶ src/webflow_client.py   (fetch collections + items)
                         │
                         ▼
                    src/cms_sync.py          (normalize ▶ data/cms/*.json)
                         │
                         ▼
                    src/git_gate.py          (diff vs committed ▶ pass/fail)
                         │
                         ▼
                    sync.py                   (CLI: snapshot | diff | gate)
```

- `webflow_client.py` - thin Webflow Data API v2 wrapper (live or `--mock`).
- `cms_sync.py` - normalizes items to deterministic JSON snapshots.
- `git_gate.py` - compares snapshots and inspects `git status` to block dirty deploys.
- `sync.py` - the entry point you wire into a Slack request or a CI step.

## Setup

```bash
pip install -r requirements.txt
export WEBFLOW_TOKEN=your_token          # not needed in --mock mode
export WEBFLOW_COLLECTION_ID=66f0...     # the CMS collection to track
```

## Usage

```bash
# Pull the live (or mock) CMS into a versioned JSON snapshot
python sync.py snapshot --mock

# Show what changed since the last committed snapshot
python sync.py diff --mock

# Fail (exit 1) if there are uncommitted CMS changes - use before a publish
python sync.py gate --mock
```

`--mock` runs the whole flow with bundled sample data so you can try it with no
Webflow token. Drop `--mock` and set the env vars to run against a real site.

## Typical support loop

1. Client pings on Slack: "change the hero CTA on the landing page."
2. Edit in Webflow, then `python sync.py snapshot` to capture the new state.
3. `python sync.py diff` to confirm only the intended fields changed.
4. Commit the snapshot, `python sync.py gate` in CI, then publish.

Now every Webflow change has a reviewable Git diff and a rollback point.
