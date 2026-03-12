---
title: Stylus Email Capture Prompt
usage: Outlook Quick Step — forward emails to Stylus LLM for structured capture
---

# Stylus Email Capture Prompt

Copy this into your Outlook Quick Step template:

---

Extract the key information from this email/content and format as markdown with the following structure:

---
title: "[Brief descriptive title]"
date: [today's date, YYYY-MM-DD]
tags: [relevant topic tags]
type: [meeting | decision | email | escalation | info | 1on1 | opportunity | team-call]
---

## Summary
[2-3 sentence summary]

## Key Points
- [Bulleted list of important details]

## Action Items
- [ ] [Any tasks or follow-ups, with owners if mentioned]

## Decisions Made
- [Any decisions, or remove this section if none]

If the content is a meeting recap, include an ## Attendees section.
If the content involves commitments or assignments, include ## Commitments I Made and ## Commitments They Made sections.
If the content describes an opportunity (visibility moment, volunteer chance, strategic opening), set the type to "opportunity" and include ## Window (when it closes) and ## Action Required.
Keep it concise and factual. No fluff.
