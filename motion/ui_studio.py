# -*- coding: utf-8 -*-
"""
ui_studio.py — واجهة «DB Studio» لعرض أثر كل خطوة SQL بشكل جمالي
=================================================================
تُرسم من القاعدة الحقيقية (SQLite) بعد كل خطوة:
  db     ← القاعدة ظهرت في الشريط الجانبي + بطاقات إحصائيات
  table  ← بنية الجدول الجديد: الأعمدة، الأنواع، PK / NOT NULL / FK ← الجدول المرتبط
  data   ← شبكة البيانات مع إبراز الصفوف الجديدة
  query  ← مسار الربط بين الجداول + النتائج
  chart  ← رسم أعمدة لنتيجة التجميع
كل دالة ترجع (الصورة, مستطيل الهدف لسهم الشرح).
"""

import os

from PIL import Image, ImageDraw, ImageFont

from code_typer import ARABIC, MONO, SANS, find_font, hex_rgb, is_arabic

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 992, 1204
SIDE = 322

C = {k: hex_rgb(v) for k, v in {
    'bg': '#0B1412', 'side': '#0E1B18', 'card': '#13231F', 'card2': '#172A25',
    'line': '#22332F', 'gold': '#C8A45D', 'cream': '#F3EEE4', 'text': '#D6DEEB',
    'muted': '#7F8D99', 'ok': '#5BD18B', 'fk': '#6FC3FF', 'green': '#123A31',
    'new': '#1E3A2C'}.items()}


def _f(names, size):
    return ImageFont.truetype(find_font(names), size)


F = {
    'h1': _f(SANS, 34), 'h2': _f(SANS, 26), 'b': _f(SANS, 22), 's': _f(ARABIC, 19),
    'ui': _f(ARABIC, 22), 'mono': _f(MONO, 22), 'mono_s': _f(MONO, 18), 'big': _f(SANS, 46),
}


def text(d, xy, s, font, fill, align='left'):
    """نص يدعم العربي؛ align=right يعني xy هو الطرف الأيمن."""
    x, y = xy
    w = font.getlength(s)
    if align == 'right':
        x -= w
    elif align == 'center':
        x -= w / 2
    d.text((x, y), s, font=font, fill=fill)
    return w


def pill(d, x, y, s, fg, bg, font=None, pad=12, h=32):
    font = font or F['mono_s']
    w = font.getlength(s) + pad * 2
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=bg)
    d.text((x + pad, y + (h - font.size) / 2 - 2), s, font=font, fill=fg)
    return w


def db_icon(d, x, y, s, col):
    d.rounded_rectangle((x, y + s * 0.15, x + s, y + s * 0.85), radius=int(s * 0.12), fill=col)
    for k in (0.15, 0.45, 0.75):
        d.ellipse((x, y + s * (k - 0.13), x + s, y + s * (k + 0.13)), fill=col,
                  outline=C['bg'], width=max(1, int(s * 0.06)))


def table_icon(d, x, y, s, col):
    d.rounded_rectangle((x, y, x + s, y + s), radius=4, outline=col, width=2)
    d.line((x, y + s / 3, x + s, y + s / 3), fill=col, width=2)
    d.line((x + s / 2, y + s / 3, x + s / 2, y + s), fill=col, width=2)


# ------------------------------------------------------------ القاعدة

