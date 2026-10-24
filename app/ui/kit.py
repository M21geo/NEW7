"""Small widget toolkit. EVERY direct Flet call lives here or in the screens' layout code,
so if a Flet release renames something there is one obvious place to fix it.

Written for the flet==0.28.3 API (ft.Colors / ft.Icons / show(page, )). NOT yet run against real Flet - see README.
"""
import os

import flet as ft

from .. import i18n, money
from . import theme as T


# ------------------------------------------------------------- primitives
_FLIP = {"arrow_forward": "arrow_back", "arrow_back": "arrow_forward", "chevron_left": "chevron_right",
         "chevron_right": "chevron_left", "keyboard_arrow_left": "keyboard_arrow_right", "keyboard_arrow_right": "keyboard_arrow_left"}


def icon_name(name: str):
    """'restaurant' -> ft.Icons.RESTAURANT (falls back to a generic icon). Direction arrows flip in English (left-to-right)."""
    name = name or "category"
    if not i18n.is_rtl():
        name = _FLIP.get(name, name)
    return getattr(ft.Icons, name.upper(), ft.Icons.CATEGORY)


def txt(value, size=14, bold=False, color=None, align=None, weight=None, expand=False, max_lines=None, **kw):
    color = T.INK if color is None else color
    if weight is None:
        weight = ft.FontWeight.W_800 if bold else ft.FontWeight.W_500
    value = i18n.tr(str(value))
    if value[:1] in "+−-–":  # keep the sign on the left of the number inside right-to-left text
        value = "\u200e" + value
    return ft.Text(value, size=size, weight=weight, color=color, text_align=align,
                   expand=expand, max_lines=max_lines, **kw)


def row(controls, spacing=8, align=None, v_align=None, wrap=False, expand=False, scroll=None, **kw):
    return ft.Row(controls=list(controls), spacing=spacing, wrap=wrap, expand=expand, scroll=scroll,
                  alignment=align or ft.MainAxisAlignment.START,
                  vertical_alignment=v_align or ft.CrossAxisAlignment.CENTER, **kw)


def col(controls, spacing=8, scroll=False, expand=False, align=None, h_align=None, **kw):
    return ft.Column(controls=list(controls), spacing=spacing, expand=expand,
                     scroll=ft.ScrollMode.AUTO if scroll else None,
                     alignment=align or ft.MainAxisAlignment.START,
                     horizontal_alignment=h_align or ft.CrossAxisAlignment.START, **kw)


def scroll_body(controls, spacing=12, side=20):
    """A full-width scrolling column whose content is inset by `side` px, so the scrollbar sits at the screen edge,
    away from the text (instead of touching it). Tagged so the app can remember/restore its scroll position."""
    inner = ft.Container(ft.Column(list(controls), spacing=spacing, horizontal_alignment=ft.CrossAxisAlignment.START),
                         padding=ft.Padding.symmetric(horizontal=side))
    return ft.Column([inner], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                     data="page_scroll")


def between(*controls, **kw):
    """Row with items pushed to both ends (RTL-aware: first item on the reading start)."""
    controls = list(controls)
    first = controls[0] if controls else None
    if len(controls) == 2 and isinstance(getattr(first, "controls", None), list) and not getattr(first, "expand", False):
        first.expand = True  # a text column on the start side takes the free width and wraps (never overflows/clips)
    return row(controls, align=ft.MainAxisAlignment.SPACE_BETWEEN, **kw)


def box(content=None, padding=14, bg=None, border="default", radius=18, on_click=None,
        width=None, height=None, expand=False, margin=None, align=None):
    bg = T.CARD if bg is None else bg
    border = T.LINE if border == "default" else border
    return ft.Container(content=content, padding=padding, bgcolor=bg, border_radius=radius,
                        border=ft.Border.all(1, border) if border else None, on_click=on_click,
                        ink=bool(on_click), width=width, height=height, expand=expand, margin=margin,
                        alignment=align)


def icon(name, size=22, color=None):
    return ft.Icon(icon=icon_name(name), size=size, color=T.INK if color is None else color)


def icon_btn(name, on_click, tooltip=None, color=None, size=22):
    return ft.IconButton(icon=icon_name(name), icon_color=T.INK if color is None else color, icon_size=size, on_click=on_click, tooltip=tooltip)


