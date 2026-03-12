# unrealized-gains

Realize the gains.

A markdown-based second brain for work — built for people who manage teams, sit in too many meetings, and need to remember what happened three months ago. Powered by VS Code + GitHub Copilot Chat custom agents.

## The Problem

Information flows constantly — meetings, emails, chats, decisions — and most of it evaporates. When it's time to write a status update, prep for a review, or answer "didn't we already discuss this?", you're relying on memory. That's an unrealized gain: valuable information captured by your brain but never organized for retrieval.

## The System

```
INBOX.md               Always-open scratchpad for raw captures
01-log/                Chronological record — meetings, decisions, emails
02-knowledge/          Canonical references — write once, link forever
03-people/             One file per direct report + yourself
04-goals/              Org and individual goals with evidence trails
05-outputs/            Templates and generated artifacts
06-projects/           Active workstreams and initiatives
```

## How It Works

**Capture** — During or after meetings, drop raw notes into `INBOX.md`. Forward important emails to an LLM tool to structure them as markdown. Keep friction low.

**Process** — Use the `process-inbox` agent to file entries into the right location with proper metadata. Connections to existing notes are surfaced automatically.

**Query** — Use the `query-brain` agent to search across everything. "When did we decide X?" "What has Jane delivered this quarter?" Answers come with source references.

**Produce** — Use agents to generate weekly status updates, review prep docs, and briefing summaries from what's already captured. The system writes the first draft; you edit.

## Agents

| Agent | Purpose |
|---|---|
| `process-inbox` | Files INBOX.md entries into the right locations |
| `weekly-status` | Generates weekly status from the past 7 days of log entries |
| `review-prep` | Builds performance review evidence from people files, goals, and logs |
| `query-brain` | Searches the full brain and answers questions with citations |

## Quick Start

1. Clone this repo and open in VS Code
2. Keep `INBOX.md` open as a pinned tab
3. Start capturing — raw bullets, pasted content, whatever
4. Use Copilot Chat agents to process and query
5. Customize `03-people/`, `04-goals/`, and `06-projects/` to match your team

## Design Principles

- **Low friction** — If capturing takes more than 30 seconds, you won't do it
- **Earn complexity** — Start simple, add structure only when real usage demands it
- **Outputs over storage** — The system's value is in what it produces, not what it holds
- **Evidence trails** — Every capture links back to goals and people, so review season is curation, not recall

## Requirements

- VS Code with GitHub Copilot Chat
- A model that supports custom agents (Claude Sonnet 4, GPT-4.1, Gemini 2.5 Pro, etc.)
- A GitHub repo (this one)
