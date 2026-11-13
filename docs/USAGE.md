# Usage

## Planning tomorrow morning

```shell
dayfit plan my-day.json
```

Read the `unscheduled` section first. A plan that hides three tasks is not a
plan; move them to tomorrow or cut them before the day starts.

## Guarding a commitment

```shell
dayfit plan my-day.json --strict || echo "The day is overbooked"
```

`--strict` exits 1 when anything is unscheduled, so it can sit in a morning
script or a scheduled task that warns you.

## Choosing break settings

- Deep work: `"break_every": 120, "break_minutes": 10`
- Fragmented support day: `"break_every": 60, "break_minutes": 10`
- Back-to-back workshops: `"break_minutes": 0` to see the raw fit

## Interpreting utilization

`utilization` counts meetings and tasks, not breaks. 80–90% is realistic;
100% leaves no slack for the inevitable interruption.

## JSON output

```shell
dayfit plan my-day.json --json
```

Slot objects include `start_text` and `end_text` for display, plus numeric
minutes, so a report generator does not need to format times itself.

## Library use

```python
from dayfit import Task, plan_day, parse_time, render_text

plan = plan_day(
    parse_time("09:00"), parse_time("12:00"),
    [Task("Write notes", 45, 1), Task("Review PRs", 60, 2)],
    break_every=90, break_minutes=15,
)
print(render_text(plan))
```
