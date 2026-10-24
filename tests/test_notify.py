import asyncio
import sys
import unittest
from datetime import datetime
from types import ModuleType

from app import notify
from app.db import connect
from app.repo import Repo
from app.seed import ensure_defaults


def make():
    r = Repo(connect(":memory:"))
    ensure_defaults(r)
    return r


class Plan(unittest.TestCase):
    def test_off_means_nothing_planned(self):
        self.assertEqual(notify.plan(make(), datetime(2026, 10, 24, 9, 0)), [])

    def test_plans_future_days_only_with_unique_ids(self):
        r = make()
        r.set_setting("reminder_enabled", "1")
        r.set_setting("reminder_time", "21:30")
        items = notify.plan(r, datetime(2026, 10, 24, 22, 0), days=5)      # today's time already passed
        self.assertEqual(len(items), 5)
        self.assertEqual(items[0][1], datetime(2026, 10, 25, 21, 30))
        self.assertEqual(len({i[0] for i in items}), 5)
        self.assertTrue(all(i[2] and i[3] for i in items))
        items2 = notify.plan(r, datetime(2026, 10, 24, 9, 0), days=3)      # today still ahead
        self.assertEqual(items2[0][1], datetime(2026, 10, 24, 21, 30))

    def test_due_debt_shows_up_in_that_days_text(self):
        from app.debts import Debts
        r = make()
        r.set_setting("reminder_enabled", "1")
        pid = r.add_person("أحمد")
        Debts(r).add_debt("on", pid, 50000, "IQD", "2026-10-26", "x")
        items = notify.plan(r, datetime(2026, 10, 24, 9, 0), days=4)
        by_day = {i[1].date().isoformat(): i[3] for i in items}
        self.assertIn("أحمد", by_day["2026-10-25"] + by_day["2026-10-26"])


class FakeNotifications:
    def __init__(self):
        self.calls = []

    async def request_permissions(self):
        return True

    async def cancel_all(self):
        self.calls.append("cancel_all")

    async def schedule(self, **kw):
        self.calls.append(("schedule", kw["id"], kw["when"], kw["time_zone"]))


class Sync(unittest.TestCase):
    def setUp(self):
        mod = ModuleType("flet_notifications")
        mod.LocalNotifications = FakeNotifications
        sys.modules["flet_notifications"] = mod
        notify._state.update(obj=None, tried=False)

    def tearDown(self):
        sys.modules.pop("flet_notifications", None)
        notify._state.update(obj=None, tried=False)

    def test_sync_schedules_and_clears(self):
        r = make()
        r.set_setting("reminder_enabled", "1")
        self.assertEqual(asyncio.run(notify.sync(r)), "ok")
        calls = notify._state["obj"].calls
        self.assertEqual(calls[0], "cancel_all")
        self.assertGreater(len([c for c in calls if c != "cancel_all"]), 5)
        self.assertEqual(calls[1][3], "Asia/Baghdad")
        r.set_setting("reminder_enabled", "0")
        self.assertEqual(asyncio.run(notify.sync(r)), "off")

    def test_missing_package_is_harmless(self):
        sys.modules.pop("flet_notifications", None)
        sys.modules["flet_notifications"] = None          # import raises ImportError
        notify._state.update(obj=None, tried=False)
        self.assertEqual(asyncio.run(notify.sync(make())), "unavailable")


if __name__ == "__main__":
    unittest.main()
