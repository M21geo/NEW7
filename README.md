# مصاريفي (Masarif)

تطبيق مصاريف شخصية بـ Python + Flet + SQLite.

## الهيكل
- `app/money.py`   الأرقام بأصغر وحدة (دينار = 1، دولار = سنت) وتحويل العملات
- `app/db.py`      مخطط قاعدة البيانات
- `app/repo.py`    كل منطق التطبيق: المحافظ، الفئات، الأشخاص، المعاملات، التحويلات، الفلاتر، الملاحظات
- `app/seed.py`    البيانات الافتراضية عند أول تشغيل
- `app/debts.py`   الديون (عليّ / لي) والدفعات، مع ترحيل الدفعة لمحفظة اختيارياً
- `app/stats.py`   إحصائيات الشهر: نظرة، فئات، أشخاص، محافظ، أيام الأسبوع، أكبر المصاريف
- `app/backup.py`  نسخ احتياطي JSON (استبدال/دمج) مع تدوير آخر N نسخة
- `app/importer.py` استيراد CSV / Excel / JSON مع ربط الأعمدة ومعاينة وكشف التكرار
- `tests/`         اختبارات (تشغيل: `python -m unittest discover -s tests`)

## الخطوات القادمة
3. واجهة Flet (الشاشات)
4. بناء APK

## الواجهة (الخطوة 3)
- الشاشات: الرئيسية، المعاملات (بحث + فلتر متقدم)، الإحصائيات (4 تبويبات)، شيت الإضافة/التعديل، تفاصيل المعاملة.
- **تنبيه:** الواجهة لم تُشغَّل على Flet الحقيقي (المكتبة غير متاحة في بيئة التطوير). فحص الدخان `tests/test_ui_smoke.py` يكشف أخطاء بايثون فقط، لا أخطاء واجهة Flet.
- التشغيل: `pip install -r requirements.txt` ثم `python main.py` (أو `flet run`). أي خطأ بالشاشة يظهر بنصه الكامل، انسخه وارسله.

## تحديث: دمج الإحصائيات مع المعاملات
- شاشة «المعاملات» صارت فيها القائمة والإحصائيات معاً (ملخص، فئات بدائرة، تحليل بهستوغرام). بدون فلتر = إحصائيات الشهر المختار؛ مع أي فلتر = المعاملات المفلترة وإحصائياتها.
- الأرقام المكتوبة تنفرز تلقائياً: 10,000,000.

## الخطوة 4: شاشات «المزيد»
المحافظ (إضافة/تعديل/ترتيب/أرشفة/حذف/تحويل)، الديون (دفعات وربط بمحفظة)، الملاحظات (تثبيت)، الفئات (إضافة/تعديل/ترتيب/حذف مع نقل المعاملات)، الأشخاص، الاستيراد (CSV/Excel/JSON مع ربط الأعمدة ومعاينة)، النسخ الاحتياطي (الآن/تصدير/استرجاع بدمج أو استبدال)، الإعدادات (العملة، سعر الصرف، النسخ التلقائي).
لم تُجرَّب على Flet الحقيقي بعد.

## تحديث: ميزانية، تكرار، تقسيط، تقويم، إخفاء الأرصدة
- الدين يرتبط بمحفظة عند الإنشاء (استلام/تسليم) وعند الدفعات والزيادة، مع تقسيط (شهري/أسبوعي) وجدول أقساط.
- ميزانية شهرية كلية ولكل فئة (أو فرعية) مع تنبيه عند الحفظ، ومعاملات تكرارية تُسجَّل تلقائياً عند فتح التطبيق.
- كل حقول التاريخ تفتح تقويماً. إخفاء الأرصدة عام (أيقونة العين) أو لمحفظة معينة.
- قاعدة البيانات تترقى تلقائياً من الإصدار 2 إلى 3 (بياناتك القديمة تبقى).

