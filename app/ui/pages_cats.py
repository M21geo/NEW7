"""More > Categories manager: add, edit, reorder, move up/down, delete (with reassignment)."""
import flet as ft

from .. import i18n
from . import icon_set, kit, theme as T
from .forms import FormSheet, choices, label
from .rows import empty_state, page_frame, small_btn

COLORS = ["#FF6B4A", "#06B6D4", "#FFB703", "#8E6CEF", "#2EC27E", "#FF5C8A", "#3A86FF", "#FB8500", "#14B8A6", "#EF476F",
          "#84CC16", "#A855F7", "#0EA5E9", "#F43F5E", "#64748B", "#92400E"]


def build_cats(ui):
    """Categories manager: one card per main category (tap the arrow for its sub-categories), a menu per item,
    and a drag-and-drop sheet for ordering."""
    repo, kind = ui.repo, ui.cat_kind
    if not hasattr(ui, "cat_open"):
        ui.cat_open = set()

    def set_kind(k):
        ui.cat_kind = k
        ui.refresh()

    def delete(c):
        used = repo.category_usage(c["id"])
        if not used:
            kit.confirm(ui.page, "حذف الفئة", f"حذف «{c['name']}» وفئاتها الفرعية؟", lambda: (repo.delete_category(c["id"]), ui.refresh()))
            return
        reassign_form(ui, c, used)

    def menu(c, sub=False):
        items = [ft.PopupMenuItem(content=i18n.tr("تعديل"), icon=ft.Icons.EDIT_OUTLINED,
                                  on_click=lambda e, c=c: cat_form(ui, c, kind, c["parent_id"]))]
        if not sub:
            items.append(ft.PopupMenuItem(content=i18n.tr("فئة فرعية"), icon=ft.Icons.ADD,
                                          on_click=lambda e, c=c: cat_form(ui, None, kind, c["id"])))
            if len(c["children"]) > 1:
                items.append(ft.PopupMenuItem(content=i18n.tr("ترتيب الفرعيات"), icon=ft.Icons.SWAP_VERT,
                                              on_click=lambda e, c=c: reorder_sheet(ui, kind, c["id"], c["name"])))
        items.append(ft.PopupMenuItem(content=i18n.tr("حذف"), icon=ft.Icons.DELETE_OUTLINE,
                                      on_click=lambda e, c=c: delete(c)))
        return ft.PopupMenuButton(items=items, icon=ft.Icons.MORE_VERT, icon_color=T.MUTED)

    holders = {}

    def toggle(cid):
        ui.cat_open.symmetric_difference_update({cid})
        holders[cid][0].content = holders[cid][1]()
        i18n.translate_tree(holders[cid][0].content)
        ui.page.update()

    def sub_row(c):
        used = repo.category_usage(c["id"])
        return ft.Container(kit.row([kit.icon_tile(c["icon"], c["color"], 32),
                                     kit.col([kit.txt(c["name"], 14, True, max_lines=2),
                                              kit.txt(f"{used} معاملة", 11, color=T.MUTED)], spacing=0, expand=True),
                                     menu(c, True)], spacing=10),
                            padding=ft.Padding.only(left=4, right=4), border_radius=12, bgcolor=T.SOFT)

    def card(c):
        used = repo.category_usage(c["id"])
        n = len(c["children"])
        opened = c["id"] in ui.cat_open and n > 0
        sub = kit.row([kit.txt(f"{used} معاملة", 12, color=T.MUTED)] +
                      ([kit.txt("·", 12, color=T.MUTED), kit.txt(f"{n} فرعية", 12, color=T.MUTED)] if n else []), spacing=5)
        head = kit.row([kit.icon_tile(c["icon"], c["color"], 44),
                        kit.col([kit.txt(c["name"], 15, True, max_lines=2), sub], spacing=1, expand=True),
                        *([ft.Container(kit.icon("expand_less" if opened else "expand_more", 22, T.PRIMARY), width=36, height=36,
                                        border_radius=18, bgcolor=T.PRIMARY_SOFT, ink=True, alignment=ft.Alignment.CENTER,
                                        on_click=lambda e, i=c["id"]: toggle(i))] if n else []),
                        menu(c)], spacing=10)
        body = [head]
        if opened:
            body += [sub_row(ch) for ch in c["children"]]
        if opened or not n:
            body.append(ft.Row([kit.chip("+ فئة فرعية", False, lambda e, i=c["id"]: cat_form(ui, None, kind, i), color=T.MUTED)]))
        return kit.col(body, spacing=8)

    tree = repo.category_tree(kind)
    cards = []
    for top in tree:
        holder = ft.Container(padding=ft.Padding.all(12), bgcolor=T.CARD, border_radius=18, border=ft.Border.all(1, T.LINE))
        holder.content = card(top)
        holders[top["id"]] = (holder, lambda top=top: card(top))
        cards.append(holder)
    seg = kit.segmented([("expense", "مصاريف"), ("income", "دخل")], kind, set_kind)
    actions = kit.row([ft.Container(kit.big_button("+ فئة رئيسية", lambda e: cat_form(ui, None, kind, None)), expand=True),
                       *([ft.Container(kit.big_button("ترتيب", lambda e: reorder_sheet(ui, kind, None, ""), outline=True), expand=True)]
                         if len(tree) > 1 else [])], spacing=10)
    return page_frame(ui, "الفئات", [seg, actions,
                                     kit.txt("اضغط السهم لعرض الفرعيات. الترتيب هنا هو نفس ترتيب الفئات عند إضافة المعاملات.", 12, color=T.MUTED),
                                     *(cards or [empty_state("ما في فئات")])])


