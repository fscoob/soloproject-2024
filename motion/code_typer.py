#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
code_typer.py — مونتاج «كأنه يكتب الكود» (Motion v1)
=====================================================
يولّد ريل عمودي 9:16 فيه شاشة على مكتب تُكتب عليها أسطر كود حرفاً حرفاً
في توقيت تحدده أنت (مثلاً على إيقاع أغنية)، مع:
  - تلوين الكود (Syntax highlighting) ورقم السطر ومؤشر يومض
  - حركة كاميرا خفيفة كأنها محمولة باليد + تقريب بطيء
  - عنوان أعلى الفيديو (يدعم العربي والإيموجي)
  - صوت نقرات كيبورد متزامن مع الكتابة، ودمج موسيقى اختيارياً
  - مشهد مكتب مرسوم تلقائياً، أو صورتك الحقيقية لشاشتك (--bg + --screen)

المتطلبات: Python 3 + Pillow + numpy + ffmpeg

أمثلة:
  python3 code_typer.py example.json -o reel.mp4
  python3 code_typer.py example.json -o reel.mp4 --music song.mp3 --music-start 62
  python3 code_typer.py example.json --preview 6.5 -o frame.png
  python3 code_typer.py example.json -o reel.mp4 --bg desk.jpg \\
          --screen 120,610,980,650,975,1150,115,1190
