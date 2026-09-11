# Alarm Clock CLI

A small Python 3 command-line alarm clock. It supports one active alarm per
process, accepts a 24-hour `HH:MM` time, and can display a label when it fires.

## Setup

No installation or third-party packages are required. Use Python 3:

```bash
python alarm_clock.py 23:00
python alarm_clock.py 23:00 --label "Take a break"
python alarm_clock.py --test-alarm
```

`--test-alarm` triggers the notification immediately. If an entered time has
already passed today, the alarm is scheduled for tomorrow. Press `Ctrl+C` to
cancel a waiting alarm cleanly.

## Design

The implementation separates time parsing, target-time calculation, waiting,
and notification into small functions. Target calculation takes a supplied
`datetime`, which keeps it easy to test without waiting. The wait loop sleeps
for at most one second at a time rather than busy-waiting, and shows the current
and remaining time. On Windows it uses the standard-library `winsound` module;
elsewhere it emits the terminal bell character.

## Testing

Run the standard-library test suite with:

```bash
python -m unittest -v
```

## Limitations

This is intentionally a single-process, single-alarm CLI. It does not persist
alarms, run in the background, integrate with desktop notifications, or provide
recurring alarms.
