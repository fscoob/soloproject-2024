#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
code_typer.py — مونتاج «كأنه يكتب الكود» (Motion v1)
=====================================================
يولّد ريل عمودي 9:16 تُكتب فيه أسطر كود حرفاً حرفاً، مع:
  - تلوين الكود (HTML / CSS / JS / SQL) وأرقام الأسطر ومؤشر يومض
  - عدة ملفات بتبويبات (index.html ← style.css ← app.js …) وطرفية terminal
  - نهاية تعرض الموقع الناتج يتمرّر داخل المتصفح (result)
  - وضعين: "desk" شاشة على مكتب، أو "plain" نافذة محرر على خلفية سوداء
  - عنوان أعلى الفيديو (يدعم العربي والإيموجي) وحركة كاميرا خفيفة
  - صوت نقرات كيبورد متزامن، ودمج موسيقى اختيارياً

المتطلبات: Python 3 + Pillow + numpy + ffmpeg

أمثلة:
  python3 code_typer.py example.json -o reel.mp4
  python3 code_typer.py fahad.json -o reel.mp4 --music song.mp3 --music-start 62
  python3 code_typer.py fahad.json --preview 6.5 -o frame.png
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
OX, OY = (SW - W) / 2, (SH - H) / 2

THEME = {
    'bg': (22, 27, 38), 'tabbar': (16, 20, 29), 'tab': (30, 37, 51),
    'line_hl': (34, 43, 60), 'gutter': (88, 98, 118), 'gutter_on': (190, 198, 214),
    'text': (214, 222, 235), 'punct': (176, 186, 204), 'keyword': (255, 92, 138),
    'func': (111, 195, 255), 'prop': (246, 208, 107), 'string': (165, 214, 138),
    'number': (242, 163, 58), 'comment': (120, 132, 154), 'cursor': (255, 79, 123),
    'title': (255, 255, 255), 'handle': (255, 255, 255),
    'backdrop': (8, 10, 10), 'glow': (40, 80, 70), 'glow2': (60, 50, 30),
}
KEYWORDS = set('''if else while for return const let var new true false null
undefined function await async break continue try catch throw class import
from export def in of not and or self this require
CREATE TABLE PRIMARY KEY NOT NULL TEXT INTEGER DEFAULT INSERT INTO VALUES
SELECT FROM WHERE ORDER BY DESC LIMIT INDEX EXISTS IF AUTOINCREMENT DATABASE USE
VARCHAR DECIMAL INT FOREIGN REFERENCES JOIN LEFT INNER ON AS GROUP HAVING AND OR'''.split())
FILE_COLORS = {'.html': (228, 112, 74), '.css': (86, 156, 214), '.js': (241, 212, 76),
               '.sql': (120, 200, 150), '.py': (90, 150, 220), '': (150, 160, 175)}

MONO = ['JetBrainsMono-SemiBold.ttf', 'JetBrainsMono-Bold.ttf', 'Menlo.ttc',
        'DejaVuSansMono-Bold.ttf', 'Consolas.ttf', 'Courier New Bold.ttf']
SANS = ['IBMPlexSansArabic-700.ttf', 'DejaVuSans-Bold.ttf', 'Arial Bold.ttf', 'Helvetica.ttc',
        'FreeSansBold.ttf', 'Arial.ttf']
ARABIC = ['IBMPlexSansArabic-500.ttf', 'DejaVuSans.ttf', 'GeezaPro.ttc', 'Arial.ttf', 'Tahoma.ttf']
EMOJI = ['NotoColorEmoji.ttf', 'Apple Color Emoji.ttc']
FONT_DIRS = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts'),
             '/usr/share/fonts', '/Library/Fonts', '/System/Library/Fonts',
             os.path.expanduser('~/Library/Fonts'), 'C:/Windows/Fonts']
_font_cache = {}


def find_font(names):
    key = tuple(names)
    if key not in _font_cache:
        _font_cache[key] = None
        for d in FONT_DIRS:
            for root, _, files in os.walk(d):
                hit = next((n for n in names if n in files), None)
                if hit:
                    _font_cache[key] = os.path.join(root, hit)
                    break
            if _font_cache[key]:
                break
    return _font_cache[key]


