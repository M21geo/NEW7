"""More > Notes (pinned first). A note can carry a picture (pick from the gallery, view, save back out)."""
import flet as ft

from .. import noteimg
from . import kit, theme as T
from .rows import empty_state, page_frame, small_btn


def build_notes(ui):
    repo = ui.repo

    def view_image(n):
        kit.view_image(ui, n["image"], f"note_{n['id']}")

    def save_image(n):
        kit.save_bytes(ui, f"note_{n['id']}.{noteimg.guess_ext(n['image'])}", noteimg.to_bytes(n["image"]),
                       [noteimg.guess_ext(n["image"])], "احفظ الصورة", "انحفظت الصورة")

    def edit(n):
        f = kit.field("الملاحظة", n["text"] if n else "", multiline=True)
        st = {"img": n["image"] if n else ""}          # base64 text, "" = no picture
        holder = ft.Column(spacing=8, tight=True)

        def draw():
            ctl = []
            if st["img"]:
                ctl.append(ft.Image(src=kit.img_src(st["img"]), height=150, fit=ft.BoxFit.COVER, border_radius=12))
            ctl.append(kit.row([ft.TextButton(("تغيير الصورة" if st["img"] else "إضافة صورة"), on_click=pick),
                                *([ft.TextButton("إزالة", on_click=drop)] if st["img"] else [])], spacing=4))
            holder.controls = ctl
            ui.page.update()

        def picked(path):
            try:
                st["img"] = noteimg.load(path)
            except Exception as ex:
                ui.toast(str(ex))
                return
            draw()

        def pick(e):
            kit.pick_file(ui, picked, noteimg.EXTENSIONS, "اختر صورة")

        def drop(e):
            st["img"] = ""
            draw()

        def ok(e):
            r = (ui.guard(repo.update_note, n["id"], f.value, st["img"]) if n
                 else ui.guard(repo.add_note, f.value, False, st["img"]))
            if n or r is not None:
                kit.hide(ui.page, dlg)
                ui.refresh()

        dlg = ft.AlertDialog(title=ft.Text("تعديل ملاحظة" if n else "ملاحظة جديدة"),
                             content=ft.Container(ft.Column([f, holder], spacing=10, tight=True, scroll=ft.ScrollMode.AUTO), width=320),
                             actions=[ft.TextButton("إلغاء", on_click=lambda e: kit.hide(ui.page, dlg)), ft.TextButton("حفظ", on_click=ok)])
        holder.controls = []
        kit.show(ui.page, dlg)
        draw()

    def pin(n):
        repo.toggle_note_pin(n["id"])
        ui.refresh()

    def delete(n):
        kit.confirm(ui.page, "حذف الملاحظة", "متأكد؟", lambda: (repo.delete_note(n["id"]), ui.refresh()))

    cards = []
    for n in repo.list_notes():
        pinned = bool(n["pinned"])
        body = []
        if n["image"]:
            body.append(ft.Container(
                ft.Stack([ft.Image(src=kit.img_src(n["image"]), width=ui.w - 40 - 28, height=220, fit=ft.BoxFit.CONTAIN),
                          ft.Container(kit.icon("zoom_out_map", 18, "#FFFFFF"), right=8, bottom=8, padding=6, border_radius=14,
                                       bgcolor=ft.Colors.with_opacity(0.55, "#000000"))],
                         width=ui.w - 40 - 28, height=220),
                border_radius=12, bgcolor=T.SOFT, clip_behavior=ft.ClipBehavior.ANTI_ALIAS, ink=True,
                on_click=lambda e, n=n: view_image(n)))
        if n["text"]:
            body.append(kit.txt(n["text"], 15))
        acts = [small_btn("push_pin" if pinned else "push_pin_outlined", lambda e, n=n: pin(n), color=T.PRIMARY if pinned else T.MUTED),
                small_btn("edit", lambda e, n=n: edit(n))]
        if n["image"]:
            acts.append(small_btn("download", lambda e, n=n: save_image(n), "حفظ الصورة", color=T.PRIMARY))
        acts.append(small_btn("delete_outline", lambda e, n=n: delete(n), color=T.EXPENSE))
        cards.append(kit.box(kit.col(body + [kit.row(acts, spacing=0)], spacing=6), bg=T.PRIMARY_SOFT if pinned else T.CARD))
    return page_frame(ui, "الملاحظات", [kit.big_button("+ ملاحظة", lambda e: edit(None))] + (cards or [empty_state("ما في ملاحظات")]))