def icon_tile(name, color, size=44):
    """Rounded tile with a tinted background (category icons)."""
    if name and not str(name).isascii():          # a 3D-style emoji picked as the icon
        face = ft.Text(str(name), size=size * 0.5, text_align=ft.TextAlign.CENTER)
    else:
        face = icon(name, 22, color)
    return ft.Container(content=face, width=size, height=size, border_radius=14,
                        bgcolor=ft.Colors.with_opacity(0.15, color), alignment=ft.Alignment.CENTER)


def hero(content, padding=20, radius=24, colors=None, **kw):
    """Gradient header card (ocean blue)."""
    return ft.Container(content=content, padding=padding, border_radius=radius, **kw,
                        gradient=ft.LinearGradient(begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
                                                   colors=list(colors or T.HERO_GRAD)))


def hscroll(controls, spacing=8):
    return ft.Row(controls=list(controls), spacing=spacing, scroll=ft.ScrollMode.HIDDEN)


# ---------------------------------------------------------------- widgets
def chip(label, selected, on_click, color=T.PRIMARY, dashed=False):
    return ft.Container(
        content=txt(label, 14, True, "#FFFFFF" if selected else T.INK),
        padding=ft.Padding.symmetric(horizontal=14, vertical=11), border_radius=14, ink=True,
        bgcolor=color if selected else T.CARD, on_click=on_click,
        border=ft.Border.all(1, color if selected else T.LINE))


def _line_of(est, width, index):
    """Which line (0-based) a chip of the wrapped row lands on, from estimated chip widths."""
    line, used = 0, 0
    for i, w in enumerate(est):
        if used and used + w > width:
            line, used = line + 1, 0
        used += w + 8
        if i == index:
            return line
    return line


def chips_box(chips, labels, width, expanded, on_toggle, lines=2, selected=None):
    """A wrapped row of chips folded to `lines` lines with a small arrow beside it that opens/closes the rest.
    expanded=None = automatic: folded, unless the selected chip would be hidden. Short rows show no arrow."""
    est = [len(str(l)) * 8.5 + 36 for l in labels]
    avail = max(120, width - 46)
    total_lines = _line_of(est, avail, len(est) - 1) + 1 if est else 1
    row = ft.Row(list(chips), wrap=True, spacing=8, run_spacing=8)
    if total_lines <= lines:
        return row
    if expanded is None:
        expanded = selected is not None and _line_of(est, avail, selected) >= lines
    box = ft.Container(row, height=None if expanded else lines * 56 - 4, padding=ft.Padding.symmetric(vertical=2),
                       clip_behavior=ft.ClipBehavior.HARD_EDGE)
    arrow = ft.Container(icon("expand_less" if expanded else "expand_more", 22, T.MUTED), width=34, height=34, border_radius=17,
                         bgcolor=T.SOFT, ink=True, on_click=lambda e: on_toggle(not expanded), alignment=ft.Alignment.CENTER)
    return ft.Row([ft.Container(box, expand=True), arrow], vertical_alignment=ft.CrossAxisAlignment.START, spacing=6)


def segmented(options, selected, on_select):
    """options: [(key, label)]; a tray of equal-width buttons (period / type switches)."""
    def btn(key, label):
        on = key == selected
        return ft.Container(
            content=txt(label, 14, True, T.INK if on else T.MUTED, align=ft.TextAlign.CENTER),
            expand=True, padding=ft.Padding.symmetric(vertical=11), border_radius=12, ink=True,
            bgcolor=T.CARD if on else None, on_click=lambda e, k=key: on_select(k),
            shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.with_opacity(0.12, T.INK), offset=ft.Offset(0, 1)) if on else None)
    return ft.Container(content=row([btn(k, l) for k, l in options], spacing=4), padding=4,
                        bgcolor=T.LINE, border_radius=16)


def badge(text, tone="neutral"):
    fg, bg = T.TONE.get(tone, T.TONE["neutral"])
    return ft.Container(content=txt(text, 11, True, fg), bgcolor=bg, border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=7, vertical=2))


