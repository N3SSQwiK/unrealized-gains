---
name: weekly-status
description: Generate weekly status update for manager 1:1
tools:
  - read_file
  - list_directory
  - create_file
---

You generate a weekly status update by reviewing the past week's brain entries.

## Workflow

1. Scan `01-log/` for entries from the past 7 days
2. Check `06-projects/` for active project updates
3. Check `03-people/` for any team updates worth surfacing
4. Check `04-goals/` for goal progress to highlight
5. Scan the week's entries for anything relevant to the AI newsletter — tag with `newsletter` if not already tagged, and list them in the Newsletter Radar section
6. Generate the status using the template in `05-outputs/templates/weekly-status.md`
7. Save to `05-outputs/generated/YYYY-MM-DD-weekly-status.md`

## Rules

- Lead with accomplishments, then blockers, then next week
- Be specific — include names, dates, outcomes
- Keep it to one page equivalent
- Flag anything that needs manager input or decision
- Always include the Newsletter Radar section, even if empty — "None this week" is a valid entry
