import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from dayfit import (
    Meeting,
    PlanError,
    Task,
    demo_input,
    format_time,
    load_plan,
    parse_time,
    plan_day,
    render_text,
)
from dayfit.cli import main


def test_time_parsing_and_formatting():
    assert parse_time("09:00") == 540
    assert format_time(540) == "09:00"
    assert format_time(555) == "09:15"
    with pytest.raises(PlanError):
        parse_time("9am")
    with pytest.raises(PlanError):
        parse_time("24:00")


def test_priority_order_and_breaks():
    plan = plan_day(
        540, 720,
        [Task("C", 40, 3), Task("A", 60, 1), Task("B", 50, 2)],
        break_every=90, break_minutes=15,
    )
    assert [(s.kind, s.label, format_time(s.start), format_time(s.end)) for s in plan.slots] == [
        ("task", "A", "09:00", "10:00"),
        ("task", "B", "10:00", "10:50"),
        ("break", "break", "10:50", "11:05"),
        ("task", "C", "11:05", "11:45"),
    ]
    assert plan.unscheduled == []
    assert plan.planned_minutes == 150
    assert plan.free_minutes == 30


def test_meeting_splits_the_day():
    plan = plan_day(
        540, 660,
        [Task("long", 60, 1), Task("short", 30, 2)],
        [Meeting("call", 600, 30)],
        break_every=0, break_minutes=0,
    )
    assert [(s.label, format_time(s.start), format_time(s.end)) for s in plan.slots] == [
        ("long", "09:00", "10:00"),
        ("call", "10:00", "10:30"),
        ("short", "10:30", "11:00"),
    ]


def test_task_that_does_not_fit_is_reported():
    plan = plan_day(540, 600, [Task("too big", 90, 1)], break_every=0, break_minutes=0)
    assert plan.slots == []
    assert [task.name for task in plan.unscheduled] == ["too big"]
    assert "unscheduled: 1" in render_text(plan)


def test_break_is_skipped_when_it_would_overflow():
    plan = plan_day(
        540, 600,
        [Task("a", 60, 1), Task("b", 45, 1)],
        break_every=60, break_minutes=15,
    )
    labels = [slot.label for slot in plan.slots]
    assert labels == ["a"]
    assert [task.name for task in plan.unscheduled] == ["b"]


def test_validation_errors():
    with pytest.raises(PlanError):
        plan_day(600, 540, [])
    with pytest.raises(PlanError):
        plan_day(540, 600, [Task("x", 0)])
    with pytest.raises(PlanError):
        plan_day(540, 600, [], [Meeting("outside", 400, 30)])
    with pytest.raises(PlanError):
        plan_day(540, 900, [], [Meeting("a", 540, 60), Meeting("b", 570, 30)])


def test_demo_and_rendering():
    plan = plan_day(*demo_input())
    text = render_text(plan)
    assert "dayfit agenda" in text
    assert "planned" in text
    assert plan.utilization <= 1.0


def test_cli_plan_json_and_strict(tmp_path, capsys):
    path = tmp_path / "day.json"
    path.write_text(json.dumps({
        "start": "09:00",
        "end": "10:00",
        "break_every": 0,
        "break_minutes": 0,
        "tasks": [{"name": "a", "minutes": 30, "priority": 1},
                  {"name": "b", "minutes": 45, "priority": 2}],
    }), encoding="utf-8")
    assert main(["plan", str(path), "--strict"]) == 1
    capsys.readouterr()  # discard the text report from the strict run
    assert main(["plan", str(path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["unscheduled"][0]["name"] == "b"

    assert main(["plan", str(tmp_path / "missing.json")]) == 2
    bad = tmp_path / "bad.json"
    bad.write_text("{oops", encoding="utf-8")
    assert main(["plan", str(bad)]) == 2
    assert main(["demo"]) == 0


def test_load_plan_defaults(tmp_path):
    path = tmp_path / "day.json"
    path.write_text(json.dumps({"tasks": [{"name": "a", "minutes": 10}]}), encoding="utf-8")
    start, end, tasks, meetings, break_every, break_minutes = load_plan(str(path))
    assert (start, end, break_every, break_minutes) == (540, 1020, 90, 15)
    assert tasks[0].priority == 3 and meetings == []