def tag(text, color, icon_name=None):
    """Small coloured pill (soft tinted background, strong text) - used for wallet and person names."""
    items = ([icon(icon_name, 12, color)] if icon_name else []) + [txt(text, 11, True, color)]
    return ft.Container(content=row(items, spacing=4, tight=True), bgcolor=ft.Colors.with_opacity(0.14, color), border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=7, vertical=2))


def wallet_tag(name):
    return tag(name, T.vivid(name), "account_balance_wallet")      # same colour as that wallet's card on Home


def person_tag(name):
    return tag(name, T.vivid("p:" + name), "person")


def tags_row(wallet_name, person_name=None):
    return row([wallet_tag(wallet_name)] + ([person_tag(person_name)] if person_name else []), spacing=6, wrap=True)


def section(title, action=None, on_action=None):
    items = [txt(title, 17, True)]
    if action:
        items.append(ft.TextButton(i18n.tr(action), on_click=on_action))
    return between(*items)


def progress(fraction, color, width, height=8, track=None):
    track = T.SOFT if track is None else track
    """Horizontal bar made of two containers (no dependency on ProgressBar styling)."""
    fraction = max(0.0, min(1.0, fraction))
    return ft.Container(
        content=ft.Container(width=max(0, width * fraction), height=height, bgcolor=color, border_radius=height / 2),
        width=width, height=height, bgcolor=track, border_radius=height / 2, alignment=ft.Alignment.CENTER_LEFT)


def field(label, value="", on_change=None, number=False, multiline=False, hint=None, width=None, expand=False,
          thousands=False, password=False):
    """Text field. thousands=True formats digits live as 10,000,000 (and accepts Arabic digits)."""
    handler = on_change
    if thousands:
        value = money.format_input(value)

        def handler(e):
            new = money.format_input(e.control.value)
            if new != e.control.value:
                e.control.value = new
                e.control.update()
            if on_change:
                on_change(e)

    return ft.TextField(
        label=i18n.tr(label), hint_text=i18n.tr(hint) if hint else hint, value=value, on_change=handler, width=width, expand=expand,
        keyboard_type=ft.KeyboardType.NUMBER if (number or thousands) else ft.KeyboardType.TEXT,
        password=password, can_reveal_password=password,
        multiline=multiline, min_lines=2 if multiline else 1, max_lines=4 if multiline else 1,
        border_radius=14, border_color=T.LINE, focused_border_color=T.PRIMARY, bgcolor=T.CARD, filled=True,
        text_size=15, content_padding=ft.Padding.symmetric(horizontal=14, vertical=12))


def columns_chart(points, width, height=110, label_every=1, gap=3):
    """Vertical bar chart from containers. points: [{'label','top','bars':[(fraction,color),...]}]."""
    n = max(1, len(points))
    nb = max(1, max((len(p["bars"]) for p in points), default=1))
    slot = width / n
    bw = max(3, min(26, (slot - gap * 2) / nb - 1))
    cols = []
    for i, p in enumerate(points):
        bars = ft.Row([ft.Container(width=bw, height=max(2, height * f) if f > 0 else 2, bgcolor=c if f > 0 else T.SOFT,
                                    border_radius=min(5, bw / 2)) for f, c in p["bars"]],
                      spacing=1, vertical_alignment=ft.CrossAxisAlignment.END, alignment=ft.MainAxisAlignment.CENTER,
                      height=height)
        lab = p["label"] if i % label_every == 0 else ""
        cols.append(ft.Container(kit_col([txt(p.get("top", ""), 10, color=T.MUTED), bars, txt(lab, 10, color=T.MUTED)],
                                         spacing=3, h_align=ft.CrossAxisAlignment.CENTER,
                                         align=ft.MainAxisAlignment.END), width=slot, alignment=ft.Alignment.BOTTOM_CENTER,
                                  on_click=p.get("on_click"), ink=bool(p.get("on_click"))))
    return ft.Row(cols, spacing=0, vertical_alignment=ft.CrossAxisAlignment.END, width=width)


def kit_col(*a, **k):
    return col(*a, **k)


def big_button(label, on_click, enabled=True, bg=T.PRIMARY, fg="#FFFFFF", outline=False):
    return ft.Container(
        content=txt(label, 16, True, T.PRIMARY if outline else fg, align=ft.TextAlign.CENTER),
        padding=ft.Padding.symmetric(vertical=15), border_radius=18, ink=enabled,
        bgcolor=None if outline else (bg if enabled else "#9DB0AA"),
        border=ft.Border.all(1.5, T.PRIMARY) if outline else None,
        on_click=on_click if enabled else None, alignment=ft.Alignment.CENTER)