def reorder_sheet(ui, kind, parent_id, parent_name):
    """Drag-and-drop ordering (long-press a row and drag). The order is saved as you drop."""
    repo = ui.repo
    tree = repo.category_tree(kind)
    if parent_id is None:
        items = tree
    else:
        items = next((t["children"] for t in tree if t["id"] == parent_id), [])
    ids = [c["id"] for c in items]
    sheet = {}

    def on_reorder(e):
        old, new = int(e.old_index), int(e.new_index)
        if 0 <= old < len(ids) and 0 <= new <= len(ids):
            ids.insert(min(new, len(ids) - 1), ids.pop(old))
            repo.reorder_categories(ids)

    def row(c):
        return ft.Container(kit.row([kit.icon("drag_indicator", 22, T.FAINT), kit.icon_tile(c["icon"], c["color"], 36),
                                     kit.txt(c["name"], 15, True, expand=True, max_lines=1)], spacing=10),
                            padding=ft.Padding.symmetric(horizontal=12, vertical=8), bgcolor=T.CARD, border_radius=14,
                            border=ft.Border.all(1, T.LINE), margin=ft.Margin.only(bottom=6), key=str(c["id"]))

    def done(e):
        kit.hide(ui.page, sheet["s"])
        ui.refresh()

    lst = ft.ReorderableListView(controls=[row(c) for c in items], on_reorder=on_reorder, expand=True)
    title = "ترتيب الفئات" if parent_id is None else f"ترتيب فرعيات «{parent_name}»"
    sheet["s"] = ui.open_sheet(kit.col([
        kit.txt(title, 20, True),
        kit.txt("اضغط مطولاً على أي صف واسحبه لمكانه الجديد.", 12, color=T.MUTED),
        lst, kit.big_button("تم", done)], spacing=10, expand=True))


def cat_form(ui, c, kind, parent_id):
    repo = ui.repo
    cur_icon = c["icon"] if c else "category"
    s = {"color": c["color"] if c else COLORS[0], "icon": cur_icon, "tab": "emoji" if not cur_icon.isascii() else "plain",
         "group": None}
    name = kit.field("اسم الفئة", c["name"] if c else "")

    def pick(key, v):
        s[key] = v
        form.render()

    def group_of(icon):
        pool = icon_set.EMOJI if not icon.isascii() else icon_set.PLAIN
        return next((g for g in icon_set.GROUPS if icon in pool[g]), icon_set.GROUPS[0])

    def controls():
        color_row = ft.Row([ft.Container(width=34, height=34, bgcolor=col, border_radius=17, ink=True,
                                         border=ft.Border.all(3, T.INK) if col == s["color"] else None,
                                         on_click=lambda e, col=col: pick("color", col)) for col in COLORS], wrap=True, spacing=8, run_spacing=8)
        group = s["group"] or group_of(s["icon"])
        pool = icon_set.EMOJI if s["tab"] == "emoji" else icon_set.PLAIN
        def set_tab(v):
            s["group"] = None
            pick("tab", v)

        tabs = kit.segmented([("plain", "عادية"), ("emoji", "مجسمة")], s["tab"], set_tab)
        group_row = ft.Row([kit.chip(g, g == group, lambda e, g=g: pick("group", g), color=T.PRIMARY) for g in icon_set.GROUPS],
                           scroll=ft.ScrollMode.HIDDEN, spacing=8)

        def cell(i):
            on = i == s["icon"]
            face = ft.Text(i, size=26) if s["tab"] == "emoji" else kit.icon(i, 24, s["color"] if on else T.MUTED)
            return ft.Container(face, width=48, height=48, border_radius=14, ink=True, alignment=ft.Alignment.CENTER,
                                bgcolor=ft.Colors.with_opacity(0.18, s["color"]) if on else T.SOFT,
                                border=ft.Border.all(2, s["color"]) if on else None,
                                on_click=lambda e, i=i: pick("icon", i))

        icon_grid = ft.Row([cell(i) for i in pool[group]], wrap=True, spacing=8, run_spacing=8)
        preview = kit.row([kit.icon_tile(s["icon"], s["color"], 52), kit.txt(name.value or i18n.tr("معاينة"), 16, True)], spacing=12)
        return [preview, name, label("اللون"), color_row, label("الأيقونة"), tabs, group_row, icon_grid]

    def save():
        if c:
            repo.update_category(c["id"], name=name.value, icon=s["icon"], color=s["color"])
        else:
            repo.add_category(kind, name.value, parent_id=parent_id, icon=s["icon"], color=s["color"])
        return True

    form = FormSheet(ui, "تعديل فئة" if c else ("فئة فرعية جديدة" if parent_id else "فئة جديدة"), controls, save).open()


def reassign_form(ui, c, used):
    repo, s = ui.repo, {"to": None}
    options = []
    for top in repo.category_tree(c["kind"]):
        for x in [top] + top["children"]:
            if x["id"] != c["id"] and x["parent_id"] != c["id"]:
                options.append((x["id"], x["name"]))

    def pick(v):
        s["to"] = v
        form.render()

    def controls():
        return [kit.txt(f"الفئة مستخدمة في {used} معاملة. اختر فئة بديلة تنتقل لها هذه المعاملات:", 14, color=T.MUTED),
                choices(options, s["to"], pick)]

    def save():
        if s["to"] is None:
            ui.toast("اختر فئة بديلة")
            return False
        repo.delete_category(c["id"], reassign_to=s["to"])
        return True

    form = FormSheet(ui, f"حذف «{c['name']}»", controls, save, save_label="حذف ونقل المعاملات").open()
