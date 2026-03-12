# unrealized-gains

Realize the gains.

A markdown-based second brain for work — built for people who manage teams, sit in too many meetings, and need to remember what happened three months ago. Powered by VS Code + GitHub Copilot Chat custom agents.

---

## The Problem

Information flows constantly — meetings, emails, chats, decisions — and most of it evaporates. When it's time to write a status update, prep for a 1:1, or answer "didn't we already discuss this?", you're relying on memory. That's an unrealized gain: valuable information captured by your brain but never organized for retrieval.

## The System

```
INBOX.md               Always-open scratchpad for raw captures
01-log/                Chronological record — meetings, decisions, emails, 1:1s, opportunities
02-knowledge/          Canonical references — write once, link forever
03-people/             One file per direct report, yourself, and your manager
04-goals/              Org and individual goals with evidence trails
05-outputs/            Templates and generated artifacts
05-tools/              Dashboard generator and sample data
06-projects/           Active workstreams and initiatives
07-newsletter/         Content pipeline: ideas, drafts, editions
```

---

## Quick Start

### 1. Clone and open
```bash
git clone <repo-url>
code unrealized-gains
```

### 2. Set up your people
Copy `03-people/.template.md` for each direct report. Fill in `03-people/manager.md` with your manager's name, priorities, and working style. Update `03-people/_self.md` with your current priorities.

### 3. Add your goals
Create `04-goals/org-goals-2026.md` with your organization's goals (narrative format is fine). Add individual goal files as they're drafted.

### 4. Set up email capture (optional)
If your organization has an LLM email integration (e.g., Outlook Quick Step), use the prompt in `05-outputs/templates/stylus-email-prompt.md` to structure forwarded emails as markdown with frontmatter.

### 5. Pin INBOX.md
Keep `INBOX.md` open as a pinned tab in VS Code. This is your always-available capture surface.

### 6. Preview with sample data
```bash
cp 05-tools/sample-data/01-log/* 01-log/
cp 05-tools/sample-data/03-people/*.md 03-people/
cp 05-tools/sample-data/04-goals/* 04-goals/
cp 05-tools/sample-data/02-knowledge/* 02-knowledge/
cp 05-tools/sample-data/06-projects/* 06-projects/
cp 05-tools/sample-data/07-newsletter/ideas/* 07-newsletter/ideas/
python3 05-tools/generate-dashboard.py
```
Open `05-tools/dashboard.html` in a browser to see the system with realistic data. Remove sample data when ready to use your own (see `05-tools/sample-data/README.md`).

---

## How to Capture

The system has two capture tracks. Use whichever has the least friction in the moment.

### Track 1: Raw capture
For quick thoughts, meeting brain dumps, and anything without structure.

- **INBOX.md** — primary scratchpad when VS Code is open. Just type.
- **Outlook drafts / OneNote** — interim surfaces during meetings. Transfer to INBOX.md later.

Raw captures require processing via the `process-inbox` agent, which adds frontmatter and files them.

### Track 2: Structured capture
For emails and meeting recaps processed through an LLM email integration.

- Forward the email with your capture prompt template
- The LLM returns pre-structured markdown with frontmatter
- Paste directly into `01-log/YYYY-MM-DD-topic-slug.md` — skip the inbox entirely

### What to capture

Not everything needs to land here. Focus on:
- Decisions made (who, what, when, why)
- Commitments — yours and theirs
- Wins worth remembering at review time
- Opportunities with a window
- Anything you'll need to recall in 1-4 weeks

---

## How to Process

Run the `process-inbox` agent in Copilot Chat. It reads INBOX.md and files each entry to the right location:

| Destination | When to use |
|---|---|
| `01-log/` | Meetings, decisions, emails, events — anything with a date |
| `02-knowledge/` | Reusable reference material — write once, link forever |
| `03-people/` | Wins, feedback given/received, development notes for a person |
| `04-goals/` | Evidence that advances a goal |
| `06-projects/` | Status, decisions, or blockers for an active workstream |

If the inbox has 10+ items, the agent offers batch triage — a summary table for your approval before filing.

---

## Agents

Agents are custom Copilot Chat participants defined in `.github/agents/`. Select them from the agents dropdown in VS Code.

| Agent | What it does |
|---|---|
| `process-inbox` | Files INBOX.md entries into the right locations |
| `weekly-status` | Generates weekly status with forward-looking risks, open commitments, and evidence gap alerts |
| `prep-1on1` | Prepares for 1:1s — surfaces open commitments, recent wins, project status, feedback to give |
| `review-prep` | Builds midyear/year-end review evidence from people files, goals, and logs |
| `newsletter` | Manages the content pipeline — `curate`, `draft [topic]`, `assemble`, `ideas` |
| `monthly-reset` | End-of-month health check — stale projects, thin evidence, open commitments, newsletter seeding |
| `query-brain` | Searches the full brain and answers questions with source citations |

