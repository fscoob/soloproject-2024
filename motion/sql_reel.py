#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sql_reel.py — ريل SQL: قاعدة بيانات شركة (أقسام ← إدارات ← موظفين)
====================================================================
1) ينفّذ كل خطوة SQL فعلياً على قاعدة SQLite حقيقية
2) يرسم نتيجة كل خطوة كصورة (رسالة / بنية جدول / جدول نتائج / مخطط علاقات ER)
3) يكتب ملف sql.json جاهز لـ code_typer.py

  python3 sql_reel.py                    # يجهّز assets/sql/*.png و sql.json
  python3 lofi.py --style energetic -o assets/sql/music.wav --seconds 75
  python3 code_typer.py sql.json -o sql_reel.mp4 --music assets/sql/music.wav

الكود المكتوب بصيغة SQL قياسية تشتغل على MySQL و PostgreSQL و SQL Server و SQLite
(ما عدا CREATE DATABASE / USE، وهذي يتجاوزها التنفيذ في SQLite ويعرض رسالتها).
"""

import json
import os
import sqlite3
import time

from PIL import Image, ImageDraw, ImageFont

from code_typer import ARABIC, MONO, find_font, is_arabic, hex_rgb

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets', 'sql')
WIDTH = 992                 # = عرض نافذة المحرر في code_typer (وضع plain)
FULL_H = 1260 - 56          # ارتفاع النافذة ناقص شريط التبويبات

C = {k: hex_rgb(v) for k, v in {
    'bg': '#0C1513', 'head': '#18262A', 'row': '#0F1A17', 'row2': '#132220',
    'line': '#22332F', 'gold': '#C8A45D', 'text': '#D6DEEB', 'muted': '#7F8D99',
    'ok': '#5BD18B', 'pk': '#C8A45D', 'fk': '#6FC3FF', 'green': '#123A31'}.items()}

F_MONO = ImageFont.truetype(find_font(MONO), 25)
F_MONO_S = ImageFont.truetype(find_font(MONO), 21)
F_AR = ImageFont.truetype(find_font(ARABIC), 25)
F_TITLE = ImageFont.truetype(find_font(MONO), 30)
F_AR_T = ImageFont.truetype(find_font(ARABIC), 30)


# ------------------------------------------------------------ الخطوات

BLOCKS = [
    dict(file='01_database.sql', code=[
        '-- 1) إنشاء قاعدة بيانات الشركة',
        'CREATE DATABASE company;',
        'USE company;',
    ], result=('msg', ['Query OK, 1 row affected', 'Database changed → company'])),

    dict(file='02_tables.sql', code=[
        '-- 2) جدول الأقسام',
        'CREATE TABLE departments (',
        '  id   INT PRIMARY KEY,',
        '  name VARCHAR(50) NOT NULL',
        ');',
    ], result=('schema', 'departments')),
    dict(file='02_tables.sql', code=[
        '',
        '-- 3) الإدارات داخل كل قسم',
        'CREATE TABLE divisions (',
        '  id   INT PRIMARY KEY,',
        '  name VARCHAR(50) NOT NULL,',
        '  department_id INT,',
        '  FOREIGN KEY (department_id)',
        '    REFERENCES departments(id)',
        ');',
    ], result=('schema', 'divisions')),
    dict(file='02_tables.sql', code=[
        '',
        '-- 4) الموظفين وبياناتهم',
        'CREATE TABLE employees (',
        '  id     INT PRIMARY KEY,',
        '  name   VARCHAR(50) NOT NULL,',
        '  job    VARCHAR(50),',
        '  salary DECIMAL(10,2),',
        '  division_id INT,',
        '  FOREIGN KEY (division_id)',
        '    REFERENCES divisions(id)',
        ');',
    ], result=('schema', 'employees')),
    dict(file=None, code=[], result=('er', None)),          # مخطط العلاقات

    dict(file='03_data.sql', code=[
        '-- 5) إدخال البيانات',
        'INSERT INTO departments VALUES',
        "  (1, 'تقنية المعلومات'),",
        "  (2, 'المالية'),",
        "  (3, 'الموارد البشرية');",
    ], result=('query', 'SELECT * FROM departments;')),
    dict(file='03_data.sql', code=[
        '',
        'INSERT INTO divisions VALUES',
        "  (1, 'البرمجة',  1),",
        "  (2, 'الشبكات',  1),",
        "  (3, 'الحسابات', 2),",
        "  (4, 'التوظيف',  3);",
    ], result=('query', 'SELECT * FROM divisions;')),
    dict(file='03_data.sql', code=[
        '',
        'INSERT INTO employees VALUES',
        "  (1, 'فهد',  'مطوّر',  12000, 1),",
        "  (2, 'سارة', 'مهندسة شبكات', 11000, 2),",
        "  (3, 'خالد', 'محاسب', 9500, 3),",
        "  (4, 'نورة', 'أخصائية توظيف', 9000, 4),",
        "  (5, 'ريم',  'مطوّرة', 12500, 1);",
    ], result=('query', 'SELECT * FROM employees;')),

    dict(file='04_join.sql', code=[
        '-- 6) الربط: مين يشتغل وين؟',
        'SELECT e.name,',
        '       v.name AS division,',
        '       d.name AS department',
        'FROM employees e',
        'JOIN divisions v',
        '  ON v.id = e.division_id',
        'JOIN departments d',
        '  ON d.id = v.department_id;',
    ], result=('query', None)),
    dict(file='04_join.sql', code=[
        '',
        '-- 7) عدد الموظفين بكل قسم',
        'SELECT d.name,',
        '       COUNT(e.id)   AS staff,',
        '       AVG(e.salary) AS avg_salary',
        'FROM departments d',
        'JOIN divisions v',
        '  ON v.department_id = d.id',
        'LEFT JOIN employees e',
        '  ON e.division_id = v.id',
        'GROUP BY d.id, d.name;',
    ], result=('query', None)),
]


# ------------------------------------------------------------ الرسم

def tw(s, mono=F_MONO, ar=F_AR):
    return (ar if any(map(is_arabic, s)) else mono).getlength(s)


def draw_cell(d, x, y, s, col, mono=F_MONO, ar=F_AR):
    if any(map(is_arabic, s)):
        d.text((x, y - 6), s, font=ar, fill=col, direction='rtl')
    else:
        d.text((x, y), s, font=mono, fill=col)


def header(d, w, label, info):
    d.rectangle((0, 0, w, 52), fill=C['head'])
    d.text((22, 12), label, font=F_MONO_S, fill=C['gold'])
    iw = F_MONO_S.getlength(info)
    d.text((w - iw - 22, 12), info, font=F_MONO_S, fill=C['ok'])


def fmt(v):
    if v is None:
        return 'NULL'
    if isinstance(v, float):
        return f'{v:,.0f}' if v == int(v) else f'{v:,.2f}'
    if isinstance(v, int):
        return f'{v:,}' if abs(v) >= 10000 else str(v)
    return str(v)


def grid_image(cols, rows, label, info, colors=None):
    rh, pad = 50, 20
    cells = [[fmt(v) for v in r] for r in rows]
    widths = [max([tw(c)] + [tw(r[i]) for r in cells]) + pad * 2 for i, c in enumerate(cols)]
    extra = max(0, WIDTH - 24 - sum(widths))
    widths = [w + extra / len(widths) for w in widths]
    h = 52 + 16 + rh * (len(rows) + 1) + 24
    im = Image.new('RGB', (WIDTH, h), C['bg'])
    d = ImageDraw.Draw(im)
    header(d, WIDTH, label, info)
    y = 68
    x = 12
    d.rectangle((12, y, WIDTH - 12, y + rh), fill=C['head'])
    for i, c in enumerate(cols):
        draw_cell(d, x + pad, y + 11, c, C['gold'])
        x += widths[i]
    for r_i, r in enumerate(cells):
        y += rh
        d.rectangle((12, y, WIDTH - 12, y + rh), fill=C['row2'] if r_i % 2 else C['row'])
        x = 12
        for i, v in enumerate(r):
            col = (colors[r_i][i] if colors else None) or C['text']
            draw_cell(d, x + pad, y + 11, v, col)
            x += widths[i]
    d.rectangle((12, 68, WIDTH - 12, y + rh), outline=C['line'], width=2)
    return im


def msg_image(lines, info):
    h = 52 + 30 + 46 * len(lines) + 20
    im = Image.new('RGB', (WIDTH, h), C['bg'])
    d = ImageDraw.Draw(im)
    header(d, WIDTH, 'Output', info)
    for i, ln in enumerate(lines):
        d.text((30, 80 + i * 46), '✓ ' + ln if i == 0 else '  ' + ln, font=F_MONO,
               fill=C['ok'] if i == 0 else C['text'])
    return im


def schema_image(db, table, info):
    cols = db.execute(f'PRAGMA table_info({table})').fetchall()
    fks = {r[3]: f'{r[2]}({r[4]})' for r in db.execute(f'PRAGMA foreign_key_list({table})')}
    rows, colors = [], []
    for _, name, typ, notnull, _, pk in cols:
        key = 'PK' if pk else ('FK' if name in fks else '')
        rows.append([name, typ, 'NO' if (notnull or pk) else 'YES', key, fks.get(name, '')])
        colors.append([None, C['muted'], None, C['pk'] if pk else C['fk'], C['fk']])
    return grid_image(['column', 'type', 'null', 'key', 'references'], rows,
                      f'Table: {table}', info, colors)


def er_image(db):
    """مخطط العلاقات: departments 1 ── N divisions 1 ── N employees"""
    im = Image.new('RGB', (WIDTH, FULL_H), C['bg'])
    d = ImageDraw.Draw(im)
    t = 'Relationships · ERD'
    d.text(((WIDTH - F_TITLE.getlength(t)) / 2, 40), t, font=F_TITLE, fill=C['gold'])
    tables = ['departments', 'divisions', 'employees']
    notes = ['القسم', 'الإدارة', 'الموظف']
    bw, rh = 520, 44
    boxes = []
    y = 130
    for i, tb in enumerate(tables):
        cols = db.execute(f'PRAGMA table_info({tb})').fetchall()
        fks = {r[3] for r in db.execute(f'PRAGMA foreign_key_list({tb})')}
        x = (WIDTH - bw) / 2 + (-150, 0, 150)[i]
        h = 60 + rh * len(cols) + 14
        d.rounded_rectangle((x, y, x + bw, y + h), radius=16, fill=C['row'],
                            outline=C['gold'], width=3)
        d.rounded_rectangle((x, y, x + bw, y + 60), radius=16, fill=C['green'])
        d.rectangle((x, y + 40, x + bw, y + 60), fill=C['green'])
        d.text((x + 22, y + 12), tb, font=F_TITLE, fill=C['gold'])
        d.text((x + bw - 22 - F_AR.getlength(notes[i]), y + 10), notes[i], font=F_AR,
               fill=C['text'], direction='rtl')
        rows_y = {}
        for j, (_, name, typ, _, _, pk) in enumerate(cols):
            ry = y + 68 + j * rh
            rows_y[name] = ry + rh / 2 - 4
            tag = 'PK' if pk else ('FK' if name in fks else '')
            if tag:
                d.text((x + 22, ry + 6), tag, font=F_MONO_S, fill=C['pk'] if pk else C['fk'])
            d.text((x + 70, ry + 4), name, font=F_MONO, fill=C['text'])
            d.text((x + bw - 22 - F_MONO_S.getlength(typ), ry + 8), typ, font=F_MONO_S,
                   fill=C['muted'])
        boxes.append((x, y, h, rows_y))
        y += h + 110
    # خطوط العلاقات: PK (1) ← FK (N)
    links = [(0, 'id', 1, 'department_id'), (1, 'id', 2, 'division_id')]
    caps = ['كل قسم ← فيه عدة إدارات', 'كل إدارة ← فيها عدة موظفين']
    for k, (a, ac, b, bc) in enumerate(links):
        ax, ay, ah, ar = boxes[a]
        bx, by, bh, br = boxes[b]
        x0, y0 = ax + bw, ar[ac]
        x1, y1 = bx + bw, br[bc]
        xm = max(x0, x1) + 60
        d.line([(x0, y0), (xm, y0), (xm, y1), (x1, y1)], fill=C['fk'], width=4)
        d.ellipse((x0 - 7, y0 - 7, x0 + 7, y0 + 7), fill=C['fk'])
        for dy in (-14, 0, 14):                        # «رجل الغراب» = كثير (N)
            d.line([(x1 + 22, y1), (x1, y1 + dy)], fill=C['fk'], width=3)
        d.text((x0 + 12, y0 - 40), '1', font=F_TITLE, fill=C['gold'])
        d.text((x1 + 26, y1 - 42), 'N', font=F_TITLE, fill=C['gold'])
        cy = (ay + ah + by) / 2 - 18
        cap = caps[k]
        d.text(((WIDTH - F_AR_T.getlength(cap)) / 2 - 40, cy), cap, font=F_AR_T,
               fill=C['text'], direction='rtl')
    return im


# ------------------------------------------------------------ التشغيل

def main():
    os.makedirs(OUT, exist_ok=True)
    db = sqlite3.connect(':memory:')
    db.execute('PRAGMA foreign_keys = ON')
    lines = []
    file = None
    for n, b in enumerate(BLOCKS, 1):
        kind, arg = b['result']
        code = '\n'.join(b['code'])
        t0 = time.perf_counter()
        sql = '\n'.join(l for l in b['code'] if not l.strip().upper().startswith(('CREATE DATABASE', 'USE ')))
        rows = cols = None
        if kind == 'query':
            q = arg or sql
            if arg:
                db.executescript(sql)
            cur = db.execute(q)
            rows = cur.fetchall()
            cols = [c[0] for c in cur.description]
        elif sql.strip():
            db.executescript(sql)
        ms = (time.perf_counter() - t0) * 1000
        path = os.path.join(OUT, f'step{n:02d}.png')
        if kind == 'msg':
            im, pane, label = msg_image(arg, f'{ms:.2f} ms'), 'bottom', 'Output'
        elif kind == 'schema':
            im, pane, label = schema_image(db, arg, f'✓ created · {ms:.2f} ms'), 'bottom', 'Results'
        elif kind == 'er':
            im, pane, label = er_image(db), 'full', 'ER Diagram'
        else:
            label = 'Results'
            im = grid_image(cols, rows, label, f'✓ {len(rows)} rows · {ms:.2f} ms')
            pane = 'bottom'
        im.save(path, optimize=True)
        if b['file'] and b['file'] != file:
            file = b['file']
            first = True
        else:
            first = False
        for i, c in enumerate(b['code']):
            ln = {'code': c}
            if first and i == 0:
                ln['file'] = file
            lines.append(ln)
        show = {'show': os.path.relpath(path, HERE), 'pane': pane, 'label': label,
                'hold': 4.0 if pane == 'full' else (2.6 if kind == 'query' else 1.8)}
        lines.append(show)
        print(f'step {n:02d} {kind:6s} ✓ {os.path.basename(path)}')
    lines[-1]['hold'] = 3.5
    data = {
        'mode': 'plain',
        'title': 'قاعدة بيانات شركة بـ SQL 🔥',
        'handle': 'F A H A D   M O H A M M E D',
        'fps': 30, 'char_time': 0.024, 'gap': 0.06, 'file_pause': 0.45,
        'theme': {'bg': '#0F1A17', 'tabbar': '#0A1210', 'tab': '#18262A', 'line_hl': '#1A2C26',
                  'cursor': '#C8A45D', 'handle': '#C8A45D', 'title': '#F3EEE4',
                  'glow': '#123A31', 'glow2': '#3A3020'},
        'lines': lines,
    }
    with open(os.path.join(HERE, 'sql.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print('✓ sql.json')


if __name__ == '__main__':
    main()