## تحديث: هستوري، مسح البيانات، تذكير
- **الهستوري** (المزيد ← الهستوري): أرشيفات معزولة (هستوري 1، 2، ...) كل واحد قاعدة بيانات مستقلة بفئاته وأشخاصه ومحافظه من الملف المرفوع. يُفتح بنفس القائمة والفلتر والإحصائيات للعرض فقط، ولا يؤثر على الأرصدة ولا الفئات ولا الأشخاص ولا الميزانيات ولا النسخ الاحتياطية للتطبيق الرئيسي.
- عند **استيراد ملف** أو **استرجاع نسخة** تختار: التطبيق الرئيسي أو هستوري معزول.
- **مسح البيانات** (الإعدادات): مسح المعاملات والديون فقط، أو إعادة ضبط كاملة. يتطلب كتابة كلمة «مسح»، وتُحفظ نسخة أمان قبله. الهستوري ما ينمسح.
- **التذكير اليومي**: نافذة داخل التطبيق بوقت تحدده (إذا ما سجلت شي اليوم أو عندك قسط قريب). التنبيهات خارج التطبيق على أندرويد تحتاج مكوّن إضافي لم يُبنَ بعد.

## إصلاحات
- خطأ SQLite «created in a thread»: الاتصال صار يعمل من أي thread (Flet يشغّل الأوامر على threads مختلفة).
- الاستيراد: ملف واحد ممكن يحتوي دينار ودولار (من عمود العملة أو رمز $ / د.ع بالمبلغ)؛ كل صف يروح لمحفظة بعملته. الهستوري يبدأ فارغاً وتنشأ محافظه من الملف.
- قارئ xlsx أقوى (ترتيب الأوراق، ملفات بدون مراجع خلايا، أرقام علمية). xls القديم غير مدعوم برسالة واضحة. الأخطاء تبقى ظاهرة بشاشة الاستيراد.

## تحسين الأداء (4e)
- قائمة المعاملات تُعرض على دفعات (40 ثم +80 بزر «عرض المزيد»)، وأرشيف الهستوري يحتفظ بنتيجة الحساب (كاش) فلا يُعاد عند التنقل بين التبويبات.
- قياس على 50 ألف معاملة (بايثون فقط): 12.3 ث → 0.48 ث لفتح القائمة.
- الديون: تحت كل دين قائمة «الدفعات المسدّدة» بتفاصيلها (رقم الدفعة، التاريخ، المبلغ، المحفظة، الملاحظة، المتبقي بعدها).
- الاستيراد: يقرأ التواريخ العربية (21 يناير، 2026 / أيلول)، ويدعم التحويلات عبر عمود «إلى المحفظة»، ويتعرف على أعمدة (التكلفة، القسم، القسم الرئيسي، جهة الإتصال).

## 5c
- ثيم صيفي حيوي (تدرّج بحري، زر + برتقالي، ألوان فئات زاهية تلقائية).
- شاشة المعاملات تتمرر كصفحة واحدة (الفلاتر والترويسة تنزاح مع القائمة).
- عرض أسبوعي (السبت–الجمعة) وشهري، مع مقارنة بالفترة السابقة.
- الضغط على أي ملخص/فئة/شخص/محفظة/عمود رسم/أكبر مصروف يفتح معاملاته.
- إصلاح علامة (−) في الأرقام داخل النص العربي، ونص بطاقة التذكير المقصوص.
- الرسم الدائري: الإجمالي بالمنتصف دائماً، نسب داخل القطاعات، دمج القطاعات الصغيرة (<3%) في «أخرى»، ومفتاح ألوان بالنسب.

## Step 6 (this version)
- Home: the main wallet (star) replaces the big total card; the total of all wallets is under the wallet list.
- Recurring transactions are never created automatically; Home shows a reminder card with "تنفيذ المستحق".
- Android back button / swipe-back (two stacked views + `on_view_pop`, see `ui/app.py::_install_views`), double back on Home exits.
- Lock: password (PBKDF2, recovery code), lock the whole app and/or the More tab. Fingerprint needs a Flet release that
  ships `flet-local-auth`; `app/biometric.py` uses it when present, otherwise the switch explains it is unavailable.
- Backups: interval and number of copies are settings. People can be moved up/down (schema v4).
- PDF export (`app/pdf_report.py`, reportlab + bundled DejaVu font, own Arabic shaping in `app/arabic.py`).
- English UI (`app/i18n.py`, `app/i18n_en.py`; `tests/test_i18n.py` fails if any Arabic UI text has no English).
- Funny rotating reminders; smart notes and debts use meaningful colours.

