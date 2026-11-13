# dayfit

**Turn a priority list and a calendar into a plan you can actually follow.**

## Why

A to-do list ignores the two things that decide whether a day works: meetings
already on the calendar, and the fact that tasks cannot be squeezed into
leftover gaps. `dayfit` takes a working window, fixed meetings, breaks and
atomic tasks, then shows the chronological agenda and names every task that does
not fit — before the day starts, not at 18:00.

## Features

- Priority-first placement (priority 1 goes first, ties keep input order)
- Fixed meetings split the day into free intervals; tasks never overlap them
- Configurable break cadence inserted only when it fits
- Explicit `unscheduled` list instead of silent over-commitment
- Utilization and free-time summary
- Text or JSON output, optional `--strict` gate for scripts

## Example

`dayfit demo`:

```text
dayfit agenda
==============================================
09:30-09:45 [meet] Standup
09:45-10:30 [task] Write release notes
10:30-12:00 [task] Fix login regression
12:00-12:15 [brk]  break
12:15-13:15 [task] Review pull requests
14:00-15:00 [meet] Design review
15:00-15:50 [task] Answer support backlog
15:50-17:00 [task] Draft next sprint
----------------------------------------------
planned 390 min of 480 (81%), free 90 min
unscheduled: none
```

## Architecture

```text
src/dayfit/__init__.py   time parsing, interval splitting, greedy placement
src/dayfit/cli.py        plan / demo commands and exit codes
tests/test_dayfit.py     ordering, meetings, breaks, overflow, CLI
```

Free intervals are derived from meetings, then each interval is filled with
priority-ordered tasks. A task is placed only if it fits whole; otherwise the
next task is tried, so a small task can fill a gap a large one would waste.

## Requirements

- Python 3.10+
- pytest for tests

## Installation

```shell
git clone https://github.com/Wsh7Ash/dayfit.git
cd dayfit
python -m pip install -e .
```

## Quick start

```shell
dayfit demo
dayfit plan examples/day.json
```

## Usage

```shell
# Strict mode: exit 1 if anything does not fit (useful before committing to a day)
dayfit plan examples/day.json --strict

# Machine-readable plan
dayfit plan examples/day.json --json --out results/day.json
```

Plan file:

```json
{
  "start": "09:00",
  "end": "17:30",
  "break_every": 90,
  "break_minutes": 15,
  "meetings": [{"name": "Standup", "start": "09:30", "minutes": 15}],
  "tasks": [
    {"name": "Fix login regression", "minutes": 90, "priority": 1},
    {"name": "Review pull requests", "minutes": 60, "priority": 2}
  ]
}
```

Exit codes: `0` plan produced, `1` `--strict` and tasks did not fit, `2` invalid
input.

## Configuration

No config file. Defaults: window `09:00-17:00`, break every `90` minutes for
`15` minutes, task priority `3`.

## Testing

```shell
python -m pip install -e . pytest
python -m pytest tests -q
```

## Project structure

```text
dayfit/
├─ src/dayfit/          planner + CLI
├─ tests/               pytest suite
├─ examples/            sample day
├─ docs/                architecture, usage, spec
├─ results/             generated plans
└─ .github/workflows/   CI
```

## Limitations

- Tasks are atomic; the planner never splits a task across a meeting.
- Breaks are inserted only between tasks, never inside one.
- No multi-day planning, calendars, or time zones.
- Priorities are numbers; there is no dependency graph between tasks.

## Roadmap

- Task dependencies and earliest-start constraints
- Multi-day planning
- ICS export

## License

MIT — see `LICENSE`.