def donut(slices, size=170, hole=52, center=None):
    """Donut chart of [{'value','color','title'?}] with an optional centre label (any control).
    The centre is laid over the ring with explicit full-size positioning, so it is always in the middle."""
    total = sum(s["value"] for s in slices) or 1
    try:
        sections = [ft.PieChartSection(
            s["value"], color=s["color"], radius=size / 2 - hole - 2, title=s.get("title", ""),
            title_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_800, color="#FFFFFF"))
            for s in slices if s["value"] > 0]
        chart = ft.PieChart(sections=sections, sections_space=2, center_space_radius=hole, width=size, height=size)
    except Exception:  # pragma: no cover - depends on the installed flet version
        return ft.Row([ft.Container(expand=max(1, round(s["value"] / total * 100)), height=18, bgcolor=s["color"])
                       for s in slices if s["value"] > 0], spacing=2, width=size)
    if center is None:
        return chart
    return ft.Stack([chart, ft.Container(center, left=0, top=0, right=0, bottom=0, alignment=ft.Alignment.CENTER)],
                    width=size, height=size)


# ------------------------------------------------------- page-level helpers
OPEN = []          # dialogs / sheets we opened (so the system back button can close the top one first)


def show(page, control):
    """Open a dialog / bottom sheet / snackbar / picker (translated to the current language first)."""
    try:
        i18n.translate_tree(control)
    except Exception:
        pass
    OPEN[:] = [c for c in OPEN if getattr(c, "open", False)]
    OPEN.append(control)
    prev = getattr(control, "on_dismiss", None)

    def dismissed(e=None):
        # closed by the phone's back button / a tap outside: forget it, so the next back press is not swallowed
        # and never closes the sheet underneath by mistake
        if control in OPEN:
            OPEN.remove(control)
        try:
            control.open = False
        except Exception:
            pass
        if prev:
            return prev(e) if e is not None else prev()

    try:
        control.on_dismiss = dismissed
    except Exception:
        pass
    page.show_dialog(control)


def hide(page, control):
    """Close one specific dialog / sheet (it need not be the top one)."""
    if control in OPEN:
        OPEN.remove(control)
    try:
        control.open = False
        control.update()
    except Exception:
        try:
            page.pop_dialog()
        except Exception:
            pass


def toast(page, message):
    show(page, ft.SnackBar(content=ft.Text(i18n.tr(str(message)))))


def confirm(page, title, message, on_yes, yes_label="حذف"):
    dlg = ft.AlertDialog(modal=True, title=ft.Text(title), content=ft.Text(message))

    def yes(e):
        hide(page, dlg)
        on_yes()

    dlg.actions = [ft.TextButton("إلغاء", on_click=lambda e: hide(page, dlg)),
                   ft.TextButton(yes_label, on_click=yes, style=ft.ButtonStyle(color=T.EXPENSE))]
    show(page, dlg)
    return dlg


# ----------------------------------------------------------------- file dialogs
def _picker(ui):
    """One FilePicker service per app (kept referenced: Flet drops services nobody holds)."""
    fp = getattr(ui, "_file_picker", None)
    if fp is None:
        fp = ft.FilePicker()
        ui._file_picker = fp
    return fp


def pick_file(ui, on_path, extensions=None, title="اختر ملف"):
    """Open the system file picker; on_path(path) is called with the chosen file path.
    Any exception inside on_path is shown on screen instead of vanishing silently."""
    fp = _picker(ui)

    async def go():
        files = await fp.pick_files(
            dialog_title=i18n.tr(title),
            file_type=ft.FilePickerFileType.CUSTOM if extensions else ft.FilePickerFileType.ANY,
            allowed_extensions=list(extensions) if extensions else None, allow_multiple=False)
        if not files:
            return
        path = files[0].path
        if not path:
            ui.toast("هذا الجهاز ما أعطانا مسار الملف. انسخ الملف لمجلد عادي وجرب مرة ثانية")
            return
        try:
            on_path(path)
        except Exception as ex:  # pragma: no cover - UI safety net
            import traceback
            ui.toast(f"خطأ بقراءة الملف: {type(ex).__name__}: {ex}")
            print(traceback.format_exc())

    ui.page.run_task(go)


