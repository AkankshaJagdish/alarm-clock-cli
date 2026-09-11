#!/usr/bin/env python3
"""A small, single-alarm command-line alarm clock."""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Callable, TextIO


def parse_alarm_time(value: str) -> tuple[int, int]:
    """Parse a strict 24-hour HH:MM value, raising ArgumentTypeError on errors."""
    try:
        hour_text, minute_text = value.split(":")
    except ValueError as error:
        raise argparse.ArgumentTypeError("time must be in HH:MM format (for example, 23:00)") from error

    if len(hour_text) != 2 or len(minute_text) != 2 or not hour_text.isdigit() or not minute_text.isdigit():
        raise argparse.ArgumentTypeError("time must be in HH:MM format (for example, 23:00)")

    hour, minute = int(hour_text), int(minute_text)
    if not 0 <= hour <= 23:
        raise argparse.ArgumentTypeError("hour must be between 00 and 23")
    if not 0 <= minute <= 59:
        raise argparse.ArgumentTypeError("minute must be between 00 and 59")
    return hour, minute


def calculate_target_time(hour: int, minute: int, now: datetime) -> datetime:
    """Return the next occurrence of hour:minute, moving past times to tomorrow."""
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target


def format_remaining(seconds: float) -> str:
    """Format a non-negative duration as HH:MM:SS."""
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def wait_for_alarm(
    target: datetime,
    *,
    now_fn: Callable[[], datetime] = datetime.now,
    sleep_fn: Callable[[float], None] = time.sleep,
    stream: TextIO = sys.stdout,
) -> None:
    """Wait efficiently until target while displaying the remaining time."""
    while True:
        now = now_fn()
        remaining = (target - now).total_seconds()
        if remaining <= 0:
            break
        status = f"Waiting — current time {now:%H:%M:%S}; remaining {format_remaining(remaining)}"
        if stream.isatty():
            print(f"\r{status}", end="", flush=True, file=stream)
        else:
            print(status, flush=True, file=stream)
        sleep_fn(min(1.0, remaining))
    if stream.isatty():
        print(file=stream)


def notify(label: str | None, *, stream: TextIO = sys.stdout) -> None:
    """Print the alarm message and make a best-effort cross-platform sound."""
    message = "ALARM!"
    if label:
        message += f" {label}"
    print(message, file=stream, flush=True)

    if os.name == "nt":
        import winsound

        winsound.MessageBeep()
    else:
        print("\a", end="", file=stream, flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Set one simple command-line alarm.")
    parser.add_argument("alarm_time", nargs="?", type=parse_alarm_time, metavar="HH:MM", help="alarm time in 24-hour format")
    parser.add_argument("--label", help="optional message displayed when the alarm fires")
    parser.add_argument("--test-alarm", action="store_true", help="trigger the alarm immediately")
    return parser


def main(
    argv: list[str] | None = None,
    *,
    now_fn: Callable[[], datetime] = datetime.now,
    sleep_fn: Callable[[float], None] = time.sleep,
    notifier: Callable[[str | None], None] | None = None,
    stream: TextIO = sys.stdout,
) -> int:
    """Run the CLI and return a process status code."""
    args = build_parser().parse_args(argv)
    if args.test_alarm and args.alarm_time is not None:
        build_parser().error("HH:MM cannot be used with --test-alarm")
    if not args.test_alarm and args.alarm_time is None:
        build_parser().error("HH:MM is required unless --test-alarm is used")

    alarm_notifier = notifier or (lambda label: notify(label, stream=stream))
    if args.test_alarm:
        print("Test alarm: triggering immediately.", file=stream)
        alarm_notifier(args.label)
        return 0

    hour, minute = args.alarm_time
    target = calculate_target_time(hour, minute, now_fn())
    print(f"Alarm set for {target:%Y-%m-%d %H:%M}.", file=stream)
    try:
        wait_for_alarm(target, now_fn=now_fn, sleep_fn=sleep_fn, stream=stream)
    except KeyboardInterrupt:
        print("\nAlarm cancelled.", file=stream)
        return 130

    alarm_notifier(args.label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
