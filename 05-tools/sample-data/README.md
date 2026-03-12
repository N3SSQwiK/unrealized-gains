---
title: Sample Data
date: 2026-03-11
---

# Sample Data

Realistic sample data demonstrating the full system: 10 log entries across all types, 3 direct reports with wins/feedback, org goals, 2 active projects, a knowledge article, and 3 newsletter ideas.

## Load Sample Data

```bash
# From repo root:
cp 05-tools/sample-data/01-log/* 01-log/
cp 05-tools/sample-data/03-people/*.md 03-people/
cp 05-tools/sample-data/04-goals/* 04-goals/
cp 05-tools/sample-data/02-knowledge/* 02-knowledge/
cp 05-tools/sample-data/06-projects/* 06-projects/
cp 05-tools/sample-data/07-newsletter/ideas/* 07-newsletter/ideas/
python3 05-tools/generate-dashboard.py
```

## Remove Sample Data

```bash
rm 01-log/2026-03-*.md
rm 03-people/jane-doe.md 03-people/bob-smith.md 03-people/maria-garcia.md
rm 04-goals/org-goals-2026.md
rm 02-knowledge/control-inventory-how-it-works.md
rm 06-projects/control-inventory-redesign.md 06-projects/ai-task-force-rollout.md
rm 07-newsletter/ideas/ai-model-approvals-expanded.md 07-newsletter/ideas/data-classification-requirements.md 07-newsletter/ideas/breach-sim-lessons.md
```