def img_src(b64):
    """Stored pictures are base64 text; Flet 1.0 Image takes the raw bytes."""
    import base64
    return base64.b64decode(b64)


def view_image(ui, b64, save_name="picture"):
    """Full-screen picture viewer: pinch to zoom, drag to move, save a copy out of the app."""
    from .. import imaging
    w, h = ui.w, ui.h
    pic = ft.Image(src=img_src(b64), fit=ft.BoxFit.CONTAIN, width=w, height=h * 0.8)
    try:
        body = ft.InteractiveViewer(content=pic, min_scale=1, max_scale=6, width=w, height=h * 0.8)
    except Exception:
        body = pic
    save_btn = ft.Container(
        icon("download", 20, "#FFFFFF"), left=10, top=10, padding=8, border_radius=20, ink=True,
        bgcolor=ft.Colors.with_opacity(0.55, "#000000"), tooltip=i18n.tr("حفظ نسخة من الصورة بالتنزيلات"),
        on_click=lambda e: save_bytes(ui, f"{save_name}.{imaging.guess_ext(b64)}", imaging.to_bytes(b64),
                                      [imaging.guess_ext(b64)], "احفظ الصورة", "انحفظت نسخة من الصورة"))
    dlg = ft.AlertDialog(content=ft.Stack([body, save_btn], width=w, height=h * 0.8), content_padding=0,
                         inset_padding=ft.Padding.all(6), bgcolor="#000000",
                         actions=[ft.TextButton(i18n.tr("إغلاق"), on_click=lambda e: hide(ui.page, dlg))])
    show(ui.page, dlg)


def pick_picture(ui, on_b64):
    """Choose a picture from the phone; on_b64(base64 text of the small stored copy)."""
    from .. import imaging

    def got(path):
        try:
            on_b64(imaging.load(path))
        except Exception as ex:
            ui.toast(str(ex))

    pick_file(ui, got, imaging.EXTENSIONS, "اختر صورة")


def save_bytes(ui, name, data, extensions=None, title="احفظ الملف", ok_msg="تم الحفظ"):
    """Save `data` (bytes) as a file the user can find. Every write is verified by size (an empty file is never
    reported as saved).
    - Android: a save dialog may give a virtual path Python cannot write to (0-byte file), so the file goes
      straight into Download/Masarif; if that is not allowed, the user is told how to allow it and may pick a folder.
    - Desktop: the normal save dialog."""
    from .. import export

    def done(path):
        ui.toast(f"{i18n.tr(ok_msg)}\n{path}")

    def fail(err):
        ui.toast(f"{i18n.tr('تعذر الحفظ')}: {err}")

    def write_to(path):
        try:
            done(export.write_verified(path, data))
        except Exception as ex:
            fail(f"{type(ex).__name__}: {ex}")

    if not export.is_android():
        async def desktop():
            fp = _picker(ui)
            chosen = await fp.save_file(
                dialog_title=i18n.tr(title), file_name=name,
                file_type=ft.FilePickerFileType.CUSTOM if extensions else ft.FilePickerFileType.ANY,
                allowed_extensions=list(extensions) if extensions else None, src_bytes=data)
            if chosen:
                path = chosen
                if extensions and not path.lower().endswith("." + extensions[0]):
                    path += "." + extensions[0]
                write_to(path)

        ui.page.run_task(desktop)
        return

    path, err = export.save_public(name, data)
    if path:
        done(path)
        return

    def pick_folder(e):
        hide(ui.page, dlg)

        async def go():
            folder = await _picker(ui).get_directory_path(dialog_title=i18n.tr("اختر مجلد الحفظ"))
            if folder:
                write_to(os.path.join(folder, name))

        ui.page.run_task(go)

    dlg = ft.AlertDialog(
        title=ft.Text(i18n.tr("ما كدرت أحفظ بمجلد التنزيلات")),
        content=ft.Column([
            ft.Text(i18n.tr("فعّل مرة وحدة: الإعدادات ← التطبيقات ← مصاريفي ← الأذونات ← الملفات والوسائط ← السماح بإدارة كل الملفات. بعدها جرب مرة ثانية. أو اختر مجلد بنفسك:")),
            ft.Text(str(err), size=11, selectable=True)], tight=True, spacing=8),
        actions=[ft.TextButton(i18n.tr("إلغاء"), on_click=lambda e: hide(ui.page, dlg)),
                 ft.TextButton(i18n.tr("اختيار مجلد"), on_click=pick_folder)])
    show(ui.page, dlg)


