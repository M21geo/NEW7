"""Transaction details sheet (edit / delete)."""
import flet as ft

from . import kit, theme as T, vm
from .rows import TONE_COLOR


def show_tx(ui, tx_id: int, readonly: bool = False):
    t = ui.guard(ui.repo.get_transaction, tx_id)
    if not t:
        return
    r = vm.tx_row(t, ui.today)
    sheet = {}

    def close():
        kit.hide(ui.page, sheet["s"])

    def edit(e):
        close()
        ui.add_transaction(t)

    def delete(e):
        def do():
            ui.guard(ui.repo.delete_transaction, tx_id)
            close()
            ui.toast("تم الحذف")
            ui.refresh()
        kit.confirm(ui.page, "حذف المعاملة", "متأكد؟ هذا الإجراء يغيّر رصيد المحفظة.", do)

    def line(label, value):
        return kit.between(kit.txt(label, 14, color=T.MUTED), kit.txt(value, 14, True))

    lines = [line("النوع", vm.KIND_LABELS[t["kind"]]), line("التاريخ", f"{r['date_label']} · {t['date']}"),
             kit.between(kit.txt("المحفظة", 14, color=T.MUTED),
                         kit.row([kit.wallet_tag(t["wallet_name"])] +
                                 ([kit.txt("←", 13, color=T.MUTED), kit.wallet_tag(t["to_wallet_name"])] if t["kind"] == "transfer" else []),
                                 spacing=6))]
    if t["kind"] != "transfer":
        if t["category_name"]:
            lines.append(line("الفئة", r["title"]))
        if t["person_name"]:
            lines.append(kit.between(kit.txt("الشخص", 14, color=T.MUTED), kit.person_tag(t["person_name"])))
    if r["recv_text"]:
        lines.append(line("المستلم", r["recv_text"]))
    if t["note"]:
        lines.append(kit.box(kit.txt(t["note"], 14), bg=T.SOFT, border=None))
    receipt = ui.repo.get_receipt(tx_id) if hasattr(ui.repo, "get_receipt") else ""
    if receipt:
        lines.append(ft.Container(
            ft.Stack([ft.Image(src=kit.img_src(receipt), width=ui.w - 40, height=200, fit=ft.BoxFit.CONTAIN),
                      ft.Container(kit.icon("zoom_out_map", 18, "#FFFFFF"), right=8, bottom=8, padding=6, border_radius=14,
                                   bgcolor=ft.Colors.with_opacity(0.55, "#000000"))], width=ui.w - 40, height=200),
            border_radius=14, bgcolor=T.SOFT, clip_behavior=ft.ClipBehavior.ANTI_ALIAS, ink=True,
            on_click=lambda e: kit.view_image(ui, receipt, f"receipt_{tx_id}")))
    content = kit.col([
        kit.row([kit.icon_tile(r["icon"], r["color"], 52), kit.col([kit.txt(r["title"], 17, True)], expand=True)], spacing=12),
        kit.txt(r["amount_text"], 30, True, TONE_COLOR[r["tone"]]),
        *lines,
        *([] if readonly else [kit.row([ft.Container(kit.big_button("تعديل", edit), expand=True),
                                        ft.Container(kit.big_button("حذف", delete, bg=T.EXPENSE), expand=True)], spacing=10)]),
    ], spacing=14, scroll=True)
    sheet["s"] = ui.open_sheet(content, height=min(ui.h * 0.8, 620))
