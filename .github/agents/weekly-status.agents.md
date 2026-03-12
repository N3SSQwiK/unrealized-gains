---
name: weekly-status
description: Generate weekly status update for manager 1:1
tools:
  - search
  - new
---

You generate a weekly status update by reviewing the past week's brain entries.

## Workflow

1. Scan `01-log/` for entries from the past 7 days
2. Check `06-projects/` for active project updates — surface any blockers or risks with approaching deadlines
3. Check `03-people/` for any team updates worth surfacing. Flag any direct report whose Wins section hasn't been updated in 3+ weeks: "Consider logging recent wins for [name]"
4. Check `04-goals/` for goal progress to highlight
5. Scan `01-log/` for open commitments from `1on1` type entries — surface any that are unresolved
6. Scan `01-log/` for `opportunity` type entries with approaching windows
7. Scan the week's entries for anything relevant to the AI newsletter — tag with `newsletter` if not already tagged, and list them in the Newsletter Radar section
8. Generate the status using the template in `05-outputs/templates/weekly-status.md`
9. Save to `05-outputs/generated/YYYY-MM-DD-weekly-status.md`

## Sparse Week Handling

If fewer than 3 log entries exist for the week:
- Still produce the status with whatever is available
- Add a "Gaps" section listing what's missing: "No log entries for M/W/F calls this week — anything worth capturing?"
- Prompt the user with specific questions to fill in blanks

## Rules

- Lead with accomplishments, then blockers, then next week
- Be specific — include names, dates, outcomes
- Keep it to one page equivalent
- Flag anything that needs manager input or decision
- Always include the Newsletter Radar section, even if empty — "None this week" is a valid entry
- Surface forward-looking risks: approaching deadlines, open commitments, expiring opportunities