def dropdown(label_text, options, value, on_change):
    """options: [(key, text)]."""
    return ft.Dropdown(label=i18n.tr(label_text), value=value, on_select=on_change, border_radius=14, border_color=T.LINE,
                       bgcolor=T.CARD, text_size=14,
                       options=[ft.DropdownOption(key=k, text=i18n.tr(t)) for k, t in options])


# ------------------------------------------------------------------- calendar
def pick_date(ui, initial, on_pick):
    """Open the calendar; on_pick('YYYY-MM-DD') is called with the chosen day."""
    from datetime import datetime, timedelta
    try:
        init = datetime.strptime(initial or "", "%Y-%m-%d")
    except ValueError:
        init = datetime.now()

    def changed(e):
        d = e.control.value
        if d is None:
            return
        if getattr(d, "hour", 0) >= 12:  # some platforms return local midnight as the previous evening in UTC
            d = d + timedelta(days=1)
        on_pick(d.strftime("%Y-%m-%d"))

    dp = ft.DatePicker(first_date=datetime(2000, 1, 1), last_date=datetime(2100, 12, 31), value=init, on_change=changed)
    show(ui.page, dp)


class DateInput:
    """A field-looking tile that opens the calendar. Read .value ('' when empty) and put .control in a layout."""

    def __init__(self, ui, label_text, value="", clearable=False, on_change=None):
        self.ui, self.label, self.value, self.on_change = ui, label_text, value or "", on_change
        self.text = ft.Text(self.value or "اختر التاريخ", size=15, weight=ft.FontWeight.W_500,
                            color=T.INK if self.value else T.FAINT)
        right = [icon("calendar_month", 22, T.PRIMARY)]
        if clearable:
            right.insert(0, icon_btn("close", self._clear, color=T.MUTED, size=18))
        self.control = ft.Container(
            content=between(col([txt(label_text, 12, color=T.MUTED), self.text], spacing=1), row(right, spacing=0)),
            padding=ft.Padding.symmetric(horizontal=14, vertical=9), border_radius=14, bgcolor=T.CARD, ink=True,
            border=ft.Border.all(1, T.LINE), on_click=self._open)

    def _open(self, e):
        pick_date(self.ui, self.value, self.set)

    def _clear(self, e):
        self.set("")

    def set(self, iso):
        self.value = iso
        self.text.value = iso or "اختر التاريخ"
        self.text.color = T.INK if iso else T.FAINT
        if self.on_change:
            self.on_change(iso)
        self.ui.page.update()


def confirm_typed(page, title, message, word, on_yes, yes_label="مسح"):
    """Destructive confirmation: the action button only works after typing `word`."""
    box = ft.TextField(hint_text=f"اكتب «{word}» للتأكيد", border_radius=12, text_size=14)
    dlg = ft.AlertDialog(modal=True, title=ft.Text(title), content=ft.Column([ft.Text(message), box], tight=True, spacing=12))

    def yes(e):
        if box.value.strip() != word:
            box.error_text = i18n.tr(f"اكتب {word} بالضبط")
            page.update()
            return
        hide(page, dlg)
        on_yes()

    dlg.actions = [ft.TextButton("إلغاء", on_click=lambda e: hide(page, dlg)),
                   ft.TextButton(yes_label, on_click=yes, style=ft.ButtonStyle(color=T.EXPENSE))]
    show(page, dlg)


def pick_time(ui, initial, on_pick):
    """Clock picker; on_pick('HH:MM')."""
    from datetime import time
    try:
        h, m = (int(x) for x in (initial or "21:00").split(":"))
    except ValueError:
        h, m = 21, 0

    def changed(e):
        v = e.control.value
        if v is not None:
            on_pick(f"{v.hour:02d}:{v.minute:02d}")

    show(ui.page, ft.TimePicker(value=time(h, m), on_change=changed))
