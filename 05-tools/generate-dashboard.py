#!/usr/bin/env python3
"""Generate a self-contained HTML dashboard for the unrealized-gains work brain.

Usage:
    python3 05-tools/generate-dashboard.py

Outputs: 05-tools/dashboard.html

Python 3 stdlib only — no external dependencies.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_FILE = SCRIPT_DIR / "dashboard.html"

TODAY = datetime.now().date()


# ---------------------------------------------------------------------------
# Frontmatter parser (no PyYAML dependency)
# ---------------------------------------------------------------------------

def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}, content
    # Split on --- but only the first two occurrences
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)', content, re.DOTALL)
    if not match:
        return {}, content
    raw_meta, body = match.group(1), match.group(2)
    meta = {}
    for line in raw_meta.strip().split('\n'):
        if ':' not in line:
            continue
        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip()
        # Array values: [a, b, c]
        if val.startswith('[') and val.endswith(']'):
            inner = val[1:-1]
            if inner.strip():
                meta[key] = [v.strip().strip('"').strip("'") for v in inner.split(',')]
            else:
                meta[key] = []
        # Quoted strings
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            meta[key] = val[1:-1]
        else:
            meta[key] = val
    return meta, body


def parse_date(date_str):
    """Parse a date string, returning None on failure."""
    if not date_str:
        return None
    try:
        return datetime.strptime(str(date_str).strip(), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def scan_markdown_files(directory):
    """Scan a directory for .md files, parse frontmatter and body."""
    results = []
    dir_path = REPO_ROOT / directory
    if not dir_path.exists():
        return results
    for f in sorted(dir_path.rglob('*.md')):
        if f.name.startswith('.') and f.name != '.template.md':
            continue
        if f.name == '.gitkeep':
            continue
        try:
            content = f.read_text(encoding='utf-8')
        except Exception:
            continue
        meta, body = parse_frontmatter(content)
        results.append({
            'path': str(f.relative_to(REPO_ROOT)),
            'filename': f.name,
            'meta': meta,
            'body': body,
        })
    return results


def count_inbox_items():
    """Count non-empty lines in INBOX.md after the header."""
    inbox = REPO_ROOT / 'INBOX.md'
    if not inbox.exists():
        return 0
    content = inbox.read_text(encoding='utf-8')
    # Skip everything before the --- separator
    parts = content.split('---')
    if len(parts) >= 3:
        body = parts[-1]
    else:
        body = content
    lines = [l.strip() for l in body.strip().split('\n') if l.strip()]
    return len(lines)


def extract_commitments(body, direction):
    """Extract commitment items from markdown body."""
    pattern = rf'## Commitments {direction}\s*\n(.*?)(?=\n## |\Z)'
    match = re.search(pattern, body, re.DOTALL)
    if not match:
        return []
    items = []
    for line in match.group(1).strip().split('\n'):
        line = line.strip()
        if line.startswith('- '):
            items.append(line[2:].strip())
    return items


def extract_section_items(body, section_name):
    """Extract bulleted items from a markdown section."""
    pattern = rf'## {re.escape(section_name)}\s*\n(.*?)(?=\n## |\Z)'
    match = re.search(pattern, body, re.DOTALL)
    if not match:
        return []
    items = []
    for line in match.group(1).strip().split('\n'):
        line = line.strip()
        if line.startswith('- ') and not line.startswith('<!-- '):
            text = line[2:].strip()
            if text and not text.startswith('<!--'):
                items.append(text)
    return items


def days_since(date_str):
    """Calculate days between a date string and today."""
    d = parse_date(date_str)
    if not d:
        return None
    return (TODAY - d).days


def days_until(date_str):
    """Calculate days from today to a future date."""
    d = parse_date(date_str)
    if not d:
        return None
    return (d - TODAY).days


# ---------------------------------------------------------------------------
# Build dashboard data
# ---------------------------------------------------------------------------

def build_data():
    """Collect all data from the repo and return as a JSON-serializable dict."""

    # Scan all directories
    log_entries = scan_markdown_files('01-log')
    knowledge = scan_markdown_files('02-knowledge')
    people = [f for f in scan_markdown_files('03-people') if f['filename'] != '.template.md']
    goals = scan_markdown_files('04-goals')
    generated = scan_markdown_files('05-outputs/generated')
    projects = [f for f in scan_markdown_files('06-projects') if f['filename'] != '.template.md']
    newsletter_ideas = scan_markdown_files('07-newsletter/ideas')
    newsletter_drafts = scan_markdown_files('07-newsletter/drafts')
    newsletter_editions = scan_markdown_files('07-newsletter/editions')

    # --- Log entries (enriched) ---
    logs = []
    for entry in log_entries:
        m = entry['meta']
        logs.append({
            'title': m.get('title', entry['filename']),
            'date': m.get('date', ''),
            'type': m.get('type', 'info'),
            'tags': m.get('tags', []),
            'attendees': m.get('attendees', []),
            'goal': m.get('goal', ''),
            'project': m.get('project', ''),
            'path': entry['path'],
            'days_ago': days_since(m.get('date')) or 0,
        })
    logs.sort(key=lambda x: x['date'], reverse=True)

    # --- Commitments (from 1:1 entries) ---
    commitments_mine = []
    commitments_theirs = []
    for entry in log_entries:
        m = entry['meta']
        if m.get('type') != '1on1':
            continue
        date = m.get('date', '')
        title = m.get('title', '')
        for item in extract_commitments(entry['body'], 'I Made'):
            commitments_mine.append({'text': item, 'date': date, 'source': title})
        for item in extract_commitments(entry['body'], 'They Made'):
            commitments_theirs.append({'text': item, 'date': date, 'source': title})

    # --- Opportunities ---
    opportunities = []
    for entry in log_entries:
        m = entry['meta']
        if m.get('type') != 'opportunity':
            continue
        window = m.get('window', '')
        opportunities.append({
            'title': m.get('title', entry['filename']),
            'date': m.get('date', ''),
            'window': window,
            'days_remaining': days_until(window),
            'action_required': m.get('action-required', ''),
            'path': entry['path'],
        })
    opportunities.sort(key=lambda x: x.get('days_remaining') or 999)

    # --- People ---
    people_data = []
    for p in people:
        m = p['meta']
        wins = extract_section_items(p['body'], 'Wins')
        feedback_given = extract_section_items(p['body'], 'Feedback Given')
        feedback_received = extract_section_items(p['body'], 'Feedback Received')
        # Find most recent dated win
        last_win_date = None
        for w in wins:
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', w)
            if date_match:
                d = parse_date(date_match.group(1))
                if d and (last_win_date is None or d > last_win_date):
                    last_win_date = d
        people_data.append({
            'name': m.get('title', p['filename'].replace('.md', '')),
            'role': m.get('role', ''),
            'tags': m.get('tags', []),
            'wins_count': len(wins),
            'feedback_count': len(feedback_given) + len(feedback_received),
            'last_win_days': (TODAY - last_win_date).days if last_win_date else None,
            'path': p['path'],
        })

    # --- Projects ---
    projects_data = []
    for proj in projects:
        m = proj['meta']
        status = m.get('status', 'active')
        # Find most recent log entry referencing this project
        proj_slug = proj['filename'].replace('.md', '')
        last_activity = None
        for entry in log_entries:
            if entry['meta'].get('project') == proj_slug:
                d = parse_date(entry['meta'].get('date'))
                if d and (last_activity is None or d > last_activity):
                    last_activity = d
        projects_data.append({
            'title': m.get('title', proj_slug),
            'status': status,
            'owner': m.get('owner', ''),
            'goal': m.get('goal', ''),
            'last_activity_days': (TODAY - last_activity).days if last_activity else None,
            'path': proj['path'],
        })

    # --- Goals ---
    goals_data = []
    for g in goals:
        m = g['meta']
        goal_slug = g['filename'].replace('.md', '').replace('-goals-', '-')
        # Count linked log entries
        evidence_count = sum(
            1 for e in log_entries
            if e['meta'].get('goal') == goal_slug or goal_slug in str(e['meta'].get('tags', []))
        )
        goals_data.append({
            'title': m.get('title', g['filename']),
            'date': m.get('date', ''),
            'scope': m.get('scope', ''),
            'evidence_count': evidence_count,
            'path': g['path'],
        })

    # --- Newsletter ---
    newsletter = {
        'ideas_count': len(newsletter_ideas),
        'drafts_count': len(newsletter_drafts),
        'editions_count': len(newsletter_editions),
        'last_edition_date': None,
        'ideas': [{'title': i['meta'].get('title', i['filename']), 'path': i['path']}
                  for i in newsletter_ideas],
    }
    if newsletter_editions:
        dates = [parse_date(e['meta'].get('date')) for e in newsletter_editions]
        dates = [d for d in dates if d]
        if dates:
            newsletter['last_edition_date'] = max(dates).isoformat()

    # --- Health metrics ---
    week_ago = (TODAY - timedelta(days=7)).isoformat()
    this_week_logs = [l for l in logs if l['date'] >= week_ago]

    stale_projects = [p for p in projects_data
                      if p['status'] == 'active' and
                      (p['last_activity_days'] is None or p['last_activity_days'] > 30)]

    evidence_gaps = [g for g in goals_data if g['evidence_count'] < 3]

    stale_people = [p for p in people_data
                    if 'team' in (p.get('tags') or []) and
                    (p['last_win_days'] is None or p['last_win_days'] > 30)]

    # Find last monthly reset
    last_reset = None
    for g in generated:
        if 'monthly-reset' in g['filename']:
            d = parse_date(g['meta'].get('date'))
            if d and (last_reset is None or d > last_reset):
                last_reset = d

    health = {
        'inbox_count': count_inbox_items(),
        'stale_projects': len(stale_projects),
        'evidence_gaps': len(evidence_gaps),
        'stale_people': len(stale_people),
        'open_commitments_mine': len(commitments_mine),
        'open_commitments_theirs': len(commitments_theirs),
        'logs_this_week': len(this_week_logs),
        'total_files': len(log_entries) + len(knowledge) + len(people) + len(goals) + len(projects),
        'days_since_reset': (TODAY - last_reset).days if last_reset else None,
    }

    return {
        'generated_at': datetime.now().isoformat(),
        'today': TODAY.isoformat(),
        'health': health,
        'logs': logs[:50],  # Last 50 entries
        'this_week': this_week_logs,
        'commitments_mine': commitments_mine,
        'commitments_theirs': commitments_theirs,
        'opportunities': opportunities,
        'people': people_data,
        'projects': projects_data,
        'goals': goals_data,
        'newsletter': newsletter,
        'knowledge_count': len(knowledge),
    }


# ---------------------------------------------------------------------------
# HTML Template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>unrealized-gains</title>
<style>
/* ===== Reset & Base ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg-primary: #0b1024;
  --bg-secondary: #0f1632;
  --bg-card: #141c3a;
  --bg-card-hover: #192347;
  --bg-card-shadow: 0 8px 32px rgba(0,0,0,.4), 0 1px 0 rgba(201,168,76,.06) inset;
  --text-primary: #e8e6e1;
  --text-secondary: #8a94a6;
  --text-muted: #4d5672;
  --accent-gold: #c9a84c;
  --accent-gold-dim: rgba(201,168,76,.15);
  --accent-gold-glow: rgba(201,168,76,.08);
  --accent-blue: #5b8def;
  --accent-green: #4ade80;
  --accent-red: #f87171;
  --accent-yellow: #fbbf24;
  --accent-purple: #a78bfa;
  --accent-cyan: #22d3ee;
  --border: rgba(201,168,76,.1);
  --border-strong: rgba(201,168,76,.2);
  --card-radius: 8px;
  --badge-radius: 4px;
  --gold-line: 2px solid var(--accent-gold);
  --type-meeting: #5b8def;
  --type-decision: #4ade80;
  --type-1on1: #a78bfa;
  --type-opportunity: #c9a84c;
  --type-team-call: #64748b;
  --type-email: #22d3ee;
  --type-escalation: #f59e0b;
  --type-info: #64748b;
}

[data-theme="light"] {
  --bg-primary: #f5f6f8;
  --bg-secondary: #eceef2;
  --bg-card: #ffffff;
  --bg-card-hover: #fafbfc;
  --bg-card-shadow: 0 1px 3px rgba(0,45,114,.06), 0 8px 24px rgba(0,45,114,.04);
  --text-primary: #1a1f36;
  --text-secondary: #4b5563;
  --text-muted: #9ca3af;
  --accent-gold: #96792a;
  --accent-gold-dim: rgba(150,121,42,.08);
  --accent-gold-glow: rgba(150,121,42,.04);
  --accent-blue: #056dae;
  --accent-green: #057a2e;
  --accent-red: #c41e1e;
  --accent-yellow: #a16207;
  --accent-purple: #7c3aed;
  --accent-cyan: #0e7490;
  --border: rgba(0,45,114,.08);
  --border-strong: rgba(0,45,114,.14);
  --card-radius: 8px;
  --gold-line: 2px solid #002d72;
  --type-meeting: #2563eb;
  --type-decision: #16a34a;
  --type-1on1: #7c3aed;
  --type-opportunity: #96792a;
  --type-team-call: #4b5563;
  --type-email: #0e7490;
  --type-escalation: #d97706;
  --type-info: #6b7280;
}

/* ===== Noise texture ===== */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 0;
  opacity: .035;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 256px;
}
[data-theme="light"] body::before { opacity: .02; }

body {
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', sans-serif;
  font-size: 15px;
  line-height: 1.55;
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  transition: background .4s ease, color .4s ease;
  -webkit-font-smoothing: antialiased;
}

/* ===== Animations ===== */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}

.animate-in {
  animation: fadeUp .5s cubic-bezier(.22,1,.36,1) backwards;
}

/* ===== Layout ===== */
.dashboard {
  position: relative;
  z-index: 1;
  max-width: 1440px;
  margin: 0 auto;
  padding: 32px 40px;
}

/* ===== Header ===== */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border);
  position: relative;
  animation: fadeUp .5s cubic-bezier(.22,1,.36,1) backwards;
}
.header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 120px;
  height: 2px;
  background: linear-gradient(90deg, var(--accent-gold), transparent);
}
[data-theme="light"] .header::after {
  background: linear-gradient(90deg, #002d72, transparent);
}
.header h1 {
  font-size: 22px;
  font-weight: 300;
  letter-spacing: 3px;
  text-transform: uppercase;
}
.header h1 .gold { color: var(--accent-gold); font-weight: 400; }
[data-theme="light"] .header h1 .gold { color: #002d72; }
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}
.header-meta {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: .5px;
  text-transform: uppercase;
}
.theme-toggle {
  background: transparent;
  border: 1px solid var(--border-strong);
  color: var(--text-secondary);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  transition: all .3s;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1;
}
.theme-toggle:hover {
  border-color: var(--accent-gold);
  color: var(--accent-gold);
  box-shadow: 0 0 16px var(--accent-gold-dim);
  transform: rotate(15deg);
}
[data-theme="light"] .theme-toggle:hover {
  border-color: #002d72;
  color: #002d72;
  box-shadow: 0 0 16px rgba(0,45,114,.1);
}
/* Sun icon in dark mode, moon in light */
.theme-toggle .icon-sun { display: inline; }
.theme-toggle .icon-moon { display: none; }
[data-theme="light"] .theme-toggle .icon-sun { display: none; }
[data-theme="light"] .theme-toggle .icon-moon { display: inline; }

/* ===== Grid ===== */
.grid { display: grid; gap: 16px; margin-bottom: 20px; }
.grid-5 { grid-template-columns: repeat(5, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-1 { grid-template-columns: 1fr; }
.col-gap { display: flex; flex-direction: column; gap: 16px; }

@media (max-width: 1200px) { .grid-5 { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 900px) { .grid-5, .grid-3 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) {
  .grid-5, .grid-3, .grid-2 { grid-template-columns: 1fr; }
  .dashboard { padding: 20px 16px; }
}

/* ===== Cards ===== */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: var(--gold-line);
  border-radius: var(--card-radius);
  padding: 24px;
  box-shadow: var(--bg-card-shadow);
  transition: transform .25s cubic-bezier(.22,1,.36,1), box-shadow .25s ease, border-color .25s ease;
  position: relative;
  overflow: hidden;
}
.card:hover {
  transform: translateY(-2px);
  border-color: var(--border-strong);
  box-shadow: var(--bg-card-shadow), 0 0 0 1px var(--accent-gold-dim);
}
[data-theme="light"] .card:hover {
  box-shadow: 0 2px 8px rgba(0,45,114,.08), 0 12px 32px rgba(0,45,114,.06);
}
.card h2 {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--accent-gold);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}
[data-theme="light"] .card h2 { color: #002d72; }
.card h2::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ===== Metric Cards ===== */
.metric {
  text-align: center;
  padding: 28px 16px;
  border-left-color: transparent;
  border-left-width: 1px;
  border-left-style: solid;
}
.metric .value {
  font-size: 40px;
  font-weight: 200;
  line-height: 1;
  margin-bottom: 10px;
  letter-spacing: -1px;
  font-feature-settings: 'tnum';
  position: relative;
  z-index: 1;
}
.metric .glow {
  position: absolute;
  inset: 0;
  border-radius: var(--card-radius);
  opacity: 0;
  transition: opacity .3s;
  z-index: 0;
  pointer-events: none;
}
.metric:hover .glow { opacity: 1; }
.metric .label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1.2px;
  font-weight: 500;
  position: relative;
  z-index: 1;
}
.metric.ok .value { color: var(--accent-green); }
.metric.ok .glow { background: radial-gradient(ellipse at center, rgba(74,222,128,.06) 0%, transparent 70%); }
.metric.warn .value { color: var(--accent-yellow); }
.metric.warn .glow { background: radial-gradient(ellipse at center, rgba(251,191,36,.06) 0%, transparent 70%); }
.metric.alert .value { color: var(--accent-gold); }
.metric.alert .glow { background: radial-gradient(ellipse at center, rgba(201,168,76,.08) 0%, transparent 70%); }
.metric.neutral .value { color: var(--text-primary); }

/* ===== Section Headers ===== */
.section-title {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 20px;
  color: var(--accent-gold);
  display: flex;
  align-items: center;
  gap: 12px;
}
[data-theme="light"] .section-title { color: #002d72; }
.section-title .count {
  font-size: 10px;
  color: var(--text-muted);
  font-weight: 400;
  letter-spacing: .5px;
}

/* ===== Type Badges ===== */
.badge {
  display: inline-flex;
  align-items: center;
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .8px;
  padding: 3px 8px;
  border-radius: var(--badge-radius);
  flex-shrink: 0;
}
.badge-meeting { background: rgba(91,141,239,.15); color: var(--type-meeting); }
.badge-decision { background: rgba(74,222,128,.15); color: var(--type-decision); }
.badge-1on1 { background: rgba(167,139,250,.15); color: var(--type-1on1); }
.badge-opportunity { background: var(--accent-gold-dim); color: var(--accent-gold); }
.badge-team-call { background: rgba(100,116,139,.15); color: var(--type-team-call); }
.badge-email { background: rgba(34,211,238,.15); color: var(--type-email); }
.badge-escalation { background: rgba(245,158,11,.15); color: var(--type-escalation); }
.badge-info { background: rgba(100,116,139,.15); color: var(--type-info); }
.badge-active { background: rgba(74,222,128,.15); color: var(--accent-green); }
.badge-on-hold { background: rgba(251,191,36,.15); color: var(--accent-yellow); }
.badge-completed { background: rgba(100,116,139,.15); color: var(--text-muted); }

/* ===== Timeline ===== */
.timeline { position: relative; padding-left: 20px; }
.timeline::before {
  content: '';
  position: absolute;
  left: 3px;
  top: 8px;
  bottom: 8px;
  width: 1px;
  background: linear-gradient(to bottom, var(--accent-gold), transparent);
}
[data-theme="light"] .timeline::before {
  background: linear-gradient(to bottom, #002d72, transparent);
}
.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  position: relative;
}
.timeline-item::before {
  content: '';
  position: absolute;
  left: -20px;
  top: 16px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent-gold);
  box-shadow: 0 0 8px var(--accent-gold-dim);
}
[data-theme="light"] .timeline-item::before {
  background: #002d72;
  box-shadow: 0 0 8px rgba(0,45,114,.15);
}
.timeline-date {
  font-size: 11px;
  color: var(--text-muted);
  min-width: 44px;
  flex-shrink: 0;
  font-feature-settings: 'tnum';
  letter-spacing: .3px;
}
.timeline-title {
  font-size: 13px;
  flex: 1;
  line-height: 1.4;
}
.timeline-meta {
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: .3px;
  padding: 2px 6px;
  background: var(--accent-gold-dim);
  border-radius: 3px;
}

/* ===== Commitment Items ===== */
.commitment-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
  line-height: 1.5;
}
.commitment-item:last-child { border-bottom: none; }
.commitment-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}
.commitment-date {
  font-size: 10px;
  color: var(--text-muted);
  font-feature-settings: 'tnum';
  letter-spacing: .3px;
}
.commitment-source {
  font-size: 10px;
  color: var(--accent-blue);
  letter-spacing: .3px;
}

/* ===== Opportunity Cards ===== */
.opp-item {
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}
.opp-item:last-child { border-bottom: none; }
.opp-window {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: var(--badge-radius);
  display: inline-block;
  margin-bottom: 8px;
  letter-spacing: .5px;
  text-transform: uppercase;
}
.opp-green { background: rgba(74,222,128,.1); color: var(--accent-green); }
.opp-yellow { background: rgba(251,191,36,.1); color: var(--accent-yellow); }
.opp-red { background: rgba(248,113,113,.1); color: var(--accent-red); }
.opp-title { font-size: 14px; font-weight: 500; margin-bottom: 4px; }
.opp-action { font-size: 12px; color: var(--text-secondary); line-height: 1.4; }

/* ===== People Cards ===== */
.person-card {
  padding: 20px 24px;
  position: relative;
}
.person-card::before {
  content: '';
  position: absolute;
  top: 20px;
  right: 20px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-green);
  box-shadow: 0 0 6px rgba(74,222,128,.3);
}
.person-card.stale::before { background: var(--accent-yellow); box-shadow: 0 0 6px rgba(251,191,36,.3); }
.person-card.no-data::before { background: var(--text-muted); box-shadow: none; }
.person-name { font-size: 15px; font-weight: 500; margin-bottom: 2px; letter-spacing: .2px; }
.person-role { font-size: 11px; color: var(--text-muted); margin-bottom: 16px; letter-spacing: .3px; text-transform: uppercase; }
.person-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.person-stat {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: .3px;
}
.person-stat-value {
  font-size: 20px;
  font-weight: 200;
  color: var(--text-primary);
  display: block;
  font-feature-settings: 'tnum';
  line-height: 1.2;
}
.person-stat.stale .person-stat-value { color: var(--accent-yellow); }
.person-freshness {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  letter-spacing: .3px;
}

/* ===== Evidence Bars ===== */
.evidence-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}
.evidence-row:last-child { border-bottom: none; }
.evidence-label {
  font-size: 13px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.evidence-bar-wrap {
  width: 140px;
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
  flex-shrink: 0;
}
.evidence-bar {
  height: 100%;
  border-radius: 2px;
  transition: width .6s cubic-bezier(.22,1,.36,1);
}
.evidence-bar.low {
  background: linear-gradient(90deg, var(--accent-yellow), var(--accent-gold));
}
.evidence-bar.good {
  background: linear-gradient(90deg, var(--accent-gold), var(--accent-green));
}
.evidence-count {
  font-size: 14px;
  font-weight: 300;
  min-width: 28px;
  text-align: right;
  font-feature-settings: 'tnum';
}

/* ===== Newsletter Pipeline ===== */
.pipeline {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 24px 0;
  position: relative;
}
.pipeline-track {
  position: absolute;
  top: 50%;
  left: 15%;
  right: 15%;
  height: 2px;
  background: linear-gradient(90deg, var(--border), var(--accent-gold), var(--accent-green));
  transform: translateY(-1px);
  z-index: 0;
  border-radius: 1px;
}
[data-theme="light"] .pipeline-track {
  background: linear-gradient(90deg, var(--border), #002d72, var(--accent-green));
}
.pipeline-stage {
  text-align: center;
  padding: 20px 32px;
  background: var(--bg-card);
  border-radius: var(--card-radius);
  border: 1px solid var(--border);
  position: relative;
  z-index: 1;
  transition: border-color .3s;
}
.pipeline-stage:hover { border-color: var(--border-strong); }
.pipeline-stage .value {
  font-size: 32px;
  font-weight: 200;
  color: var(--accent-gold);
  font-feature-settings: 'tnum';
  letter-spacing: -1px;
}
[data-theme="light"] .pipeline-stage .value { color: #002d72; }
.pipeline-stage .label {
  font-size: 9px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1.2px;
  font-weight: 600;
  margin-top: 4px;
}
.pipeline-spacer { width: 48px; flex-shrink: 0; }
.pipeline-meta {
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: .3px;
  margin-top: 8px;
}

/* ===== Project Items ===== */
.project-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
.project-item:last-child { border-bottom: none; }
.project-info { flex: 1; }
.project-title { font-size: 13px; font-weight: 500; letter-spacing: .2px; }
.project-meta { font-size: 10px; color: var(--text-muted); margin-top: 2px; letter-spacing: .3px; }
.stale-tag {
  font-size: 9px;
  font-weight: 600;
  letter-spacing: .8px;
  text-transform: uppercase;
  color: var(--accent-yellow);
  padding: 2px 8px;
  background: rgba(251,191,36,.1);
  border-radius: var(--badge-radius);
  margin-left: 8px;
}

/* ===== Empty States ===== */
.empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
  font-size: 12px;
  letter-spacing: .3px;
}
.empty::before {
  content: '';
  display: block;
  width: 40px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
  margin: 0 auto 16px;
}
[data-theme="light"] .empty::before {
  background: linear-gradient(90deg, transparent, #002d72, transparent);
}
.empty-text {
  font-style: italic;
  font-size: 13px;
}
</style>
</head>
<body>

<div class="dashboard" id="app"></div>

<script>
const DATA = __DASHBOARD_DATA__;

function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  html.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
  localStorage.setItem('ug-theme', html.getAttribute('data-theme'));
}
const saved = localStorage.getItem('ug-theme');
if (saved) document.documentElement.setAttribute('data-theme', saved);
document.addEventListener('keydown', e => {
  if ((e.key === 't' || e.key === 'T') && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') toggleTheme();
});

function h(tag, attrs, ...children) {
  const el = document.createElement(tag);
  if (attrs) Object.entries(attrs).forEach(([k, v]) => {
    if (k === 'className') el.className = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2).toLowerCase(), v);
    else el.setAttribute(k, v);
  });
  children.flat().forEach(c => {
    if (c == null) return;
    el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  });
  return el;
}

function metricClass(value, warnAt, alertAt, invert) {
  if (value === null || value === undefined) return 'neutral';
  if (invert) return value <= warnAt ? 'ok' : value <= alertAt ? 'warn' : 'alert';
  return value >= alertAt ? 'alert' : value >= warnAt ? 'warn' : 'ok';
}

function typeBadge(type) {
  const t = (type || 'info');
  return h('span', {className: 'badge badge-' + t.replace(/\s+/g, '-')}, t);
}

function statusBadge(status) {
  return h('span', {className: 'badge badge-' + (status || 'active').replace(/\s+/g, '-')}, status || 'active');
}

function formatDate(d) {
  if (!d) return '\u2014';
  return d.slice(5);
}

function delay(i) { return 'animation-delay:' + (i * 60) + 'ms'; }

function renderHeader() {
  return h('div', {className: 'header'},
    h('h1', null,
      h('span', {className: 'gold'}, 'unrealized'),
      '\u2009\u2014\u2009gains'
    ),
    h('div', {className: 'header-right'},
      h('span', {className: 'header-meta'}, new Date(DATA.generated_at).toLocaleDateString('en-US', {month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'})),
      h('button', {className: 'theme-toggle', onClick: toggleTheme, title: 'Toggle theme (T)'},
        h('span', {className: 'icon-sun'}, '\u2600'),
        h('span', {className: 'icon-moon'}, '\u263E')
      )
    )
  );
}

function renderHealthMetrics() {
  const hd = DATA.health;
  const metrics = [
    {label: 'Inbox', value: hd.inbox_count, warn: 3, alert: 6, invert: false},
    {label: 'This Week', value: hd.logs_this_week, warn: 3, alert: 1, invert: true},
    {label: 'Stale Projects', value: hd.stale_projects, warn: 1, alert: 2, invert: false},
    {label: 'Evidence Gaps', value: hd.evidence_gaps, warn: 1, alert: 3, invert: false},
    {label: 'Commitments', value: hd.open_commitments_mine + hd.open_commitments_theirs, warn: 3, alert: 6, invert: false},
  ];

  return h('div', {className: 'grid grid-5'},
    ...metrics.map((m, i) => {
      const cls = metricClass(m.value, m.warn, m.alert, m.invert);
      return h('div', {className: 'card metric animate-in ' + cls, style: delay(i + 1)},
        h('div', {className: 'glow'}),
        h('div', {className: 'value'}, String(m.value ?? '\u2014')),
        h('div', {className: 'label'}, m.label)
      );
    })
  );
}

function renderThisWeek() {
  const logs = DATA.this_week;
  if (logs.length === 0) {
    return h('div', {className: 'card'},
      h('h2', null, 'This Week'),
      h('div', {className: 'empty'},
        h('div', {className: 'empty-text'}, 'No captures this week. Start logging.')
      )
    );
  }
  const timeline = h('div', {className: 'timeline'});
  logs.forEach(l => {
    timeline.appendChild(
      h('div', {className: 'timeline-item'},
        h('span', {className: 'timeline-date'}, formatDate(l.date)),
        typeBadge(l.type),
        h('span', {className: 'timeline-title'}, l.title),
        l.goal ? h('span', {className: 'timeline-meta'}, l.goal) : null
      )
    );
  });
  return h('div', {className: 'card'},
    h('h2', null, 'This Week'),
    timeline
  );
}

function renderCommitments() {
  function renderList(items, emptyMsg) {
    if (items.length === 0) {
      return h('div', {className: 'empty'}, h('div', {className: 'empty-text'}, emptyMsg));
    }
    return h('div', null, ...items.map(c =>
      h('div', {className: 'commitment-item'},
        h('div', null, c.text),
        h('div', {className: 'commitment-footer'},
          h('span', {className: 'commitment-date'}, formatDate(c.date)),
          h('span', {className: 'commitment-source'}, c.source)
        )
      )
    ));
  }
  return h('div', {className: 'grid grid-2'},
    h('div', {className: 'card'},
      h('h2', null, 'I Committed To'),
      renderList(DATA.commitments_mine, 'No open commitments')
    ),
    h('div', {className: 'card'},
      h('h2', null, 'They Committed To'),
      renderList(DATA.commitments_theirs, 'No open commitments')
    )
  );
}

function renderOpportunities() {
  if (DATA.opportunities.length === 0) {
    return h('div', {className: 'card'},
      h('h2', null, 'Opportunities'),
      h('div', {className: 'empty'}, h('div', {className: 'empty-text'}, 'No open opportunities'))
    );
  }
  return h('div', {className: 'card'},
    h('h2', null, 'Opportunities'),
    ...DATA.opportunities.map(o => {
      const dr = o.days_remaining;
      const expired = dr !== null && dr < 0;
      const cls = dr === null ? 'opp-yellow' : expired ? 'opp-red' : dr > 14 ? 'opp-green' : 'opp-yellow';
      const label = dr === null ? 'No window' : expired ? 'Past due' : dr + 'd remaining';
      return h('div', {className: 'opp-item'},
        h('span', {className: 'opp-window ' + cls}, label),
        h('div', {className: 'opp-title'}, o.title),
        o.action_required ? h('div', {className: 'opp-action'}, o.action_required) : null
      );
    })
  );
}

function renderPeople() {
  if (DATA.people.length === 0) {
    return h('div', {className: 'card'}, h('h2', null, 'People'),
      h('div', {className: 'empty'}, h('div', {className: 'empty-text'}, 'No people files yet')));
  }
  return h('div', null,
    h('div', {className: 'section-title'}, 'People'),
    h('div', {className: 'grid grid-3'},
      ...DATA.people.map((p, i) => {
        const stale = p.last_win_days !== null && p.last_win_days > 30;
        const noData = p.last_win_days === null;
        const winsLabel = p.last_win_days !== null ? p.last_win_days + ' days since last win' : 'No wins logged yet';
        const cardCls = 'card person-card animate-in' + (stale ? ' stale' : '') + (noData ? ' no-data' : '');
        return h('div', {className: cardCls, style: delay(i)},
          h('div', {className: 'person-name'}, p.name),
          h('div', {className: 'person-role'}, p.role || '\u2014'),
          h('div', {className: 'person-stats'},
            h('div', {className: 'person-stat'},
              h('span', {className: 'person-stat-value'}, String(p.wins_count)),
              'wins'
            ),
            h('div', {className: 'person-stat'},
              h('span', {className: 'person-stat-value'}, String(p.feedback_count)),
              'feedback'
            )
          ),
          h('div', {className: 'person-freshness'}, winsLabel)
        );
      })
    )
  );
}

function renderGoals() {
  if (DATA.goals.length === 0) {
    return h('div', {className: 'card'}, h('h2', null, 'Goal Evidence'),
      h('div', {className: 'empty'}, h('div', {className: 'empty-text'}, 'No goals created yet')));
  }
  const maxEvidence = Math.max(10, ...DATA.goals.map(g => g.evidence_count));
  return h('div', {className: 'card'},
    h('h2', null, 'Goal Evidence'),
    ...DATA.goals.map(g => {
      const pct = Math.min(100, (g.evidence_count / maxEvidence) * 100);
      const barCls = g.evidence_count < 3 ? 'low' : 'good';
      const countColor = g.evidence_count < 3 ? 'color:var(--accent-yellow)' : 'color:var(--accent-green)';
      return h('div', {className: 'evidence-row'},
        h('span', {className: 'evidence-label'}, g.title),
        h('div', {className: 'evidence-bar-wrap'},
          h('div', {className: 'evidence-bar ' + barCls, style: 'width:' + pct + '%'})
        ),
        h('span', {className: 'evidence-count', style: countColor}, String(g.evidence_count))
      );
    })
  );
}

function renderNewsletter() {
  const nl = DATA.newsletter;
  return h('div', {className: 'card'},
    h('h2', null, 'Newsletter Pipeline'),
    h('div', {className: 'pipeline'},
      h('div', {className: 'pipeline-track'}),
      h('div', {className: 'pipeline-stage'},
        h('div', {className: 'value'}, String(nl.ideas_count)),
        h('div', {className: 'label'}, 'Ideas')
      ),
      h('div', {className: 'pipeline-spacer'}),
      h('div', {className: 'pipeline-stage'},
        h('div', {className: 'value'}, String(nl.drafts_count)),
        h('div', {className: 'label'}, 'Drafts')
      ),
      h('div', {className: 'pipeline-spacer'}),
      h('div', {className: 'pipeline-stage'},
        h('div', {className: 'value'}, String(nl.editions_count)),
        h('div', {className: 'label'}, 'Published')
      )
    ),
    h('div', {className: 'pipeline-meta'},
      nl.last_edition_date ? 'Last edition: ' + nl.last_edition_date : 'No editions published yet'
    )
  );
}

function renderProjects() {
  if (DATA.projects.length === 0) {
    return h('div', {className: 'card'}, h('h2', null, 'Projects'),
      h('div', {className: 'empty'}, h('div', {className: 'empty-text'}, 'No projects tracked yet')));
  }
  return h('div', {className: 'card'},
    h('h2', null, 'Projects'),
    ...DATA.projects.map(p => {
      const activity = p.last_activity_days !== null
        ? p.last_activity_days + 'd ago'
        : 'No activity';
      const stale = p.status === 'active' && (p.last_activity_days === null || p.last_activity_days > 30);
      return h('div', {className: 'project-item'},
        h('div', {className: 'project-info'},
          h('div', {className: 'project-title'}, p.title),
          h('div', {className: 'project-meta'},
            (p.owner ? p.owner + ' \u00b7 ' : '') + activity
          )
        ),
        statusBadge(p.status),
        stale ? h('span', {className: 'stale-tag'}, 'Stale') : null
      );
    })
  );
}

function renderRecentLogs() {
  const logs = DATA.logs.slice(0, 20);
  if (logs.length === 0) {
    return h('div', {className: 'card'}, h('h2', null, 'Recent Activity'),
      h('div', {className: 'empty'}, h('div', {className: 'empty-text'}, 'Start capturing')));
  }
  const timeline = h('div', {className: 'timeline'});
  logs.forEach(l => {
    timeline.appendChild(
      h('div', {className: 'timeline-item'},
        h('span', {className: 'timeline-date'}, formatDate(l.date)),
        typeBadge(l.type),
        h('span', {className: 'timeline-title'}, l.title),
        l.goal ? h('span', {className: 'timeline-meta'}, l.goal) : null
      )
    );
  });
  return h('div', {className: 'card'},
    h('h2', null, 'Recent Activity'),
    timeline
  );
}

function render() {
  const app = document.getElementById('app');
  app.innerHTML = '';
  app.appendChild(renderHeader());
  app.appendChild(renderHealthMetrics());

  const mainGrid = h('div', {className: 'grid grid-2'});
  const left = h('div', {className: 'col-gap animate-in', style: delay(6)});
  left.appendChild(renderThisWeek());
  left.appendChild(renderCommitments());
  left.appendChild(renderRecentLogs());

  const right = h('div', {className: 'col-gap animate-in', style: delay(7)});
  right.appendChild(renderOpportunities());
  right.appendChild(renderGoals());
  right.appendChild(renderNewsletter());
  right.appendChild(renderProjects());

  mainGrid.appendChild(left);
  mainGrid.appendChild(right);
  app.appendChild(mainGrid);
  app.appendChild(renderPeople());
}

render();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data = build_data()
    data_json = json.dumps(data, indent=None, default=str)
    html = HTML_TEMPLATE.replace('__DASHBOARD_DATA__', data_json)
    OUTPUT_FILE.write_text(html, encoding='utf-8')
    print(f"Dashboard generated: {OUTPUT_FILE}")
    print(f"  Total files: {data['health']['total_files']}")
    print(f"  Logs this week: {data['health']['logs_this_week']}")
    print(f"  Inbox items: {data['health']['inbox_count']}")


if __name__ == '__main__':
    main()