def hex_rgb(v):
    if isinstance(v, (list, tuple)):
        return tuple(v)
    v = v.lstrip('#')
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


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


EMOJI_RE = '\U0001F000-\U0010FFFF\u2600-\u27BF\u200D\uFE0F'
ARABIC_RE = '\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF'
RUNS = re.compile(f'[{EMOJI_RE}]+|[{ARABIC_RE}](?:[{ARABIC_RE} ]*[{ARABIC_RE}])?|[^{EMOJI_RE}{ARABIC_RE}]+')


def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0x200D, 0xFE0F)


def is_arabic(ch):
    return re.match(f'[{ARABIC_RE}]', ch) is not None


# ------------------------------------------------------------- السكربت

class Line:
    __slots__ = ('code', 'at', 'times', 'file', 'idx', 'silent')


class Show:
    """عرض نتيجة: pane=bottom (لوحة نتائج تحت الكود) أو full (يملأ النافذة)."""
    __slots__ = ('image', 'at', 'hold', 'pane', 'file', 'label', 'img',
                 'transition', 'out', 'sw_in', 'sw_out', 'full')


class Swarm:
    """تأثير Swarm Rebuild: الصورة A تتفكك لسرب جزيئات يطير ثم يعيد بناء الصورة B."""

    def __init__(self, A, B, bg, accent, top=0, n=24000, seed=5):
        self.A = np.asarray(A, np.float32)
        self.B = np.asarray(B, np.float32)
        self.top = top
        self.bg = np.array(bg, np.float32)
        self.accent = np.array(accent, np.float32)
        h, w = self.A.shape[:2]
        self.h, self.w = h, w
        rnd = np.random.default_rng(seed)

        def pick(img):
            m = np.abs(img - self.bg).sum(-1) > 70
            m[:top] = False
            ys, xs = np.nonzero(m)
            if len(xs) == 0:
                ys, xs = np.array([h // 2]), np.array([w // 2])
            i = rnd.integers(0, len(xs), n)
            order = np.lexsort((xs[i], ys[i] // 24))     # ترتيب سطري لحركة منظّمة
            i = i[order]
            return np.stack([xs[i], ys[i]], 1).astype(np.float32), img[ys[i], xs[i]]

        self.p0, self.c0 = pick(self.A)
        self.p1, self.c1 = pick(self.B)
        self.delay = (self.p0[:, 1] / h) * 0.22 + rnd.random(n) * 0.08
        self.R = rnd.uniform(30, 220, n).astype(np.float32)
        self.th = rnd.uniform(0, 2 * np.pi, n).astype(np.float32)
        self.om = (rnd.uniform(2.5, 6, n) * rnd.choice([-1, 1], n)).astype(np.float32)
        self.size = rnd.choice([2, 2, 3], n)

    def frame(self, u):
        u = min(1.0, max(0.0, u))
        fa = ease(u / 0.25)                       # A يختفي
        fb = ease((u - 0.72) / 0.28)              # B يظهر
        out = self.A * (1 - fa) + self.bg * fa
        out = out * (1 - fb) + self.B * fb
        v = np.clip((u - self.delay) / 0.68, 0, 1)
        e = 0.5 - 0.5 * np.cos(np.pi * v)
        fl = np.sin(np.pi * v)
        ang = self.th + self.om * v
        x = self.p0[:, 0] * (1 - e) + self.p1[:, 0] * e + fl * self.R * np.cos(ang)
        y = self.p0[:, 1] * (1 - e) + self.p1[:, 1] * e + fl * self.R * np.sin(ang) * 0.7
        col = self.c0 * (1 - e)[:, None] + self.c1 * e[:, None]
        col = col * (1 - 0.55 * fl)[:, None] + self.accent * (0.55 * fl)[:, None]
        vis = (fb < 0.999) & (v > 0) & (v < 1) | ((v >= 1) & (fb < 0.9)) | ((v <= 0) & (fa > 0.05))
        xi = x[vis].astype(int)
        yi = y[vis].astype(int)
        c = col[vis]
        sz = self.size[vis]
        for dx in (0, 1, 2):
            for dy in (0, 1, 2):
                k = (dx < sz) & (dy < sz)
                xx, yy = xi[k] + dx, yi[k] + dy
                ok = (xx >= 0) & (xx < self.w) & (yy >= self.top) & (yy < self.h)
                out[yy[ok], xx[ok]] = c[k][ok]
        img = out.clip(0, 255).astype(np.uint8)
        img[:self.top] = (self.A if u < 0.5 else self.B)[:self.top].astype(np.uint8)
        return Image.fromarray(img, 'RGB')


class Script:
    """يقرأ ملف JSON. كل سطر: code + (اختياري) file, at, type, instant."""

    def __init__(self, data, base_dir='.', seed=7):
        self.title = data.get('title', '')
        self.handle = data.get('handle', '')
        self.fps = int(data.get('fps', 30))
        self.mode = data.get('mode', 'desk')
        self.theme = dict(THEME)
        for k, v in data.get('theme', {}).items():
            self.theme[k] = hex_rgb(v)
        cps = float(data.get('char_time', 0.06))
        gap = float(data.get('gap', 0.25))
        pause = float(data.get('file_pause', 0.8))
        rnd = random.Random(seed)
        file = data.get('file', 'main.js')
        t = float(data.get('start', 0.4))
        self.lines, self.files, counts = [], [], {}
        self.shows = []
        for ln in data['lines']:
            if 'show' in ln:
                S = Show()
                S.image = os.path.join(base_dir, ln['show'])
                S.pane = ln.get('pane', 'bottom')
                S.at = float(ln['at']) if 'at' in ln else t + float(ln.get('delay', 0.35))
                S.hold = float(ln.get('hold', 2.0 if S.pane == 'bottom' else 3.5))
                S.file, S.label = file, ln.get('label', 'Results')
                S.transition = ln.get('transition', 'fade')
                S.out = ln.get('out', True)
                S.sw_in = S.sw_out = S.full = None
                self.shows.append(S)
                t = S.at + S.hold
                continue
            f = ln.get('file', file)
            if f != file and self.lines:
                t += pause
            file = f
            if f not in self.files:
                self.files.append(f)
            code = ln.get('code', '')
            at = float(ln['at']) if 'at' in ln else t
            if ln.get('instant'):
                dur = 0.01
            else:
                dur = float(ln['type']) if 'type' in ln else max(0.12, len(code) * cps)
            times, n = [], max(1, len(code))
            for i in range(len(code)):
                jitter = (rnd.random() - 0.5) * (dur / n) * 0.9
                ti = at + dur * i / n + jitter
                times.append(max(at, ti if not times else max(times[-1] + 0.004, ti)))
            L = Line()
            L.code, L.at, L.times, L.file = code, at, times, f
            L.idx = counts.get(f, 0)
            L.silent = bool(ln.get('instant'))
            counts[f] = L.idx + 1
            self.lines.append(L)
            t = max((times[-1] if times else at), at) + gap + float(ln.get('pause', 0))
        self.result = None
        res = data.get('result')
        if res:
            img = os.path.join(base_dir, res['image'])
            at = float(res.get('at', t + 0.5))
            self.result = {'image': img, 'at': at, 'hold': float(res.get('hold', 7)),
                           'url': res.get('url', 'localhost:3000')}
            self.duration = at + self.result['hold']
        elif self.shows and not self.shows[-1].out:
            self.duration = self.shows[-1].at + self.shows[-1].hold   # الختام يبقى حتى النهاية
        else:
            self.duration = float(data.get('duration', t + 2.5))
        if 'duration' in data:
            self.duration = float(data['duration'])

    def state(self, t):
        """الملف الحالي، الأسطر الظاهرة منه، رقم السطر الحالي، وهل يكتب الآن."""
        cur = None
        for L in self.lines:
            if L.at <= t:
                cur = L
            else:
                break
        if cur is None:
            return (self.lines[0].file if self.lines else ''), [], -1, False
        shown, typing = [], False
        for L in self.lines:
            if L.file != cur.file or L.at > t:
                continue
            k = bisect.bisect_right(L.times, t)
            shown.append((L.code[:k], L.code))
            if k < len(L.code) or (L.times and t - L.times[-1] < 0.35):
                typing = True
        return cur.file, shown, cur.idx, typing

    def open_files(self, t):
        seen = []
        for L in self.lines:
            if L.at <= t and L.file not in seen:
                seen.append(L.file)
        return seen or self.files[:1]

    def key_times(self):
        out = []
        for L in self.lines:
            if not L.silent:
                out += [(t, L.code[i]) for i, t in enumerate(L.times)]
        return out


# ---------------------------------------------------------- تلوين الكود

TOKEN = re.compile(
    r'(?P<comment>//.*|<!--.*|/\*.*|--\s.*|^\s*-- .*)'
    r'|(?P<string>"[^"]*"?|\'[^\']*\'?|`[^`]*`?)'
    r'|(?P<number>#[0-9A-Fa-f]{3,8}\b|\b\d+(?:\.\d+)?(?:px|em|rem|vw|vh|%|s|ms)?\b)'
    r'|(?P<ident>-{0,2}[A-Za-z_$][\w$-]*)'
    rf'|(?P<arabic>[{ARABIC_RE}](?:[{ARABIC_RE} ]*[{ARABIC_RE}])?)'
    r'|(?P<space>\s+)|(?P<other>.)')


def colorize(code, full, th):
    """تقسيم السطر لأجزاء ملوّنة. full = السطر كاملاً لمعرفة ما يليه."""
    out, depth, first = [], 0, True
    for m in TOKEN.finditer(code):
        kind, s = m.lastgroup, m.group()
        if kind == 'ident':
            rest = full[m.end():].lstrip()
            nxt = rest[:1]
            prev = code[:m.start()].rstrip()[-2:]
            if s in KEYWORDS or prev.endswith('<') or prev == '</':
                col = th['keyword']
            elif s.startswith('--') or nxt == ':' and depth == 0 and '{' not in code:
                col = th['prop']
            elif nxt == '(':
                col = th['func']
            elif nxt == '=' and rest[:2] != '==' or (first and nxt == '.'):
                col = th['keyword'] if first and nxt == '.' else th['prop']
            elif prev.endswith('.') or depth > 0:
                col = th['prop']
            else:
                col = th['text']
            first = False
        elif kind == 'other':
            depth += s in '([{'
            depth -= s in ')]}' and depth > 0
            col = th['punct']
        elif kind in ('space', 'arabic'):
            col = th['text']
        else:
            col = th[kind]
        out.append((s, col))
    return out


class Editor:
    """يرسم صورة المحرر (أو المتصفح في النهاية) لأي لحظة t."""

    def __init__(self, script, size, font_size, chrome=False):
        self.s, self.th = script, script.theme
        self.w, self.h = size
        k = font_size / 46
        self.font = ImageFont.truetype(find_font(MONO), font_size)
        self.small = ImageFont.truetype(find_font(MONO), int(28 * k))
        self.arabic = ImageFont.truetype(find_font(ARABIC) or find_font(SANS), font_size)
        self.tab_h = int(66 * k)
        self.top, self.lh, self.x0 = int(self.tab_h + 30 * k), int(70 * k), int(130 * k)
        self.pad = int(26 * k)
        self.k = k
        self.chrome = chrome
        self.rows = (self.h - self.top - 30) // self.lh
        self._emoji = {}
        for S in script.shows:
            im = Image.open(S.image).convert('RGB')
            if im.width != self.w:
                im = im.resize((self.w, int(im.height * self.w / im.width)), Image.LANCZOS)
            S.img = im
        self.page = None
        if script.result:
            pg = Image.open(script.result['image']).convert('RGB')
            pw = self.w
            self.page = pg.resize((pw, int(pg.height * pw / pg.width)), Image.LANCZOS)

    def emoji(self, s):
        if s not in self._emoji:
            self._emoji[s] = rich_text(s, int(40 * self.k))
        return self._emoji[s]

    # ---- شريط التبويبات
    def tabbar(self, d, files, active, url=None):
        th, k = self.th, self.k
        d.rectangle((0, 0, self.w, self.tab_h), fill=th['tabbar'])
        x = int(28 * k)
        if self.chrome:
            for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
                cx = x + i * int(30 * k)
                r = int(9 * k)
                d.ellipse((cx - r, self.tab_h / 2 - r, cx + r, self.tab_h / 2 + r), fill=c)
            x += int(100 * k)
        if url is None and getattr(self, '_run', False):
            lbl = '▶ Run'
            tw = self.small.getlength(lbl) + 30 * k
            d.rounded_rectangle((self.w - tw - 20 * k, 12 * k, self.w - 20 * k, self.tab_h - 12 * k),
                                radius=int(16 * k), fill=(40, 160, 90))
            d.text((self.w - tw - 5 * k, 17 * k), lbl, font=self.small, fill=(255, 255, 255))
        if url:
            d.rounded_rectangle((x, int(12 * k), self.w - int(28 * k), self.tab_h - int(12 * k)),
                                radius=int(20 * k), fill=th['tab'])
            d.text((x + int(24 * k), int(18 * k)), url,
                   font=self.small, fill=th['text'])
            return
        widths = [int(self.small.getlength(f) + 70 * k) for f in files]
        if active in files:
            i = files.index(active)
            end = x + sum(w + int(6 * k) for w in widths[:i + 1])
            x -= max(0, end - (self.w - int(20 * k)))
        start = x
        for f, tw in zip(files, widths):
            ext = os.path.splitext(f)[1]
            on = f == active
            if on:
                d.rectangle((x, int(8 * k), x + tw, self.tab_h), fill=th['bg'])
                d.rectangle((x, int(8 * k), x + tw, int(12 * k)), fill=th['cursor'])
            d.rectangle((x + int(18 * k), int(26 * k), x + int(30 * k), int(44 * k)),
                        fill=FILE_COLORS.get(ext, FILE_COLORS['']))
            d.text((x + int(40 * k), int(19 * k)), f, font=self.small,
                   fill=th['text'] if on else th['gutter'])
            x += tw + int(6 * k)
        if self.chrome and start < int(128 * k):
            d.rectangle((0, 0, int(118 * k), self.tab_h), fill=th['tabbar'])
            for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
                cx, r = int(28 * k) + i * int(30 * k), int(9 * k)
                d.ellipse((cx - r, self.tab_h / 2 - r, cx + r, self.tab_h / 2 + r), fill=c)

    def scroll(self, t, file, rows):
        """إزاحة ناعمة تُبقي السطر الحالي ظاهراً فوق لوحة النتائج."""
        cur = None
        for L in self.s.lines:
            if L.file == file and L.at <= t:
                cur = L
        if cur is None:
            return 0.0
        pos = cur.idx - 1 + ease((t - cur.at) / 0.25)
        return max(0.0, pos + 2.2 - rows)

    def bottom_show(self, t, file):
        """آخر نتيجة سفلية في نفس الملف + نسبة ظهور اللوحة."""
        act, first = None, None
        for S in self.s.shows:
            if S.pane == 'bottom' and S.file == file and S.at <= t:
                act = S
                if first is None:
                    first = S
        if act is None:
            return None, 0.0
        return act, ease((t - first.at) / 0.35)

    def full_show(self, t):
        for S in self.s.shows:
            if S.pane == 'full' and S.at <= t < S.at + S.hold:
                a = ease((t - S.at) / 0.4)
                if S.out:
                    a = min(a, ease((S.at + S.hold - t) / 0.4))
                return S, a
        return None, 0.0

    def draw_text(self, im, d, x, y, text, col):
        for run in RUNS.findall(text):
            if is_emoji(run[0]):
                e = self.emoji(run)
                im.paste(e, (int(x), int(y + 2 * self.k)), e)
                x += e.width + 4
            elif is_arabic(run[0]):
                d.text((x, y - 6 * self.k), run, font=self.arabic, fill=col, direction='rtl')
                x += self.arabic.getlength(run, direction='rtl')
            else:
                d.text((x, y), run, font=self.font, fill=col)
                x += self.font.getlength(run)
        return x

    def code_view(self, t):
        th = self.th
        im = Image.new('RGB', (self.w, self.h), th['bg'])
        d = ImageDraw.Draw(im)
        file, shown, cur, typing = self.s.state(t)
        term = file == 'terminal'
        show, pa = self.bottom_show(t, file)
        panel_h = 0
        if show is not None:
            panel_h = int(min(show.img.height, self.h * 0.55) * pa)
        rows = (self.h - panel_h - self.top - 20) / self.lh
        off = self.scroll(t, file, rows)
        x0 = self.pad if term else self.x0
        for i, (text, full) in enumerate(shown):
            y = self.top + (i - off) * self.lh
            if y < self.tab_h - self.lh or y > self.h:
                continue
            if i == cur and not term:
                d.rectangle((0, y - 8 * self.k, self.w, y + self.lh - 8 * self.k),
                            fill=th['line_hl'])
            if not term:
                num = str(i + 1)
                d.text((self.x0 - 40 * self.k - self.small.getlength(num), y + 10 * self.k),
                       num, font=self.small,
                       fill=th['gutter_on'] if i == cur else th['gutter'])
                parts = colorize(text, full, th)
            elif full.startswith('$'):
                parts = [(text[:1], th['string']), (text[1:], th['text'])]
            else:
                parts = [(text, th['string'] if full.strip() else th['text'])]
            x = x0
            for part, col in parts:
                x = self.draw_text(im, d, x, y, part, col)
            if i == cur and (typing or int(t * 2.2) % 2 == 0):
                d.rectangle((x + 3, y + 2, x + 3 + 12 * self.k, y + self.lh - 14 * self.k),
                            fill=th['cursor'])
        if panel_h:
            ph = int(min(show.img.height, self.h * 0.55))
            y0 = self.h - panel_h
            im.paste(show.img.crop((0, 0, self.w, ph)), (0, y0))
            d.line((0, y0, self.w, y0), fill=th['cursor'], width=max(2, int(3 * self.k)))
        self._run = any(S.file == file and S.at - 0.35 <= t < S.at + 0.15 for S in self.s.shows)
        self.tabbar(d, self.s.open_files(t), file)
        self._run = False
        return im

    def browser_view(self, t):
        r = self.s.result
        im = Image.new('RGB', (self.w, self.h), (255, 255, 255))
        view_h = self.h - self.tab_h
        span = max(0, self.page.height - view_h)
        start, end = r['at'] + 1.2, r['at'] + r['hold'] - 1.0
        y = span * ease((t - start) / max(0.1, end - start))
        im.paste(self.page.crop((0, int(y), self.w, int(y) + view_h)), (0, self.tab_h))
        self.tabbar(ImageDraw.Draw(im), [], None, url=r['url'])
        return im

    def full_view(self, S):
        im = Image.new('RGB', (self.w, self.h), self.th['bg'])
        im.paste(S.img.crop((0, 0, self.w, self.h - self.tab_h)), (0, self.tab_h))
        self.tabbar(ImageDraw.Draw(im), [S.label], S.label)
        return im

    def swarm_view(self, S, t, tin=1.6, tout=1.3):
        if S.full is None:
            S.full = self.full_view(S)
        args = (self.th['bg'], self.th['cursor'], self.tab_h)
        if t < S.at + tin:
            if S.sw_in is None:
                S.sw_in = Swarm(self.code_view(S.at - 0.01), S.full, *args)
            return S.sw_in.frame((t - S.at) / tin)
        if S.out and t > S.at + S.hold - tout:
            if S.sw_out is None:
                S.sw_out = Swarm(S.full, self.code_view(S.at + S.hold + 0.01), *args, seed=9)
            return S.sw_out.frame((t - (S.at + S.hold - tout)) / tout)
        return S.full

    def render(self, t):
        r = self.s.result
        S, fa = self.full_show(t)
        if S is not None and S.transition == 'swarm':
            return self.swarm_view(S, t)
        if S is not None:
            base = self.code_view(t)
            return Image.blend(base, self.full_view(S), fa) if fa < 1 else self.full_view(S)
        if not r or t < r['at']:
            return self.code_view(t)
        a = ease((t - r['at']) / 0.6)
        b = self.browser_view(t)
        return b if a >= 1 else Image.blend(self.code_view(t), b, a)


# --------------------------------------------------------------- المشهد

DEFAULT_SCREEN = [(175, 720), (1075, 752), (1068, 1268), (168, 1312)]


def build_desk():
    """مكتب بإضاءة بنفسجية/برتقالية مع شاشة وكيبورد (مرسوم بالكود)."""
    sc = vgrad((SW, SH), (46, 30, 56), (92, 62, 98))
    sc = glow(sc, (SW * 0.02, SH * 0.58), (SW * 0.5, SH * 0.28), (1.0, 0.55, 0.3), 190)
    sc = glow(sc, (SW * 1.0, SH * 0.5), (SW * 0.45, SH * 0.3), (0.7, 0.45, 1.0), 150)
    sc = glow(sc, (SW * 0.5, SH * 0.3), (SW * 0.6, SH * 0.18), (1.0, 0.75, 0.9), 45)
    d = ImageDraw.Draw(sc)
    desk_y = int(SH * 0.66)
    d.polygon([(0, desk_y - 40), (SW, desk_y - 90), (SW, SH), (0, SH)], fill=(112, 70, 52))
    d.polygon([(0, desk_y + 70), (SW, desk_y), (SW, SH), (0, SH)], fill=(34, 30, 38))
    cx = sum(p[0] for p in DEFAULT_SCREEN) / 4
    d.polygon([(cx - 40, 1330), (cx + 40, 1325), (cx + 55, desk_y - 30), (cx - 55, desk_y - 25)],
              fill=(150, 140, 150))
    d.ellipse((cx - 210, desk_y - 75, cx + 210, desk_y + 25), fill=(170, 160, 168))
    d.ellipse((cx - 180, desk_y - 62, cx + 180, desk_y + 10), fill=(120, 112, 122))
    q = DEFAULT_SCREEN
    pad = [(q[0][0] - 22, q[0][1] - 22), (q[1][0] + 22, q[1][1] - 22),
           (q[2][0] + 22, q[2][1] + 30), (q[3][0] - 22, q[3][1] + 30)]
    d.polygon(pad, fill=(24, 25, 30))
    d.line([pad[0], pad[1]], fill=(110, 100, 115), width=3)
    ky = int(SH * 0.8)
    for r in range(5):
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
    return sc.filter(ImageFilter.GaussianBlur(1.2)), DEFAULT_SCREEN, 0


PLAIN_WIN = (44, 400, W - 44, 1660)   # موضع النافذة في الإطار النهائي


def build_plain(th):
    """خلفية سوداء بتوهج خفيف من ألوان الهوية + ظل للنافذة."""
    sc = Image.new('RGB', (SW, SH), th['backdrop'])
    sc = glow(sc, (SW * 0.5, SH * 0.55), (SW * 0.9, SH * 0.5), tuple(c / 255 for c in th['glow']), 255)
    sc = glow(sc, (SW * 0.5, SH * 0.12), (SW * 0.8, SH * 0.2), tuple(c / 255 for c in th['glow2']), 255)
    x0, y0, x1, y1 = (PLAIN_WIN[0] + OX, PLAIN_WIN[1] + OY, PLAIN_WIN[2] + OX, PLAIN_WIN[3] + OY)
    sh = Image.new('L', (SW, SH), 0)
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 30, x1, y1 + 40), radius=40, fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(40))
    sc = Image.composite(Image.new('RGB', (SW, SH), (0, 0, 0)), sc, sh)
    quad = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return sc, quad, 28


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
    def __init__(self, scene, quad, tex_size, radius=0, gloss=True):
        self.scene = scene
        xs, ys = [p[0] for p in quad], [p[1] for p in quad]
        self.box = (int(min(xs)), int(min(ys)), int(math.ceil(max(xs))), int(math.ceil(max(ys))))
        bw, bh = self.box[2] - self.box[0], self.box[3] - self.box[1]
        self.bsize = (bw, bh)
        tw, th = tex_size
        local = [(x - self.box[0], y - self.box[1]) for x, y in quad]
        self.coeffs = perspective_coeffs(local, [(0, 0), (tw, 0), (tw, th), (0, th)])
        mask = Image.new('L', self.bsize, 0)
        md = ImageDraw.Draw(mask)
        if radius:
            md.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=radius, fill=255)
        else:
            md.polygon(local, fill=255)
        self.mask = mask
        self.gloss = None
        if gloss:
            yy, xx = np.mgrid[:bh, :bw]
            band = (xx / bw) - (yy / bh) * 0.6
            g = np.clip(1 - np.abs(band - 0.25) / 0.18, 0, 1) * 16
            self.gloss = Image.fromarray(g.astype('uint8'), 'L')

    def frame(self, tex):
        warped = tex.transform(self.bsize, Image.PERSPECTIVE, self.coeffs, Image.BICUBIC)
        if self.gloss is not None:
            warped = Image.composite(Image.new('RGB', self.bsize, (255, 255, 255)), warped, self.gloss)
        out = self.scene.copy()
        out.paste(warped, self.box[:2], self.mask)
        return out


def camera(scene, t, dur, push=0.05):
    """تقريب بطيء + اهتزاز يد خفيف."""
    z = OVER * (1 + push * ease(t / dur))
    cw, ch = SW / z, SH / z
    dx = 9 * math.sin(2 * math.pi * 0.21 * t) + 4 * math.sin(2 * math.pi * 0.57 * t + 1)
    dy = 7 * math.sin(2 * math.pi * 0.17 * t + 2) + 3 * math.sin(2 * math.pi * 0.71 * t)
    cx, cy = SW / 2 + dx, SH / 2 + dy - 20
    left = min(max(cx - cw / 2, 0), SW - cw)
    top = min(max(cy - ch / 2, 0), SH - ch)
    return scene.resize((W, H), Image.BICUBIC, box=(left, top, left + cw, top + ch))


# ------------------------------------------------------------ النصوص

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
    if sum(map(is_arabic, text)) > len(text) / 3:
        parts.reverse()          # جملة عربية: الإيموجي في نهايتها (يساراً)
    imgs = []
    for s, e in parts:
        if e and epath:
            ef = ImageFont.truetype(epath, 109)
            im = Image.new('RGBA', (int(ef.getlength(s)) + 8, 136), (0, 0, 0, 0))
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
    th = script.theme
    plain = script.mode == 'plain'
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if script.title:
        t = rich_text(script.title, 66, th['title'])
        if t.width > W - 80:
            t = t.resize((W - 80, int(t.height * (W - 80) / t.width)), Image.LANCZOS)
        t = with_shadow(t)
        layer.alpha_composite(t, ((W - t.width) // 2, 170 if plain else 300))
    if script.handle:
        h = with_shadow(rich_text(script.handle, 30 if plain else 32, th['handle']), 4, 160)
        pos = ((W - h.width) // 2, 285) if plain else (W - h.width - 70, 430)
        layer.alpha_composite(h, pos)
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
    ap.add_argument('--mode', choices=['desk', 'plain'], help='يتجاوز "mode" في السكربت')
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
        script = Script(json.load(f), os.path.dirname(os.path.abspath(a.script)))
    if a.mode:
        script.mode = a.mode

    if a.bg:
        if not a.screen:
            sys.exit('--bg يحتاج --screen بزوايا الشاشة الأربع')
        nums = [float(v) for v in a.screen.split(',')]
        scene, quad = load_bg(a.bg, list(zip(nums[0::2], nums[1::2])))
        radius, plain = 0, False
    elif script.mode == 'plain':
        scene, quad, radius = build_plain(script.theme)
        plain = True
    else:
        scene, quad, radius = build_desk()
        plain = False

    if plain:
        tex = (int(quad[1][0] - quad[0][0]), int(quad[2][1] - quad[1][1]))
        editor = Editor(script, tex, int(34 * OVER), chrome=True)
    else:
        tex = (1600, 900)
        editor = Editor(script, tex, 46)
    comp = Compositor(scene, quad, tex, radius=radius, gloss=not plain)
    over = overlays(script)

    def frame_at(t):
        f = camera(comp.frame(editor.render(t)), t, script.duration,
                   push=0.03 if plain else 0.05).convert('RGBA')
        f.alpha_composite(over)
        return f.convert('RGB')

    if a.preview is not None:
        frame_at(a.preview).save(a.out)
        print('✓', a.out, f'(المدة الكلية {script.duration:.1f}s)')
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
              '[c][m]amix=inputs=2:duration=longest:normalize=0,'
              'loudnorm=I=-14:TP=-1.5:LRA=11[a]')
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
