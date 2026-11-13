"""dayfit - fit real tasks into real hours.

Given a working window, fixed meetings, and a priority-ordered task list,
``plan_day`` produces a chronological agenda with breaks, and reports exactly
which tasks do not fit. Tasks are atomic: nothing is split across meetings, so
the output can be followed without guesswork.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Iterable, Sequence


class PlanError(ValueError):
    """Raised for malformed plans or impossible windows."""


@dataclass(frozen=True)
class Task:
    name: str
    minutes: int
    priority: int = 3


@dataclass(frozen=True)
class Meeting:
    name: str
    start: int
    minutes: int


@dataclass(frozen=True)
class Slot:
    kind: str  # meeting | task | break
    label: str
    start: int
    end: int

    @property
    def minutes(self) -> int:
        return self.end - self.start


@dataclass
class Plan:
    start: int
    end: int
    slots: list[Slot] = field(default_factory=list)
    unscheduled: list[Task] = field(default_factory=list)
    break_minutes: int = 0

    @property
    def planned_minutes(self) -> int:
        return sum(slot.minutes for slot in self.slots if slot.kind != "break")

    @property
    def free_minutes(self) -> int:
        return max(0, self.end - self.start - self.planned_minutes)

    @property
    def utilization(self) -> float:
        window = self.end - self.start
        return round(self.planned_minutes / window, 4) if window else 0.0

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["slots"] = [
            {**asdict(slot), "start_text": format_time(slot.start), "end_text": format_time(slot.end)}
            for slot in self.slots
        ]
        payload["unscheduled"] = [asdict(task) for task in self.unscheduled]
        payload["planned_minutes"] = self.planned_minutes
        payload["free_minutes"] = self.free_minutes
        payload["utilization"] = self.utilization
        return payload


def parse_time(text: str) -> int:
    """Parse ``HH:MM`` (24h) into minutes after midnight."""
    raw = text.strip()
    parts = raw.split(":")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise PlanError(f"expected HH:MM, got {text!r}")
    hours, minutes = int(parts[0]), int(parts[1])
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise PlanError(f"time out of range: {text!r}")
    return hours * 60 + minutes


def format_time(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def plan_day(
    start: int,
    end: int,
    tasks: Sequence[Task],
    meetings: Sequence[Meeting] = (),
    break_every: int = 90,
    break_minutes: int = 15,
) -> Plan:
    if start >= end:
        raise PlanError("working window must end after it starts")
    if break_every < 0 or break_minutes < 0:
        raise PlanError("break settings cannot be negative")

    ordered = [task for _, task in sorted(enumerate(tasks), key=lambda pair: (pair[1].priority, pair[0]))]
    for task in ordered:
        if task.minutes <= 0:
            raise PlanError(f"task '{task.name}' must have positive minutes")

    fixed: list[Slot] = []
    for meeting in sorted(meetings, key=lambda item: item.start):
        if meeting.minutes <= 0:
            raise PlanError(f"meeting '{meeting.name}' must have positive minutes")
        if meeting.start < start or meeting.start + meeting.minutes > end:
            raise PlanError(f"meeting '{meeting.name}' is outside the working window")
        if fixed and meeting.start < fixed[-1].end:
            raise PlanError(f"meeting '{meeting.name}' overlaps '{fixed[-1].label}'")
        fixed.append(Slot("meeting", meeting.name, meeting.start, meeting.start + meeting.minutes))

    plan = Plan(start=start, end=end, break_minutes=break_minutes)
    remaining = list(ordered)

    def free_intervals() -> list[tuple[int, int]]:
        intervals: list[tuple[int, int]] = []
        cursor = start
        for slot in fixed:
            if slot.start > cursor:
                intervals.append((cursor, slot.start))
            cursor = max(cursor, slot.end)
        if cursor < end:
            intervals.append((cursor, end))
        return intervals

    for window_start, window_end in free_intervals():
        cursor = window_start
        worked = 0
        progressed = True
        while progressed:
            progressed = False
            for task in list(remaining):
                if worked >= break_every and break_minutes and cursor + break_minutes <= window_end:
                    plan.slots.append(Slot("break", "break", cursor, cursor + break_minutes))
                    cursor += break_minutes
                    worked = 0
                if cursor + task.minutes <= window_end:
                    plan.slots.append(Slot("task", task.name, cursor, cursor + task.minutes))
                    cursor += task.minutes
                    worked += task.minutes
                    remaining.remove(task)
                    progressed = True

    plan.slots.extend(fixed)
    plan.slots.sort(key=lambda slot: slot.start)
    plan.unscheduled = remaining
    return plan


def load_plan(path: str) -> tuple[int, int, list[Task], list[Meeting], int, int]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return (
        parse_time(data.get("start", "09:00")),
        parse_time(data.get("end", "17:00")),
        [Task(str(t["name"]), int(t.get("minutes", 0)), int(t.get("priority", 3))) for t in data.get("tasks", [])],
        [
            Meeting(str(m["name"]), parse_time(str(m["start"])), int(m.get("minutes", 0)))
            for m in data.get("meetings", [])
        ],
        int(data.get("break_every", 90)),
        int(data.get("break_minutes", 15)),
    )


def render_text(plan: Plan) -> str:
    lines = ["dayfit agenda", "=" * 46]
    for slot in plan.slots:
        marker = {"meeting": "[meet]", "task": "[task]", "break": "[brk] "}[slot.kind]
        lines.append(f"{format_time(slot.start)}-{format_time(slot.end)} {marker} {slot.label}")
    lines.append("-" * 46)
    lines.append(
        f"planned {plan.planned_minutes} min of {plan.end - plan.start} "
        f"({plan.utilization:.0%}), free {plan.free_minutes} min"
    )
    if plan.unscheduled:
        lines.append(f"unscheduled: {len(plan.unscheduled)}")
        for task in plan.unscheduled:
            lines.append(f"  - {task.name} ({task.minutes} min, priority {task.priority})")
    else:
        lines.append("unscheduled: none")
    return "\n".join(lines)


def demo_input() -> tuple[int, int, list[Task], list[Meeting], int, int]:
    tasks = [
        Task("Write release notes", 45, 1),
        Task("Review pull requests", 60, 2),
        Task("Fix login regression", 90, 1),
        Task("Answer support backlog", 50, 3),
        Task("Draft next sprint", 70, 3),
    ]
    meetings = [Meeting("Standup", parse_time("09:30"), 15), Meeting("Design review", parse_time("14:00"), 60)]
    return parse_time("09:00"), parse_time("17:00"), tasks, meetings, 90, 15
