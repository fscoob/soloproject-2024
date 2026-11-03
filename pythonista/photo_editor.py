# -*- coding: utf-8 -*-
"""
محرر الصور - تطبيق لـ Pythonista على iOS
----------------------------------------
- اختيار صورة من الألبوم أو التقاطها بالكاميرا
- فلاتر: أبيض وأسود، سيبيا، دافئ، بارد، تنعيم، حدّة، فينيت، رسم
- أدوات: تدوير، قلب، قص مربع / 4:5 / 9:16
- منزلقات: سطوع، تباين، تشبّع، دفء
- تراجع، إعادة ضبط، حفظ في الألبوم، مشاركة

التشغيل: افتح الملف في Pythonista واضغط ▶︎
"""

import io

import ui
import photos
import dialogs
import console
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw

PREVIEW_MAX = 1200      # أقصى بُعد لصورة المعاينة (للسرعة)
UNDO_LIMIT = 8          # عدد خطوات التراجع
BG = '#111418'
PANEL = '#1c2128'
ACCENT = '#f2a33a'
TEXT = '#e6e6e6'


# ----------------------------------------------------------------- أدوات PIL

def pil_to_ui(img):
    """تحويل صورة PIL إلى ui.Image للعرض."""
    buf = io.BytesIO()
    img.convert('RGB').save(buf, 'JPEG', quality=90)
    return ui.Image.from_data(buf.getvalue())


def downscale(img, max_side=PREVIEW_MAX):
    img = img.copy()
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    return img


def tint(img, r, g, b):
    """تغيير توازن الألوان بضرب كل قناة بمعامل."""
    rc, gc, bc = img.convert('RGB').split()
    rc = rc.point(lambda v: min(255, int(v * r)))
    gc = gc.point(lambda v: min(255, int(v * g)))
    bc = bc.point(lambda v: min(255, int(v * b)))
    return Image.merge('RGB', (rc, gc, bc))


def sepia(img):
    gray = ImageOps.grayscale(img)
    return ImageOps.colorize(gray, '#2b1a0e', '#f5e6c8')