## Step 7 (this update)
- Notes can carry a picture (pick, view, save back out); stored in the database so backups include it.
- Redrawing a screen (expanding a category, opening the password box) keeps your scroll position.
- Scrollbar sits at the screen edge, away from the text.
- Dollar income/expense has its own "rate on this day" field (stored per transaction; statistics use it).
- People can be hidden from the add-transaction sheet (eye button in More > People) and shown again any time.

## Step 7b
- Fixed 0-byte backup/PDF on Android (Flet 0.28 save dialog gives a virtual path): files are written into Download/Masarif and verified by size; auto backups are mirrored to Download/Masarif/auto.
- Fixed "can't update APK": fixed signing key + increasing build number in the workflow.
- Back no longer flickers (view is never popped); exit really closes the app on Android.
- Wallet cards on Home are smaller.

## Step 7c
- Categories tab: opening a category's sub-categories redraws only that row (no jump to the top and back).
- Every backup/export is now one full file: all tables (notes with pictures, debts, people, settings...) plus all History archives. Restoring brings the archives back too.
- Wallet and person names are coloured tags (wallet colour = its card colour on Home).

## Step 7d
- Dark mode (Settings > Appearance: light / dark / follow phone). Notes and History survive a full reset.
- Thin dividers between transactions of one day; wallet/person tags sized to their text, side by side.
- Restore dialog: "Isolated History" first (own categories/wallets/people), then merge, then replace.
- Categories page: rows no longer clip on the right (compact buttons, wrapping names).

## Step 7e
- PDF export uses Noto Sans Arabic (standard Android Arabic font, SIL OFL licence in app/fonts) instead of DejaVu; DejaVu is kept only for Latin letters and symbols.

## Step 7f
- Notes: pictures show large in the card; tap -> full-screen viewer with pinch zoom + save.
- Add-transaction sheet: category / sub-category / person chips fold to 1 line (wallets included) with a small arrow to open the rest (settings order).
- Categories manager redesigned: cards with sub-category arrow, item menu, drag-and-drop ordering sheet.
- Fixed: restoring the same full backup twice duplicated History archives (creation time is now kept).

## Step 7h
- Receipts: attach a picture to any transaction (add/edit sheet). Stored as a small JPEG (longest side 1280 px, ~100-250 KB) inside the app, so deleting the original from the phone is fine. Shown in the transaction details, a paper-clip on the list row, included in backups/restore. Needs the `pillow` dependency (remove it from requirements.txt / pyproject.toml if a build ever fails on it; pictures are then stored as is up to 1.5 MB).
- Icons: category icon picker has "plain" Material icons and "3D" colour emoji, in groups (food, transport, home, health, shopping, fun, money, other), plus 16 colours and a live preview.
- Chips (categories / wallets / people) are no longer clipped when folded.

## Step 8 - Flet 1.0 and out-of-app notifications
- Ported from Flet 0.28.3 to Flet 1.0.x: `ft.Padding/Margin/Border/Alignment`, `page.show_dialog` (via `kit.show/hide`), async `FilePicker` (`kit.pick_file`, `kit.save_bytes`), `Dropdown.on_select`, `PopupMenuItem(content=)`, `BottomSheet(scrollable=)`, images passed as bytes, single view with `can_pop=False` + `on_confirm_pop` for the back button, `ft.run`.
- New `app/notify.py`: real phone notifications through `flet-notifications`. The next 14 days are scheduled as separate notifications (varied funny wording + debts due that day), re-planned on every start and whenever the reminder switch/time changes.
- Fingerprint login works through `flet-local-auth` (service registers itself in 1.0).
- CI: `flet build apk`, then `flet-notifications-patch` + `gradlew assembleRelease` + `apksigner` with the same fixed key; flet's own gradle step is expected to fail first (core-library desugaring is only added by the patch).
- Tests: `tests/real_flet_smoke.py` builds every screen/sheet against the REAL Flet 1.0 source (run alone: `python -m unittest tests.real_flet_smoke`; needs the flet source on the path, see the file). Not proven on a phone yet: back button, file saving, notifications.
