"""Command line interface for dayfit."""

from __future__ import annotations

import argparse
import json
import sys

from . import PlanError, demo_input, load_plan, plan_day, render_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dayfit",
        description="Fit a priority-ordered task list into a working day with meetings and breaks.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="plan a day from a JSON file")
    plan.add_argument("path", help="plan JSON with start, end, tasks and optional meetings")
    plan.add_argument("--json", action="store_true", help="emit JSON instead of text")
    plan.add_argument("--out", help="also write the report to this path")
    plan.add_argument("--strict", action="store_true", help="exit 1 when any task does not fit")

    sub.add_parser("demo", help="plan the built-in example day")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "demo":
        print(render_text(plan_day(*demo_input())))
        return 0

    try:
        start, end, tasks, meetings, break_every, break_minutes = load_plan(args.path)
        plan = plan_day(start, end, tasks, meetings, break_every, break_minutes)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"dayfit: {exc}", file=sys.stderr)
        return 2

    output = json.dumps(plan.to_dict(), indent=2) if args.json else render_text(plan)
    print(output)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(output + "\n")

    if args.strict and plan.unscheduled:
        print(f"dayfit: {len(plan.unscheduled)} task(s) do not fit", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
