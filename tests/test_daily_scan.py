import datetime as dt
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('daily_scan', Path(__file__).parents[1] / 'scripts/daily_scan.py')
daily = importlib.util.module_from_spec(spec)
spec.loader.exec_module(daily)


class DailyScanTests(unittest.TestCase):
    def check(self, run, event='schedule', requested=False, time='2026-09-21T03:30:00+00:00'):
        return daily.decision({'run': run}, event, requested, dt.datetime.fromisoformat(time))[:2]

    def test_primary_and_backup_are_due_after_nine(self):
        self.assertEqual(self.check({'checkedOn': '2026-09-20'}), (True, True))
        self.assertEqual(self.check({}, time='2026-09-21T11:17:00+00:00'), (True, True))

    def test_delayed_event_before_nine_waits(self):
        self.assertEqual(self.check({}, time='2026-09-21T03:29:00+00:00'), (False, False))

    def test_same_day_backups_do_not_scan_or_publish(self):
        self.assertEqual(self.check({'scanDateIst': '2026-09-21'}), (False, False))
        self.assertEqual(self.check({'checkedOn': '2026-09-21'}), (False, False))

    def test_limited_scan_does_not_burn_credits_repeatedly(self):
        self.assertEqual(self.check({'scanDateIst': '2026-09-21', 'status': 'limited'}), (False, False))

    def test_ist_date_takes_precedence_over_utc_date(self):
        self.assertEqual(self.check({'scanDateIst': '2026-09-21', 'checkedOn': '2026-09-20'}), (False, False))

    def test_next_day_is_due(self):
        self.assertEqual(self.check({'scanDateIst': '2026-09-20'}), (True, True))

    def test_push_and_publish_only_dispatch_still_publish(self):
        self.assertEqual(self.check({}, event='push'), (False, True))
        self.assertEqual(self.check({}, event='workflow_dispatch'), (False, True))

    def test_manual_scan_also_respects_daily_limit(self):
        self.assertEqual(self.check({}, event='workflow_dispatch', requested=True), (True, True))
        self.assertEqual(self.check({'scanDateIst': '2026-09-21'}, event='workflow_dispatch', requested=True), (False, True))