"""

import argparse
import bisect
import json
import math
import os
import random
import re
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920           # مقاس الريل
OVER = 1.14                 # المشهد أكبر قليلاً لإتاحة حركة الكاميرا
SW, SH = int(W * OVER), int(H * OVER)
EW, EH = 1600, 900          # مقاس شاشة المحرر قبل إسقاطها على الشاشة

THEME = {
    'bg': (22, 27, 38), 'tabbar': (16, 20, 29), 'tab': (30, 37, 51),
    'line_hl': (34, 43, 60), 'gutter': (88, 98, 118), 'gutter_on': (190, 198, 214),
    'text': (214, 222, 235), 'punct': (176, 186, 204), 'keyword': (255, 92, 138),
    'func': (111, 195, 255), 'prop': (246, 208, 107), 'string': (165, 214, 138),
    'number': (242, 163, 58), 'comment': (120, 132, 154), 'cursor': (255, 79, 123),
}
KEYWORDS = set('''if else while for return const let var new true false null
undefined function await async break continue try catch throw class import
from export def in of not and or self this'''.split())

MONO = ['JetBrainsMono-SemiBold.ttf', 'JetBrainsMono-Bold.ttf', 'Menlo.ttc',
        'DejaVuSansMono-Bold.ttf', 'Consolas.ttf', 'Courier New Bold.ttf']
SANS = ['DejaVuSans-Bold.ttf', 'Arial Bold.ttf', 'Helvetica.ttc',
        'FreeSansBold.ttf', 'Arial.ttf']
EMOJI = ['NotoColorEmoji.ttf', 'Apple Color Emoji.ttc']
FONT_DIRS = ['/usr/share/fonts', '/Library/Fonts', '/System/Library/Fonts',
             os.path.expanduser('~/Library/Fonts'), 'C:/Windows/Fonts']


def find_font(names):
    for d in FONT_DIRS:
        for root, _, files in os.walk(d):
            for n in names:
                if n in files:
                    return os.path.join(root, n)
    return None


# ------------------------------------------------------------- أدوات عامة

def ease(t):
    t = min(1.0, max(0.0, t))
    return 0.5 - 0.5 * math.cos(math.pi * t)


def perspective_coeffs(dst, src):
    """معاملات PIL PERSPECTIVE: نقطة في الناتج (dst) ← نقطة في المصدر (src)."""
    a = []
    for (x, y), (u, v) in zip(dst, src):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    b = [c for p in src for c in p]
    return np.linalg.solve(np.array(a, float), np.array(b, float)).tolist()


def vgrad(size, top, bottom):
    w, h = size
    t = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(top)[None, None, :] * (1 - t) + np.array(bottom)[None, None, :] * t
    return Image.fromarray(np.repeat(arr, w, axis=1).astype('uint8'), 'RGB')


def glow(base, center, radius, color, strength):
    """توهج ضوئي ناعم (إضافة لونية)."""
    w, h = base.size
    y, x = np.ogrid[:h, :w]
    d = np.sqrt(((x - center[0]) / radius[0]) ** 2 + ((y - center[1]) / radius[1]) ** 2)
    m = np.clip(1 - d, 0, 1) ** 2 * strength
    arr = np.asarray(base, float) + m[..., None] * np.array(color)[None, None, :]
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGB')


# ------------------------------------------------------------- السكربت

class Script:
    def __init__(self, data, seed=7):
        self.title = data.get('title', '')
        self.handle = data.get('handle', '')
        self.file = data.get('file', 'main.js')
        self.fps = int(data.get('fps', 30))
        rnd = random.Random(seed)
        self.lines = []           # (code, [زمن كل حرف])
        for ln in data['lines']:
            code = ln.get('code', '')
            at = float(ln['at'])
            dur = float(ln.get('type', max(0.4, len(code) * 0.06)))
            times, n = [], max(1, len(code))
            for i in range(len(code)):
                jitter = (rnd.random() - 0.5) * (dur / n) * 0.9
                t = at + dur * i / n + jitter
                times.append(max(at, t if not times else max(times[-1] + 0.005, t)))
            self.lines.append((code, at, times))
        last = max((tm[-1] if tm else at) for _, at, tm in self.lines)
        self.duration = float(data.get('duration', last + 2.5))

    def state(self, t):
        """[(نص مكتوب حتى الآن، رقم السطر)] + مؤشر السطر الحالي وهل يكتب الآن."""
        shown, cur, typing = [], -1, False
        for idx, (code, at, times) in enumerate(self.lines):
            if t < at:
                break
            k = bisect.bisect_right(times, t)
            shown.append(code[:k])
            cur = idx
            if k < len(code) or (times and t - times[-1] < 0.35):
                typing = True
        return shown, cur, typing

    def key_times(self):
        out = []
        for code, _, times in self.lines:
            out += [(t, code[i]) for i, t in enumerate(times)]
        return out


# ---------------------------------------------------------- تلوين الكود

TOKEN = re.compile(r'(?P<comment>//.*|#.*)|(?P<string>"[^"]*"?|\'[^\']*\'?|`[^`]*`?)'
                   r'|(?P<number>\b\d+(?:\.\d+)?\b)|(?P<ident>[A-Za-z_$][\w$]*)'
                   r'|(?P<space>\s+)|(?P<other>.)')


def colorize(code, full):
    """تقسيم السطر لأجزاء ملوّنة. full = السطر كاملاً لمعرفة ما يليه."""
    out, depth, first = [], 0, True
    for m in TOKEN.finditer(code):
        kind, s = m.lastgroup, m.group()
        if kind == 'ident':
            nxt = full[m.end():].lstrip()[:1]
            prev = code[:m.start()].rstrip()[-1:]
            if s in KEYWORDS:
                col = THEME['keyword']
            elif nxt == '(':
                col = THEME['func']
            elif first and nxt == '.':
                col = THEME['keyword']
            elif prev == '.' or depth > 0:
                col = THEME['prop']
            else:
                col = THEME['text']
            first = False
        elif kind == 'other':
            depth += s in '([{'
            depth -= s in ')]}' and depth > 0
            col = THEME['punct']
        elif kind == 'space':
            col = THEME['text']
        else:
            col = THEME[kind]
        out.append((s, col))
    return out


class Editor:
    def __init__(self, script):
        self.s = script
        self.font = ImageFont.truetype(find_font(MONO), 46)
        self.small = ImageFont.truetype(find_font(MONO), 28)
        self.cw = self.font.getlength('M')
        self.top, self.lh, self.x0 = 92, 70, 130
        self.rows = (EH - self.top - 30) // self.lh
        self.base = self._chrome()

    def emoji(self, s):
        cache = self.__dict__.setdefault('_emoji', {})
        if s not in cache:
            cache[s] = rich_text(s, 40)
        return cache[s]

    def _chrome(self):
        im = Image.new('RGB', (EW, EH), THEME['bg'])
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, EW, 64), fill=THEME['tabbar'])
        tw = int(self.small.getlength(self.s.file)) + 110
        d.rectangle((28, 8, 28 + tw, 64), fill=THEME['tab'])
        d.rectangle((28, 8, 28 + tw, 12), fill=THEME['cursor'])
        d.rectangle((48, 28, 60, 46), fill=THEME['prop'])
        d.text((72, 22), self.s.file, font=self.small, fill=THEME['text'])
        d.text((28 + tw - 34, 22), 'x', font=self.small, fill=THEME['gutter'])
        d.ellipse((tw + 66, 28, tw + 82, 44), fill=THEME['number'])
        return im

    def scroll(self, t):
        """إزاحة عمودية ناعمة عندما يتجاوز الكود عدد الأسطر الظاهرة."""
        off = 0.0
        for idx, (_, at, _) in enumerate(self.s.lines):
            if idx >= self.rows - 2:
                off += ease((t - at) / 0.3)
        return off

    def render(self, t):
        im = self.base.copy()
        d = ImageDraw.Draw(im)
        shown, cur, typing = self.s.state(t)
        off = self.scroll(t)
        for i, text in enumerate(shown):
            y = self.top + (i - off) * self.lh
            if y < 64 - self.lh or y > EH:
                continue
            if i == cur:
                d.rectangle((0, y - 8, EW, y + self.lh - 8), fill=THEME['line_hl'])
            num = str(i + 1)
            d.text((self.x0 - 40 - self.small.getlength(num), y + 10), num,
                   font=self.small,
                   fill=THEME['gutter_on'] if i == cur else THEME['gutter'])
            x = self.x0
            for part, col in colorize(text, self.s.lines[i][0]):
                for chunk in re.findall(r'[\U0001F000-\U0010FFFF\u2600-\u27BF\u200D\uFE0F]+|[^\U0001F000-\U0010FFFF\u2600-\u27BF\u200D\uFE0F]+', part):
                    if is_emoji(chunk[0]):
                        e = self.emoji(chunk)
                        im.paste(e, (int(x), int(y + 2)), e)
                        x += e.width + 4
                    else:
                        d.text((x, y), chunk, font=self.font, fill=col)
                        x += self.font.getlength(chunk)
            if i == cur and (typing or int(t * 2.2) % 2 == 0):
                d.rectangle((x + 3, y + 2, x + 15, y + self.lh - 14),
                            fill=THEME['cursor'])
        im.paste(self.base.crop((0, 0, EW, 64)), (0, 0))   # الشريط فوق الكود المُزاح
        return im


# --------------------------------------------------------------- المشهد

DEFAULT_SCREEN = [(175, 720), (1075, 752), (1068, 1268), (168, 1312)]


def build_scene():
    """مكتب بإضاءة بنفسجية/برتقالية مع شاشة وكيبورد (مرسوم بالكود)."""
    sc = vgrad((SW, SH), (46, 30, 56), (92, 62, 98))
    sc = glow(sc, (SW * 0.02, SH * 0.58), (SW * 0.5, SH * 0.28), (1.0, 0.55, 0.3), 190)
    sc = glow(sc, (SW * 1.0, SH * 0.5), (SW * 0.45, SH * 0.3), (0.7, 0.45, 1.0), 150)
    sc = glow(sc, (SW * 0.5, SH * 0.3), (SW * 0.6, SH * 0.18), (1.0, 0.75, 0.9), 45)
    d = ImageDraw.Draw(sc)
    # المكتب
    desk_y = int(SH * 0.66)
    d.polygon([(0, desk_y - 40), (SW, desk_y - 90), (SW, SH), (0, SH)], fill=(112, 70, 52))
    d.polygon([(0, desk_y + 70), (SW, desk_y), (SW, SH), (0, SH)], fill=(34, 30, 38))
    # قاعدة الشاشة
    cx = sum(p[0] for p in DEFAULT_SCREEN) / 4
    d.polygon([(cx - 40, 1330), (cx + 40, 1325), (cx + 55, desk_y - 30), (cx - 55, desk_y - 25)],
              fill=(150, 140, 150))
    d.ellipse((cx - 210, desk_y - 75, cx + 210, desk_y + 25), fill=(170, 160, 168))
    d.ellipse((cx - 180, desk_y - 62, cx + 180, desk_y + 10), fill=(120, 112, 122))
    # إطار الشاشة
    q = DEFAULT_SCREEN
    pad = [(q[0][0] - 22, q[0][1] - 22), (q[1][0] + 22, q[1][1] - 22),
           (q[2][0] + 22, q[2][1] + 30), (q[3][0] - 22, q[3][1] + 30)]
    d.polygon(pad, fill=(24, 25, 30))
    d.line([pad[0], pad[1]], fill=(110, 100, 115), width=3)
    # كيبورد
    rows, ky = 5, int(SH * 0.8)
    for r in range(rows):
        y0 = ky + r * 78
        s = 1 + r * 0.06
        n = 14
        kw = SW * 0.9 * s / n
        x0 = SW / 2 - kw * n / 2
        for k in range(n):
            col = (150, 80, 78) if (r == 4 and 3 < k < 10) or (r + k) % 11 == 0 \
                else (40, 38, 48) if (k + r) % 4 else (150, 144, 156)
            d.rounded_rectangle((x0 + k * kw + 4, y0, x0 + (k + 1) * kw - 4, y0 + 68),
                                radius=10, fill=col)
            d.rounded_rectangle((x0 + k * kw + 4, y0 + 56, x0 + (k + 1) * kw - 4, y0 + 70),
                                radius=8, fill=tuple(int(c * 0.6) for c in col))
    return sc.filter(ImageFilter.GaussianBlur(1.2)), DEFAULT_SCREEN


def load_bg(path, screen):
    """صورة حقيقية (تغطية كاملة للمشهد) + تحويل نقاط الشاشة."""
    im = Image.open(path).convert('RGB')
    s = max(SW / im.width, SH / im.height)
    nw, nh = int(im.width * s), int(im.height * s)
    ox, oy = (nw - SW) / 2, (nh - SH) / 2
    im = im.resize((nw, nh), Image.LANCZOS).crop((ox, oy, ox + SW, oy + SH))
    pts = [(x * s - ox, y * s - oy) for x, y in screen]
    return im, pts


class Compositor:
    def __init__(self, scene, quad):
        self.scene = scene
        xs, ys = [p[0] for p in quad], [p[1] for p in quad]
        self.box = (int(min(xs)), int(min(ys)), int(math.ceil(max(xs))), int(math.ceil(max(ys))))
        bw, bh = self.box[2] - self.box[0], self.box[3] - self.box[1]
        self.bsize = (bw, bh)
        local = [(x - self.box[0], y - self.box[1]) for x, y in quad]
        self.coeffs = perspective_coeffs(local, [(0, 0), (EW, 0), (EW, EH), (0, EH)])
        mask = Image.new('L', self.bsize, 0)
        ImageDraw.Draw(mask).polygon(local, fill=255)
        self.mask = mask
        # لمعة خفيفة على الزجاج
        g = np.zeros((bh, bw), float)
        yy, xx = np.mgrid[:bh, :bw]
        band = (xx / bw) - (yy / bh) * 0.6
        g += np.clip(1 - np.abs(band - 0.25) / 0.18, 0, 1) * 16
        self.gloss = Image.fromarray(g.astype('uint8'), 'L')
        self.glow_cache = None

    def frame(self, editor_img):
        warped = editor_img.transform(self.bsize, Image.PERSPECTIVE, self.coeffs, Image.BICUBIC)
        warped = Image.composite(Image.new('RGB', self.bsize, (255, 255, 255)), warped, self.gloss)
        out = self.scene.copy()
        out.paste(warped, self.box[:2], self.mask)
        return out


def camera(scene, t, dur):
    """تقريب بطيء + اهتزاز يد خفيف."""
    z = OVER * (1 + 0.05 * ease(t / dur))
    cw, ch = SW / z, SH / z
    dx = 9 * math.sin(2 * math.pi * 0.21 * t) + 4 * math.sin(2 * math.pi * 0.57 * t + 1)
    dy = 7 * math.sin(2 * math.pi * 0.17 * t + 2) + 3 * math.sin(2 * math.pi * 0.71 * t)
    cx, cy = SW / 2 + dx, SH / 2 + dy - 20
    left = min(max(cx - cw / 2, 0), SW - cw)
    top = min(max(cy - ch / 2, 0), SH - ch)
    return scene.resize((W, H), Image.BICUBIC, box=(left, top, left + cw, top + ch))


# ------------------------------------------------------------ النصوص

def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0x200D, 0xFE0F)


def rich_text(text, size, color=(255, 255, 255)):
    """صورة RGBA لنص يدعم العربي (raqm) والإيموجي الملوّن."""
    font = ImageFont.truetype(find_font(SANS), size)
    epath = find_font(EMOJI)
    parts, buf, emo = [], '', False
    for ch in text:
        e = is_emoji(ch)
        if buf and e != emo:
            parts.append((buf, emo))
            buf = ''
        buf, emo = buf + ch, e
    if buf:
        parts.append((buf, emo))
    imgs = []
    for s, e in parts:
        if e and epath:
            ef = ImageFont.truetype(epath, 109)
            bb = (0, 0, int(ef.getlength(s)), 128)
            im = Image.new('RGBA', (bb[2] + 8, 136), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((0, 0), s, font=ef, embedded_color=True)
            k = size * 1.15 / 128
            im = im.resize((max(1, int(im.width * k)), max(1, int(136 * k))), Image.LANCZOS)
        else:
            bb = font.getbbox(s)
            im = Image.new('RGBA', (bb[2] + 12, int(size * 1.35)), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((4, 0), s, font=font, fill=color)
        imgs.append(im)
    w = sum(i.width for i in imgs)
    h = max(i.height for i in imgs)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    x = 0
    for i in imgs:
        out.alpha_composite(i, (x, (h - i.height) // 2))
        x += i.width
    return out


def with_shadow(img, radius=6, alpha=200):
    pad = radius * 3
    sh = Image.new('RGBA', (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * alpha // 255)
    blk = Image.new('RGBA', img.size, (0, 0, 0, 255))
    blk.putalpha(a)
    sh.alpha_composite(blk, (pad, pad + 3))
    sh = sh.filter(ImageFilter.GaussianBlur(radius))
    sh.alpha_composite(img, (pad, pad))
    return sh


def overlays(script):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if script.title:
        t = rich_text(script.title, 66)
        if t.width > W - 80:
            t = t.resize((W - 80, int(t.height * (W - 80) / t.width)), Image.LANCZOS)
        t = with_shadow(t)
        layer.alpha_composite(t, ((W - t.width) // 2, 300))
    if script.handle:
        h = with_shadow(rich_text(script.handle, 32), 4, 160)
        layer.alpha_composite(h, (W - h.width - 70, 430))
    # تعتيم الأطراف (فينيت)
    yy, xx = np.mgrid[:H, :W]
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    vig = (np.clip(d - 0.55, 0, 1) * 230).astype('uint8')
    v = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    v.putalpha(Image.fromarray(vig, 'L'))
    v.alpha_composite(layer)
    return v


# --------------------------------------------------------------- الصوت

def click_track(script, path, sr=44100, seed=3):
    rnd = np.random.default_rng(seed)
    n = int(script.duration * sr) + sr
    out = np.zeros(n, np.float32)
    for t, ch in script.key_times():
        L = int(sr * (0.05 if ch == ' ' else 0.03))
        env = np.exp(-np.linspace(0, 9 if ch == ' ' else 12, L))
        noise = rnd.standard_normal(L)
        noise = np.convolve(noise, np.ones(4 if ch == ' ' else 2) / 3, 'same')
        thock = np.sin(2 * np.pi * (180 if ch == ' ' else 320 + rnd.random() * 120)
                       * np.arange(L) / sr) * 0.6
        amp = (0.5 if ch == ' ' else 0.32) * (0.75 + rnd.random() * 0.5)
        s = int(t * sr)
        if s + L < n:
            out[s:s + L] += ((noise * 0.6 + thock) * env * amp).astype(np.float32)
    out = np.clip(out, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((out * 32000).astype('<i2').tobytes())


# ---------------------------------------------------------------- التشغيل

def main():
    ap = argparse.ArgumentParser(description='مونتاج كتابة الكود على الشاشة')
    ap.add_argument('script', help='ملف JSON للأسطر والتوقيت')
    ap.add_argument('-o', '--out', default='reel.mp4')
    ap.add_argument('--bg', help='صورة حقيقية لمكتبك/شاشتك')
    ap.add_argument('--screen', help='زوايا الشاشة في الصورة: x1,y1,...,x4,y4 '
                    '(أعلى يسار، أعلى يمين، أسفل يمين، أسفل يسار)')
    ap.add_argument('--music', help='ملف موسيقى يُدمج مع صوت الكيبورد')
    ap.add_argument('--music-start', type=float, default=0, help='بداية المقطع من الأغنية (ثوانٍ)')
    ap.add_argument('--music-volume', type=float, default=0.9)
    ap.add_argument('--clicks-volume', type=float, default=0.8)
    ap.add_argument('--no-clicks', action='store_true')
    ap.add_argument('--preview', type=float, help='احفظ إطاراً واحداً عند هذه الثانية (PNG)')
    a = ap.parse_args()

    with open(a.script, encoding='utf-8') as f:
        script = Script(json.load(f))

    if a.bg:
        if not a.screen:
            sys.exit('--bg يحتاج --screen بزوايا الشاشة الأربع')
        nums = [float(v) for v in a.screen.split(',')]
        scene, quad = load_bg(a.bg, list(zip(nums[0::2], nums[1::2])))
    else:
        scene, quad = build_scene()

    editor = Editor(script)
    comp = Compositor(scene, quad)
    over = overlays(script)

    def frame_at(t):
        f = camera(comp.frame(editor.render(t)), t, script.duration).convert('RGBA')
        f.alpha_composite(over)
        return f.convert('RGB')

    if a.preview is not None:
        frame_at(a.preview).save(a.out)
        print('✓', a.out)
        return

    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, 'clicks.wav')
    click_track(script, wav)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(script.fps), '-i', '-', '-i', wav]
    if a.music:
        cmd += ['-ss', str(a.music_start), '-i', a.music]
    cv = 0 if a.no_clicks else a.clicks_volume
    if a.music:
        fc = (f'[1:a]volume={cv}[c];[2:a]volume={a.music_volume},'
              f'afade=t=out:st={script.duration - 1.2}:d=1.2[m];'
              '[c][m]amix=inputs=2:duration=longest:normalize=0[a]')
    else:
        fc = f'[1:a]volume={cv}[a]'
    cmd += ['-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-t', str(script.duration),
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', a.out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(script.duration * script.fps)
    for i in range(total):
        p.stdin.write(frame_at(i / script.fps).tobytes())
        if i % script.fps == 0:
            print(f'\r{i * 100 // total}%', end='', flush=True)
    p.stdin.close()
    p.wait()
    print('\r✓', a.out, f'({script.duration:.1f}s)')


if __name__ == '__main__':
    main()