### Agent details

**`weekly-status`** — Scans the past 7 days of log entries, active projects, people files, and goals. Produces a status update with: current priorities, accomplishments, blockers, forward-looking risks, team updates, and a newsletter radar section. Handles sparse weeks gracefully by flagging gaps.

**`prep-1on1`** — For manager 1:1s: surfaces unresolved commitments, your accomplishments, what they'll likely ask about, and opportunities to raise. For direct report 1:1s: their recent wins, feedback to deliver, development check-in, and project status.

**`review-prep`** — Mines the full system to build a performance review draft. Ties accomplishments to goals, builds the differentiation argument for ratings, and flags goal areas with thin evidence.

**`newsletter`** — Four commands:
- `curate` — Review idea backlog + weekly status radar items, recommend 3-5 topics
- `draft [topic]` — Write an article from an idea, pulling context from the brain
- `assemble` — Compile drafted articles into an edition
- `ideas` — List all current ideas with strength assessment

**`monthly-reset`** — Runs a full system health check: stale projects (no activity in 30 days), goals with thin evidence, people files missing recent wins, unresolved commitments, expiring opportunities, and newsletter pipeline status.

---

## Cadence

| When | What to do |
|---|---|
| **During the day** | Capture as things happen — INBOX.md or structured email |
| **End of day** | Transfer any interim captures (OneNote, drafts) to INBOX.md |
| **Before 1:1s** | Run `prep-1on1` for the person you're meeting |
| **Weekly** | Process inbox, run `weekly-status` before your manager 1:1 |
| **Mid-month** | Run `newsletter curate` to review the idea pipeline |
| **End of month** | Run `monthly-reset` for a full system health check |

---

## Dashboard

A single-file HTML dashboard generated from your data. No external dependencies.

```bash
python3 05-tools/generate-dashboard.py
open 05-tools/dashboard.html       # macOS
start 05-tools/dashboard.html      # Windows
```

The dashboard shows:
- **Health metrics** — inbox count, weekly activity, stale projects, evidence gaps, open commitments
- **This week** — timeline of log entries with type badges
- **Commitments** — what you committed to and what others committed to you
- **Opportunities** — open opportunities with countdown to window close
- **People** — cards for each person with win count and freshness indicator
- **Goal evidence** — bar chart showing evidence density per goal
- **Newsletter pipeline** — ideas → drafts → published flow
- **Projects** — status board with staleness alerts

Dark mode (navy + gold) and light mode (white + navy). Toggle with the sun/moon button or press `T`.

---

## File Conventions

All files use YAML frontmatter. Required fields: `title`, `date`, `tags`.

### Log entries (`01-log/YYYY-MM-DD-topic-slug.md`)
```yaml
---
title: "MWF Team Call — Controls Discussion"
date: 2026-03-11
tags: [controls, team-sync]
type: meeting | decision | email | escalation | 1on1 | opportunity | team-call
attendees: [names]
goal: goal-file-slug (optional)
project: project-file-slug (optional)
---
```

### 1:1 entries (type: 1on1)
Include these sections in the body:
- `## Discussed`
- `## Commitments I Made`
- `## Commitments They Made`
- `## Follow-ups`

### Opportunity entries (type: opportunity)
Add to frontmatter:
```yaml
window: 2026-03-25
action-required: "Brief description of what needs to happen"
```

### People files (`03-people/firstname-lastname.md`)
Sections: Goals, Wins, Feedback Given (or Feedback Received for self/manager), Development Areas, Notes. Add dated entries under each section.

### Knowledge articles (`02-knowledge/topic-slug.md`)
Write-once references for things you explain repeatedly. Add `last-reviewed: YYYY-MM-DD` to frontmatter.

### Project files (`06-projects/project-slug.md`)
```yaml
status: active | on-hold | completed
goal: goal-file-slug
owner: "Name"
```
Sections: Summary, Key Decisions, Current Status, Blockers/Risks, Dependencies & Deadlines, Next Steps.

### Frontmatter format note
The dashboard parser supports inline YAML only: `key: value` and `key: [a, b, c]`. Block-style YAML lists (indented `- items`) are **not supported** — always use the inline array format.

---

## Design Principles

- **Low friction** — If capturing takes more than 30 seconds, you won't do it
- **Earn complexity** — Start simple, add structure only when real usage demands it
- **Outputs over storage** — The system's value is in what it produces, not what it holds
- **Evidence trails** — Every capture links back to goals and people, so review season is curation, not recall
- **Graceful degradation** — Sparse weeks still produce useful output with explicit gap flagging

---

## Requirements

- VS Code with GitHub Copilot Chat
- A model that supports custom agents (Claude Sonnet 4, GPT-4.1, Gemini 2.5 Pro, etc.)
- Python 3 (stdlib only, for dashboard generation)
- A GitHub repo (this one)
