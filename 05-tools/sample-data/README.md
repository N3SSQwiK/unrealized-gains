---
title: Sample Data
date: 2026-03-11
---

# Sample Data

Copy these files into the main repo directories to preview the dashboard with realistic content.

```bash
# From repo root:
cp -r 05-tools/sample-data/01-log/* 01-log/
cp -r 05-tools/sample-data/03-people/* 03-people/
cp -r 05-tools/sample-data/06-projects/* 06-projects/
python3 05-tools/generate-dashboard.py
```

Remove them when you're ready to use real data:
```bash
rm 01-log/2026-03-07-decision-vendor-selection.md
rm 01-log/2026-03-09-email-ai-policy.md
rm 01-log/2026-03-10-mwf-controls-review.md
rm 01-log/2026-03-11-1on1-manager.md
rm 01-log/2026-03-11-opportunity-exec-presentation.md
rm 06-projects/control-inventory-redesign.md
```