def vignette(img, strength=0.55):
    img = img.convert('RGB')
    w, h = img.size
    mask = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(mask)
    pad_w, pad_h = int(w * 0.08), int(h * 0.08)
    d.ellipse((pad_w, pad_h, w - pad_w, h - pad_h), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(max(w, h) // 8))
    dark = ImageEnhance.Brightness(img).enhance(1 - strength)
    return Image.composite(img, dark, mask)


def sketch(img):
    gray = ImageOps.grayscale(img)
    inv = ImageOps.invert(gray).filter(ImageFilter.GaussianBlur(8))
    # Color dodge
    g = gray.load()
    i = inv.load()
    out = Image.new('L', gray.size)
    o = out.load()
    w, h = gray.size
    for y in range(h):
        for x in range(w):
            a, b = g[x, y], i[x, y]
            o[x, y] = 255 if b == 255 else min(255, (a * 255) // (255 - b))
    return out.convert('RGB')


def crop_ratio(img, rw, rh):
    """قص من المنتصف بنسبة rw:rh."""
    w, h = img.size
    target = rw / rh
    if w / h > target:
        nw = int(h * target)
        left = (w - nw) // 2
        return img.crop((left, 0, left + nw, h))
    nh = int(w / target)
    top = (h - nh) // 2
    return img.crop((0, top, w, top + nh))


FILTERS = [
    ('أبيض وأسود', lambda im: ImageOps.grayscale(im).convert('RGB')),
    ('سيبيا', sepia),
    ('دافئ', lambda im: tint(im, 1.10, 1.02, 0.88)),
    ('بارد', lambda im: tint(im, 0.90, 1.00, 1.12)),
    ('تنعيم', lambda im: im.filter(ImageFilter.GaussianBlur(2))),
    ('حدّة', lambda im: im.filter(ImageFilter.UnsharpMask(2, 150, 3))),
    ('فينيت', vignette),
    ('تلقائي', lambda im: ImageOps.autocontrast(im.convert('RGB'), cutoff=1)),
    ('رسم', sketch),
]

TOOLS = [
    ('↻ تدوير', lambda im: im.rotate(-90, expand=True)),
    ('⇋ قلب', ImageOps.mirror),
    ('◻︎ 1:1', lambda im: crop_ratio(im, 1, 1)),
    ('▭ 4:5', lambda im: crop_ratio(im, 4, 5)),
    ('▯ 9:16', lambda im: crop_ratio(im, 9, 16)),
]

SLIDERS = [
    # (المفتاح، الاسم، الحد الأدنى، الحد الأعلى)
    ('brightness', 'سطوع', 0.4, 1.6),
    ('contrast', 'تباين', 0.4, 1.6),
    ('color', 'تشبّع', 0.0, 2.0),
    ('warmth', 'دفء', -0.25, 0.25),
]


def apply_adjustments(img, adj):
    img = img.convert('RGB')
    if adj['brightness'] != 1:
        img = ImageEnhance.Brightness(img).enhance(adj['brightness'])
    if adj['contrast'] != 1:
        img = ImageEnhance.Contrast(img).enhance(adj['contrast'])
    if adj['color'] != 1:
        img = ImageEnhance.Color(img).enhance(adj['color'])
    if adj['warmth']:
        w = adj['warmth']
        img = tint(img, 1 + w, 1, 1 - w)
    return img


# ---------------------------------------------------------------- الواجهة

class PhotoEditor(ui.View):

    def __init__(self):
        super().__init__()
        self.name = 'محرر الصور'
        self.background_color = BG
        self.tint_color = ACCENT

        self.full = None        # الصورة بكامل الدقة بعد العمليات
        self.preview = None     # نسخة مصغرة للمعاينة
        self.undo = []
        self.busy = False
        self.adj = self.default_adj()

        # أزرار شريط العنوان
        self.left_button_items = [
            ui.ButtonItem(title='فتح', action=self.open_photo),
            ui.ButtonItem(title='كاميرا', action=self.take_photo),
        ]
        self.right_button_items = [
            ui.ButtonItem(title='حفظ', action=self.save_photo),
            ui.ButtonItem(image=ui.Image.named('iob:ios7_upload_outline_24'),
                          action=self.share_photo),
            ui.ButtonItem(image=ui.Image.named('iob:ios7_undo_outline_24'),
                          action=self.undo_action),
        ]

        # عرض الصورة
        self.image_view = ui.ImageView(content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
        self.image_view.background_color = '#000'
        self.add_subview(self.image_view)

        self.hint = ui.Label(text='اضغط «فتح» لاختيار صورة',
                             alignment=ui.ALIGN_CENTER,
                             text_color='#888', font=('<system>', 17))
        self.add_subview(self.hint)

        # لوحة التحكم
        self.panel = ui.View(background_color=PANEL)
        self.add_subview(self.panel)

        self.tabs = ui.SegmentedControl(segments=['فلاتر', 'تعديل', 'أدوات'])
        self.tabs.selected_index = 0
        self.tabs.action = self.tab_changed
        self.panel.add_subview(self.tabs)

        self.filter_strip = self.make_strip(FILTERS, self.filter_tapped)
        self.tool_strip = self.make_strip(
            TOOLS + [('⟲ الأصل', None)], self.tool_tapped)
        self.adjust_view = self.make_sliders()
        for v in (self.filter_strip, self.tool_strip, self.adjust_view):
            self.panel.add_subview(v)
        self.tab_changed(self.tabs)

    # ---------------------------------------------------- البناء والتخطيط

    @staticmethod
    def default_adj():
        return {'brightness': 1.0, 'contrast': 1.0, 'color': 1.0, 'warmth': 0.0}

    def make_strip(self, items, action):
        sv = ui.ScrollView(shows_horizontal_scroll_indicator=False)
        x = 10
        for title, func in items:
            b = ui.Button(title=title, font=('<system-bold>', 14))
            b.tint_color = TEXT
            b.background_color = '#2a313b'
            b.corner_radius = 10
            b.frame = (x, 10, 92, 44)
            b.func = func
            b.action = action
            sv.add_subview(b)
            x += 100
        sv.content_size = (x, 64)
        return sv

    def make_sliders(self):
        v = ui.View()
        self.sliders = {}
        for i, (key, title, lo, hi) in enumerate(SLIDERS):
            lbl = ui.Label(text=title, text_color=TEXT,
                           font=('<system>', 14), alignment=ui.ALIGN_RIGHT)
            lbl.name = 'lbl_' + key
            s = ui.Slider()
            s.key, s.lo, s.hi = key, lo, hi
            s.continuous = False
            s.action = self.slider_changed
            s.value = self.to_slider(key)
            v.add_subview(lbl)
            v.add_subview(s)
            self.sliders[key] = (lbl, s)
        return v

    def layout(self):
        w, h = self.width, self.height
        panel_h = 190
        self.image_view.frame = (0, 0, w, h - panel_h)
        self.hint.frame = self.image_view.frame
        self.panel.frame = (0, h - panel_h, w, panel_h)
        self.tabs.frame = (10, 8, w - 20, 32)
        content = (0, 46, w, panel_h - 46)
        self.filter_strip.frame = content
        self.tool_strip.frame = content
        self.adjust_view.frame = content
        row = (panel_h - 46) / len(SLIDERS)
        for i, (key, _, _, _) in enumerate(SLIDERS):
            lbl, s = self.sliders[key]
            s.frame = (12, i * row, w - 100, row)
            lbl.frame = (w - 84, i * row, 72, row)

    def tab_changed(self, sender):
        idx = sender.selected_index
        self.filter_strip.hidden = idx != 0
        self.adjust_view.hidden = idx != 1
        self.tool_strip.hidden = idx != 2

    # ------------------------------------------------------- الحالة والعرض

    def to_slider(self, key):
        _, _, lo, hi = next(s for s in SLIDERS if s[0] == key)
        return (self.adj[key] - lo) / (hi - lo)

    def load_image(self, img):
        img = ImageOps.exif_transpose(img).convert('RGB')
        self.full = img
        self.original = img.copy()
        self.preview = downscale(img)
        self.undo = []
        self.reset_adjustments()
        self.hint.hidden = True
        self.refresh()

    def reset_adjustments(self):
        self.adj = self.default_adj()
        for key, (_, s) in self.sliders.items():
            s.value = self.to_slider(key)

    def refresh(self):
        if self.preview is None:
            return
        shown = apply_adjustments(self.preview, self.adj)
        self.image_view.image = pil_to_ui(shown)

    def push_undo(self):
        self.undo.append((self.full, self.preview, dict(self.adj)))
        if len(self.undo) > UNDO_LIMIT:
            self.undo.pop(0)

    @ui.in_background
    def apply_op(self, func, max_side=None):
        """تطبيق عملية على الصورة الكاملة ثم تحديث المعاينة."""
        if self.full is None:
            console.hud_alert('اختر صورة أولاً', 'error', 1)
            return
        if self.busy:
            return
        self.busy = True
        console.show_activity('جاري المعالجة…')
        try:
            self.push_undo()
            src = downscale(self.full, max_side) if max_side else self.full
            self.full = func(src).convert('RGB')
            self.preview = downscale(self.full)
            ui.delay(self.refresh, 0)
        finally:
            console.hide_activity()
            self.busy = False

    # ------------------------------------------------------------ الإجراءات

    def filter_tapped(self, sender):
        # فلتر «رسم» بطيء نسبياً، لذلك نطبّقه على نسخة بدقة أقل
        self.apply_op(sender.func, 1600 if sender.func is sketch else None)

    def tool_tapped(self, sender):
        if sender.func is None:   # الرجوع للأصل
            if self.full is None:
                return
            self.push_undo()
            self.full = self.original.copy()
            self.preview = downscale(self.full)
            self.reset_adjustments()
            self.refresh()
        else:
            self.apply_op(sender.func)

    def slider_changed(self, sender):
        self.adj[sender.key] = sender.lo + sender.value * (sender.hi - sender.lo)
        self.refresh()

    def undo_action(self, sender):
        if not self.undo:
            console.hud_alert('لا يوجد ما يمكن التراجع عنه', 'error', 1)
            return
        self.full, self.preview, adj = self.undo.pop()
        self.adj = adj
        for key, (_, s) in self.sliders.items():
            s.value = self.to_slider(key)
        self.refresh()

    @ui.in_background
    def open_photo(self, sender):
        asset = photos.pick_asset(assets=photos.get_assets(media_type='image'),
                                  title='اختر صورة')
        if asset is None:
            return
        console.show_activity('جاري التحميل…')
        try:
            img = asset.get_image(original=False)
            self.load_image(img)
        finally:
            console.hide_activity()

    @ui.in_background
    def take_photo(self, sender):
        img = photos.capture_image()
        if img is not None:
            self.load_image(img)

    def final_image(self):
        return apply_adjustments(self.full, self.adj)

    @ui.in_background
    def save_photo(self, sender):
        if self.full is None:
            console.hud_alert('اختر صورة أولاً', 'error', 1)
            return
        console.show_activity('جاري الحفظ…')
        try:
            ok = photos.save_image(self.final_image())
        finally:
            console.hide_activity()
        console.hud_alert('تم الحفظ في الألبوم ✓' if ok else 'فشل الحفظ',
                          'success' if ok else 'error', 1.2)

    @ui.in_background
    def share_photo(self, sender):
        if self.full is None:
            console.hud_alert('اختر صورة أولاً', 'error', 1)
            return
        dialogs.share_image(pil_to_ui(self.final_image()))


if __name__ == '__main__':
    PhotoEditor().present('fullscreen', hide_title_bar=False,
                          title_bar_color=PANEL, title_color=TEXT)
