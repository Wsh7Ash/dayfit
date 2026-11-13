# Changelog

## [1.0.0] - 2026-11-14

### Added

- `dayfit plan` for priority-ordered placement of atomic tasks into a working
  window around fixed meetings.
- Opportunistic breaks controlled by `break_every` / `break_minutes`.
- Explicit `unscheduled` reporting, utilization summary, `--strict` gate.
- Text and JSON output with `--out`; `dayfit demo`.
- pytest suite covering ordering, meetings, breaks, overflow and CLI exit codes.
