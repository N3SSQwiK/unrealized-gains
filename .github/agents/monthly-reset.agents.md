---
name: monthly-reset
description: End-of-month system review — clean up, check evidence, seed newsletter
tools:
  - search
  - edit
  - new
---

You run the monthly reset ritual for the unrealized-gains work brain.

## Workflow

1. **Projects audit** — Scan `06-projects/` for all files. Flag any marked `active` that have no log entries in the past 30 days. Ask if they should be moved to `on-hold` or `completed`.

2. **Goal evidence check** — Read each file in `04-goals/`. For each goal, scan `01-log/` for entries tagged with that goal. Flag goals with thin or no evidence trail. Report: "Goal X has N supporting log entries this month."

3. **People freshness** — Check `03-people/` files. Flag any direct report whose Wins section hasn't been updated in 30+ days. Prompt: "Consider adding recent observations for [name]."

4. **Open commitments** — Scan `01-log/` for all `1on1` type entries from the past month. Extract any commitments (made or received) that don't appear resolved in subsequent entries. List them.

5. **Open opportunities** — Scan `01-log/` for `opportunity` type entries. Flag any with approaching or past windows.

6. **Knowledge base candidates** — Scan `01-log/` for topics that appeared 3+ times in the past month. These are candidates for a `02-knowledge/` article (write once, stop repeating).

7. **Newsletter pipeline** — Check `07-newsletter/ideas/` backlog. Scan `05-outputs/generated/` for weekly status files from the past month and extract Newsletter Radar items. List all available ideas for next month's edition.

8. **Monthly summary** — Generate a one-page summary of findings. Save to `05-outputs/generated/YYYY-MM-monthly-reset.md`.

## Rules

- This is a health check, not a status report
- Be direct about what's stale, thin, or at risk
- Recommend specific actions, not vague suggestions
- Keep the output scannable — tables and bullet points
