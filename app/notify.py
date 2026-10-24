"""Out-of-app reminders (real phone notifications, shown even when the app is closed).

Uses the `flet-notifications` package (Flutter local notifications + the OS alarm manager). The app plans the next
DAYS days as separate one-shot notifications, each with its own funny wording (and any debt that falls due that
day), and re-plans every time the app opens or the reminder settings change. The phone keeps the alarms, so they
fire with the app closed and after a reboot.

Every call is guarded: if the package is missing (desktop run, tests) nothing happens and the app keeps working.
"""
import inspect
from datetime import datetime, timedelta

from . import reminder

DAYS = 14                    # how many days ahead are planned
BASE_ID = 4100               # notification ids BASE_ID .. BASE_ID+DAYS-1
TIME_ZONE = "Asia/Baghdad"   # the wall-clock time the user picked is in this zone

_state = {"obj": None, "tried": False}


def plan(repo, now=None, days=DAYS) -> list:
    """[(id, datetime, title, body)] for the coming days. Pure logic (testable without Flet)."""
    now = now or datetime.now()
    cfg = reminder.settings(repo)
    if not cfg["enabled"]:
        return []
    hh, mm = (int(x) for x in cfg["time"].split(":"))
    out = []
    for i in range(days + 1):
        day = (now + timedelta(days=i)).date()
        when = datetime(day.year, day.month, day.day, hh, mm)
        if when <= now:
            continue
        lines = reminder.lines(repo, day.isoformat())
        if not lines:
            continue
        out.append((BASE_ID + len(out), when, reminder.title(repo), "\n".join(lines)))
        if len(out) >= days:
            break
    return out


def _load():
    if _state["tried"]:
        return _state["obj"]
    _state["tried"] = True
    try:
        from flet_notifications import LocalNotifications  # type: ignore
        _state["obj"] = LocalNotifications()
    except Exception:
        _state["obj"] = None
    return _state["obj"]


async def _maybe(v):
    return await v if inspect.isawaitable(v) else v


async def sync(repo, ask_permission=True) -> str:
    """Re-plan the phone's reminders from the current settings. Returns 'off', 'ok', 'denied' or 'unavailable'."""
    obj = _load()
    if obj is None:
        return "unavailable"
    try:
        items = plan(repo)
        try:
            await _maybe(obj.cancel_all())
        except Exception:
            pass
        if not items:
            return "off"
        if ask_permission and not await _maybe(obj.request_permissions()):
            return "denied"
        import flet_notifications as fn  # type: ignore
        modes = [getattr(fn, "AndroidScheduleMode", None)]
        for nid, when, title, body in items:
            try:
                await _maybe(obj.schedule(id=nid, when=when, title=title, body=body, time_zone=TIME_ZONE))
            except Exception:
                inexact = None
                for name in ("INEXACT_ALLOW_WHILE_IDLE", "INEXACT"):
                    inexact = getattr(modes[0], name, None) if modes[0] else None
                    if inexact is not None:
                        break
                if inexact is None:
                    raise
                await _maybe(obj.schedule(id=nid, when=when, title=title, body=body, time_zone=TIME_ZONE,
                                          schedule_mode=inexact))
        return "ok"
    except Exception:
        return "unavailable"


def resync(ui) -> None:
    """Called after the reminder settings changed (and at start-up)."""
    async def go():
        status = await sync(ui.repo)
        if status == "denied":
            ui.toast("ما انسمح بالإشعارات. فعّلها من إعدادات الهاتف ← التطبيقات ← مصاريفي ← الإشعارات")

    try:
        ui.page.run_task(go)
    except Exception:
        pass
