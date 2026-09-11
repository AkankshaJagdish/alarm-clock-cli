import io
import unittest
from datetime import datetime

import alarm_clock


class ParseAlarmTimeTests(unittest.TestCase):
    def test_valid_time(self):
        self.assertEqual(alarm_clock.parse_alarm_time("23:05"), (23, 5))

    def test_invalid_hour(self):
        with self.assertRaisesRegex(Exception, "hour"):
            alarm_clock.parse_alarm_time("24:00")

    def test_invalid_minute(self):
        with self.assertRaisesRegex(Exception, "minute"):
            alarm_clock.parse_alarm_time("12:60")

    def test_invalid_format(self):
        with self.assertRaisesRegex(Exception, "HH:MM"):
            alarm_clock.parse_alarm_time("9:00")


class TargetTimeTests(unittest.TestCase):
    def test_uses_today_for_future_time(self):
        now = datetime(2026, 9, 11, 9, 30, 15)
        self.assertEqual(alarm_clock.calculate_target_time(10, 0, now), datetime(2026, 9, 11, 10, 0))

    def test_moves_past_time_to_tomorrow(self):
        now = datetime(2026, 9, 11, 9, 30, 15)
        self.assertEqual(alarm_clock.calculate_target_time(9, 30, now), datetime(2026, 9, 12, 9, 30))


class CliTests(unittest.TestCase):
    def test_test_alarm_passes_label_to_notifier(self):
        received = []
        stream = io.StringIO()
        result = alarm_clock.main(["--test-alarm", "--label", "Take a break"], notifier=received.append, stream=stream)
        self.assertEqual(result, 0)
        self.assertEqual(received, ["Take a break"])
        self.assertIn("triggering immediately", stream.getvalue())

    def test_help_exits_successfully(self):
        with self.assertRaises(SystemExit) as raised:
            alarm_clock.main(["--help"])
        self.assertEqual(raised.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
