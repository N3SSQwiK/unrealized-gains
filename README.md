# unrealized-gains

Realize the gains.

A markdown-based second brain for work — built for people who manage teams, sit in too many meetings, and need to remember what happened three months ago. Powered by VS Code + GitHub Copilot Chat custom agents.

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
06-projects/           Active workstreams and initiatives
07-newsletter/         Content pipeline: ideas, drafts, editions
```

## How It Works

**Capture** — During or after meetings, drop raw notes into `INBOX.md`. Forward important emails to an LLM tool to structure them as markdown. Jot notes in Outlook drafts or OneNote during meetings and transfer later. Keep friction low.

**Process** — Use the `process-inbox` agent to file entries into the right location with proper metadata. Connections to existing notes are surfaced automatically. If the inbox piles up, the agent offers batch triage first.

**Query** — Use the `query-brain` agent to search across everything. "When did we decide X?" "What has Jane delivered this quarter?" "What commitments did my manager make last month?" Answers come with source references.

**Produce** — Use agents to generate weekly status updates, 1:1 prep docs, review evidence, and newsletter editions from what's already captured. The system writes the first draft; you edit.

## Agents

| Agent | Purpose |
|---|---|
| `process-inbox` | Files INBOX.md entries into the right locations with batch triage for backlogs |
| `weekly-status` | Generates weekly status with forward-looking risks, open commitments, and evidence gap alerts |
| `prep-1on1` | Prepares for manager or direct report 1:1s with context, open items, and commitments |
| `review-prep` | Builds performance review evidence from people files, goals, and logs |
| `newsletter` | Manages the content pipeline — curate ideas, draft articles, assemble editions |
| `monthly-reset` | End-of-month health check — stale projects, thin evidence, open commitments, newsletter seeding |
| `query-brain` | Searches the full brain and answers questions with citations |

## Quick Start

1. Clone this repo and open in VS Code
2. Keep `INBOX.md` open as a pinned tab
3. Set up people files for your direct reports and manager using the templates in `03-people/`
4. Add your goals to `04-goals/`
5. Start capturing — raw bullets, pasted content, whatever
6. Use Copilot Chat agents to process, query, and generate outputs

## Cadence

| When | What |
|---|---|
| Daily | Drop captures into INBOX.md, process when you have a few minutes |
| Before 1:1s | Run `prep-1on1` for the person you're meeting |
| Weekly | Run `weekly-status` before your manager 1:1 |
| Mid-month | Run `newsletter curate` to review the idea pipeline |
| End of month | Run `monthly-reset` for a full system health check |

## Design Principles

- **Low friction** — If capturing takes more than 30 seconds, you won't do it
- **Earn complexity** — Start simple, add structure only when real usage demands it
- **Outputs over storage** — The system's value is in what it produces, not what it holds
- **Evidence trails** — Every capture links back to goals and people, so review season is curation, not recall
- **Graceful degradation** — Sparse weeks still produce useful output with explicit gap flagging

## Requirements

- VS Code with GitHub Copilot Chat
- A model that supports custom agents (Claude Sonnet 4, GPT-4.1, Gemini 2.5 Pro, etc.)
- A GitHub repo (this one)
