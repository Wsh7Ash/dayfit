# Contributing

## Setup

```shell
python -m pip install -e . pytest
python -m pytest tests -q
```

## Invariants

- Slots never overlap and stay inside the working window.
- Every input task ends up in `slots` or `unscheduled`, exactly once.
- Breaks never displace a task that would otherwise fit.
- The planner is deterministic: same input, same output.

## Adding behaviour

1. Change the planner in `plan_day`, not the CLI.
2. Add an exact slot-sequence test (times, not just counts).
3. Update `docs/ARCHITECTURE.md` if an invariant changes.

## Style

- Standard library only.
- Times are integer minutes internally; parsing/formatting live at the edges.