def snapshot(db):
    tables = [r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid")]
    counts = {t: db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in tables}
    rels = []
    for t in tables:
        for r in db.execute(f'PRAGMA foreign_key_list({t})'):
            rels.append((t, r[3], r[2], r[4]))
    return tables, counts, rels


# ------------------------------------------------------------ الإطار

def frame(db, dbname, active=None, new=None, view='Structure'):
    tables, counts, rels = snapshot(db)
    im = Image.new('RGB', (W, H), C['bg'])
    d = ImageDraw.Draw(im)
    # شريط التطبيق
    d.rectangle((0, 0, W, 64), fill=C['side'])
    seal = Image.open(os.path.join(HERE, '..', 'site', 'assets', 'seal-gold.png')).convert('RGBA')
    seal = seal.resize((int(seal.width * 40 / seal.height), 40), Image.LANCZOS)
    im.paste(seal, (20, 12), seal)
    text(d, (62, 14), 'DB Studio', F['h2'], C['cream'])
    w = F['mono_s'].getlength(f'SQLite · {dbname}') + 52
    d.rounded_rectangle((W - w - 20, 16, W - 20, 48), radius=16, fill=C['card'])
    d.ellipse((W - w - 4, 27, W - w + 6, 37), fill=C['ok'])
    text(d, (W - w + 14, 20), f'SQLite · {dbname}', F['mono_s'], C['text'])
    d.line((0, 64, W, 64), fill=C['line'], width=2)

    # الشريط الجانبي
    d.rectangle((0, 65, SIDE, H - 44), fill=C['side'])
    d.line((SIDE, 65, SIDE, H - 44), fill=C['line'], width=2)
    text(d, (22, 84), 'EXPLORER', F['mono_s'], C['muted'])
    y = 122
    target = None
    is_new_db = new == ('db', dbname)
    if is_new_db:
        d.rounded_rectangle((10, y - 6, SIDE - 10, y + 40), radius=10, fill=C['new'],
                            outline=C['gold'], width=2)
        target = (10, y - 6, SIDE - 10, y + 40)
    db_icon(d, 22, y, 30, C['gold'])
    text(d, (64, y + 2), dbname, F['mono'], C['cream'])
    if is_new_db:
        pill(d, SIDE - 78, y + 2, 'NEW', C['green'], C['gold'], F['mono_s'], 10, 28)
    y += 56
    text(d, (40, y), f'Tables ({len(tables)})', F['mono_s'], C['muted'])
    y += 36
    for t in tables:
        on = t == active
        fresh = new == ('table', t)
        if fresh or on:
            d.rounded_rectangle((26, y - 6, SIDE - 10, y + 36), radius=10,
                                fill=C['new'] if fresh else C['card'],
                                outline=C['gold'] if fresh else None, width=2)
        if fresh:
            target = (26, y - 6, SIDE - 10, y + 36)
        table_icon(d, 44, y + 4, 22, C['gold'] if (on or fresh) else C['muted'])
        text(d, (78, y), t, F['mono'], C['cream'] if (on or fresh) else C['text'])
        badge = 'NEW' if fresh else str(counts[t])
        pill(d, SIDE - 24 - F['mono_s'].getlength(badge) - 20, y + 1, badge,
             C['green'] if fresh else C['text'], C['gold'] if fresh else C['card2'],
             F['mono_s'], 10, 28)
        y += 50
    if rels:
        y += 20
        text(d, (22, y), 'RELATIONS', F['mono_s'], C['muted'])
        y += 36
        for t, col, rt, rc in rels:
            text(d, (26, y), f'{t}', F['mono_s'], C['text'])
            text(d, (26, y + 24), f'  → {rt}', F['mono_s'], C['fk'])
            y += 60

    # شريط الحالة
    d.rectangle((0, H - 44, W, H), fill=C['side'])
    d.line((0, H - 44, W, H - 44), fill=C['line'], width=2)
    total = sum(counts.values())
    text(d, (20, H - 34), f'Tables: {len(tables)}   ·   Rows: {total}   ·   Relations: {len(rels)}',
         F['mono_s'], C['muted'])
    text(d, (W - 20, H - 34), '● ready', F['mono_s'], C['ok'], 'right')

    # عنوان المنطقة الرئيسية + تبويبات العرض
    mx = SIDE + 28
    crumb = f'{dbname}  ›  {active}' if active else dbname
    text(d, (mx, 86), crumb, F['mono'], C['muted'])
    x = mx
    for v in ('Structure', 'Data', 'Relations'):
        on = v == view
        x += pill(d, x, 128, v, C['green'] if on else C['muted'], C['gold'] if on else C['card'],
                  F['mono_s'], 16, 34) + 10
    return im, d, target, (tables, counts, rels)


# ------------------------------------------------------------ العروض

def ui_db(db, dbname):
    im, d, target, (tables, counts, rels) = frame(db, dbname, new=('db', dbname), view='Structure')
    mx = SIDE + 28
    cw = W - mx - 28
    d.rounded_rectangle((mx, 190, mx + cw, 520), radius=24, fill=C['card'], outline=C['line'], width=2)
    db_icon(d, mx + cw / 2 - 45, 230, 90, C['gold'])
    text(d, (mx + cw / 2, 345), dbname, F['big'], C['cream'], 'center')
    text(d, (mx + cw / 2, 420), 'تم إنشاء قاعدة البيانات ✓', F['h2'], C['ok'], 'center')
    stats = [('Tables', len(tables)), ('Rows', sum(counts.values())), ('Relations', len(rels))]
    sw = (cw - 40) / 3
    for i, (k, v) in enumerate(stats):
        x = mx + i * (sw + 20)
        d.rounded_rectangle((x, 550, x + sw, 690), radius=18, fill=C['card'], outline=C['line'], width=2)
        text(d, (x + sw / 2, 572), str(v), F['big'], C['gold'], 'center')
        text(d, (x + sw / 2, 640), k, F['mono_s'], C['muted'], 'center')
    text(d, (mx + cw / 2, 740), 'القاعدة فاضية… الخطوة الجاية: الجداول', F['ui'], C['muted'], 'center')
    return im, target


def ui_table(db, dbname, table, target_fk=False):
    im, d, side_target, _ = frame(db, dbname, active=table, new=('table', table), view='Structure')
    cols = db.execute(f'PRAGMA table_info({table})').fetchall()
    fks = {r[3]: (r[2], r[4]) for r in db.execute(f'PRAGMA foreign_key_list({table})')}
    mx = SIDE + 28
    cw = W - mx - 28
    table_icon(d, mx, 196, 34, C['gold'])
    text(d, (mx + 48, 190), table, F['h1'], C['cream'])
    pill(d, mx + 60 + F['h1'].getlength(table), 198, 'NEW TABLE', C['green'], C['gold'], F['mono_s'], 12, 30)
    text(d, (mx, 246), f'{len(cols)} أعمدة', F['ui'], C['muted'])
    y = 300
    fk_rect = None
    for _, name, typ, notnull, _, pk in cols:
        h = 78
        d.rounded_rectangle((mx, y, mx + cw, y + h), radius=16, fill=C['card'], outline=C['line'], width=2)
        if pk:
            d.rounded_rectangle((mx, y, mx + 8, y + h), radius=4, fill=C['gold'])
        elif name in fks:
            d.rounded_rectangle((mx, y, mx + 8, y + h), radius=4, fill=C['fk'])
        text(d, (mx + 26, y + 12), name, F['mono'], C['cream'])
        text(d, (mx + 26, y + 44), typ, F['mono_s'], C['muted'])
        x = mx + cw - 18
        chips = []
        if pk:
            chips.append(('PK', C['green'], C['gold']))
        if notnull and not pk:
            chips.append(('NOT NULL', C['text'], C['card2']))
        if name in fks:
            rt, rc = fks[name]
            chips.append((f'FK → {rt}.{rc}', C['bg'], C['fk']))
        for s, fg, bg in chips:
            fnt = F['mono_s']
            w = fnt.getlength(s) + 24
            x -= w
            pill(d, x, y + 23, s, fg, bg, fnt, 12, 32)
            if s.startswith('FK'):
                fk_rect = (x - 6, y + 17, x + w + 6, y + 61)
            x -= 10
        y += h + 14
    return im, (fk_rect if target_fk and fk_rect else side_target)


def ui_data(db, dbname, table, new_rows):
    im, d, _, _ = frame(db, dbname, active=table, view='Data')
    cur = db.execute(f'SELECT * FROM {table}')
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    mx = SIDE + 28
    cw = W - mx - 28
    text(d, (mx, 192), table, F['h1'], C['cream'])
    pill(d, mx + 20 + F['h1'].getlength(table), 200, f'+{new_rows} rows', C['bg'], C['ok'], F['mono_s'], 12, 30)
    fnt, fa = F['mono_s'], F['s']

    def tw(s):
        return (fa if any(map(is_arabic, s)) else fnt).getlength(s)

    cells = [[('{:,}'.format(v) if isinstance(v, (int, float)) and abs(v) >= 1000 else str(v)) for v in r]
             for r in rows]
    widths = [max([tw(c)] + [tw(r[i]) for r in cells]) + 26 for i, c in enumerate(cols)]
    extra = max(0, cw - sum(widths))
    widths = [w + extra / len(widths) for w in widths]
    y, rh = 260, 54
    d.rounded_rectangle((mx, y, mx + cw, y + rh * (len(rows) + 1) + 4), radius=16, fill=C['card'],
                        outline=C['line'], width=2)
    x = mx
    for i, c in enumerate(cols):
        text(d, (x + 13, y + 15), c, fnt, C['gold'])
        x += widths[i]
    target = None
    for r_i, r in enumerate(cells):
        y += rh
        fresh = r_i >= len(rows) - new_rows
        d.line((mx + 10, y, mx + cw - 10, y), fill=C['line'], width=1)
        if fresh:
            d.rectangle((mx + 4, y + 3, mx + cw - 4, y + rh - 3), fill=C['new'])
            d.rectangle((mx + 4, y + 3, mx + 9, y + rh - 3), fill=C['ok'])
            if target is None:
                target = (mx, y, mx + cw, y + rh)
        x = mx
        for i, v in enumerate(r):
            text(d, (x + 13, y + (11 if any(map(is_arabic, v)) else 15)), v,
                 fa if any(map(is_arabic, v)) else fnt, C['cream'] if fresh else C['text'])
            x += widths[i]
    text(d, (mx, y + rh + 24), f'{len(rows)} صف في الجدول', F['ui'], C['muted'])
    return im, target


def ui_query(db, dbname, sql, chain):
    im, d, _, _ = frame(db, dbname, active=None, view='Relations')
    mx = SIDE + 28
    cw = W - mx - 28
    text(d, (mx, 192), 'مسار الربط', F['h2'], C['cream'])
    x, y = mx, 244
    for i, t in enumerate(chain):
        w = F['mono'].getlength(t) + 30
        d.rounded_rectangle((x, y, x + w, y + 50), radius=14, fill=C['card'], outline=C['gold'], width=2)
        text(d, (x + 15, y + 11), t, F['mono'], C['cream'])
        x += w
        if i < len(chain) - 1:
            d.line((x + 6, y + 25, x + 34, y + 25), fill=C['fk'], width=3)
            d.polygon([(x + 36, y + 25), (x + 26, y + 18), (x + 26, y + 32)], fill=C['fk'])
            x += 42
    target = (mx - 6, y - 6, x + 6, y + 56)
    cur = db.execute(sql)
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    y = 340
    rh = 52
    d.rounded_rectangle((mx, y, mx + cw, y + rh * (len(rows) + 1) + 4), radius=16, fill=C['card'],
                        outline=C['line'], width=2)
    cwid = cw / len(cols)
    for i, c in enumerate(cols):
        text(d, (mx + 14 + i * cwid, y + 14), c, F['mono_s'], C['gold'])
    for r in rows:
        y += rh
        d.line((mx + 10, y, mx + cw - 10, y), fill=C['line'], width=1)
        for i, v in enumerate(r):
            text(d, (mx + 14 + i * cwid, y + 10), str(v), F['s'], C['text'])
    text(d, (mx, y + rh + 24), f'{len(rows)} نتيجة من 3 جداول', F['ui'], C['muted'])
    return im, target


def ui_chart(db, dbname, sql):
    im, d, _, _ = frame(db, dbname, active=None, view='Data')
    rows = db.execute(sql).fetchall()
    mx = SIDE + 28
    cw = W - mx - 28
    text(d, (mx, 192), 'الموظفين بكل قسم', F['h2'], C['cream'])
    top = max(r[1] for r in rows) or 1
    y = 262
    target = None
    for name, staff, avg in rows:
        d.rounded_rectangle((mx, y, mx + cw, y + 150), radius=18, fill=C['card'], outline=C['line'], width=2)
        text(d, (mx + cw - 22, y + 14), str(name), F['h2'], C['cream'], 'right')
        bw = (cw - 150) * staff / top
        d.rounded_rectangle((mx + 22, y + 66, mx + 22 + cw - 150, y + 100), radius=17, fill=C['card2'])
        d.rounded_rectangle((mx + 22, y + 66, mx + 22 + max(34, bw), y + 100), radius=17, fill=C['gold'])
        text(d, (mx + cw - 22, y + 64), f'{staff}', F['h1'], C['gold'], 'right')
        text(d, (mx + 22, y + 112), f'avg salary  {avg:,.0f}', F['mono_s'], C['muted'])
        if target is None:
            target = (mx + 14, y + 58, mx + 30 + bw, y + 108)
        y += 168
    return im, target
