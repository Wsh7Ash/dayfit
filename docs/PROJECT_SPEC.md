# PROJECT_SPEC — dayfit

- **Name:** dayfit
- **Category:** productivity
- **Target user:** anyone planning a working day around existing meetings
- **Problem:** to-do lists ignore calendar commitments and the fact that tasks do
  not fit into arbitrary leftover gaps, so days are over-committed by design
- **Solution:** deterministic planner that places atomic, priority-ordered tasks
  into free intervals, inserts breaks only when they fit, and lists what does not
- **Core workflow:** `dayfit plan day.json` → chronological agenda + unscheduled
- **Must-have features:** HH:MM parsing, meeting validation, free intervals,
  priority order, breaks, unscheduled reporting, text/JSON, strict gate
- **Nice-to-have features:** dependencies, multi-day, ICS export
- **Stack:** Python 3.10+ standard library
- **Test strategy:** exact slot sequences for ordering/meetings/breaks, overflow
  cases, invalid meetings, CLI exit codes
- **Demo/result strategy:** `dayfit demo` and `examples/day.json`
- **Safety considerations:** local file only, no network, no personal data
- **Definition of done:** tests pass, install works, demo recorded, docs accurate
