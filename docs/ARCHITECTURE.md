# Architecture

## Flow

```text
JSON plan ──► parse_time / load_plan ──► Task[], Meeting[]
                                              │
                       meetings sorted and validated (inside window, no overlap)
                                              │
                                   free intervals = window − meetings
                                              │
                    for each interval: priority-ordered greedy placement
                       (break inserted only when it fits before the next task)
                                              ▼
                                            Plan
                              slots (sorted) + unscheduled + utilization
```

## Decisions

**Meetings are fixed points.** They are validated first (inside the window and
non-overlapping), then the remaining time is split into intervals. Tasks are
never placed across a meeting, so the agenda can be followed literally.

**Tasks are atomic.** Splitting a 90-minute task into two 45-minute pieces around
a meeting produces a plan nobody follows. If a task does not fit, the planner
tries the next one, which lets a 15-minute task use a 20-minute gap.

**Breaks are opportunistic.** A break is inserted when the accumulated work
since the last break reaches `break_every` *and* it fits inside the current
interval. It is not forced at the cost of dropping a task.

**Priority, then input order.** `priority` is ascending (1 highest). Ties keep
the order from the plan file via an index-decorated sort, so the output is
stable and duplicate task names are handled correctly.

## Invariants

- Slots never overlap and always lie inside `[start, end)`.
- `planned_minutes` excludes breaks, so utilization means "time in meetings and
  tasks".
- Every task appears exactly once in `slots` or `unscheduled`.
