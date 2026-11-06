/* lib.js — shared pieces for every scene: background, floating shapes, colored word-synced captions, small drawing helpers. */
const G = globalThis;
if (!G.LIB) {
  const cl = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const pr = (t, a, b) => cl((t - a) / (b - a));

  // ── which words get colored (match without punctuation / diacritics)
  const HOT = {
    acc: ['التصرفات', 'النسوة', 'مبلغ', 'كبير', 'كمصروف', 'مصروفي', 'مصروف', 'المصاريف', 'يقلل', 'المصروف', 'مخصص', 'شهري', 'الواقع', 'يتزوج', 'الطلبات', 'لطلباتك', 'حلا', 'مكياج'],
    clay: ['حيلة', 'سنع', 'تفرض', 'ملزم', 'فجأة', 'تقلب', 'تقشف', 'صعوبة', 'يضطر', 'فيضطر', 'حقي', 'خطأ', 'المشكلة', 'براتب', 'جارية', 'يزعلون', 'ما', 'لم'],
    hi: ['آية', 'بالإحسان', 'الكسوة', 'والمسكن', 'والطعام', 'منفذ', 'سبحان', 'سبحانه', 'الله', 'وتعالى'],
  };
  const NOCOLOR_MA = true; // «ما» is colored only inside these lines:
  const MA_LINES = new Set(['l19']);
  const norm = w => String(w).replace(/[ً-ْٰـ]/g, '').replace(/[،,.:؟?!«»"]/g, '').trim();
  const HOTMAP = {}; for (const k in HOT) for (const w of HOT[k]) HOTMAP[norm(w)] = k;
  const NOCAP = new Set(['l17']);         // the ayah card shows this line itself

  let CHUNKS = null;
  function chunks(ctx) {
    if (CHUNKS) return CHUNKS;
    CHUNKS = [];
    for (const L of ctx.timeline.vo || []) {
      if (NOCAP.has(L.id)) continue;
      const ws = L.words; let cur = [];
      ws.forEach((w, i) => {
        cur.push({ ...w, i, line: L.id });
        const brk = /[،,:؟?]$/.test(w.w) && cur.length >= 2;
        const left = ws.length - 1 - i;
        if ((cur.length >= 4 && left !== 1) || cur.length >= 5 || (brk && left !== 1) || i === ws.length - 1) { CHUNKS.push(cur); cur = []; }
      });
    }
    CHUNKS.forEach((c, k) => {
      c.s = c[0].s - 0.08;
      const nx = CHUNKS[k + 1];
      c.e = nx ? Math.min(nx[0].s - 0.08, c[c.length - 1].e + 0.9) : c[c.length - 1].e + 0.6;
    });
    return CHUNKS;
  }
  function colorOf(ctx, w, lineId) {
    const n = norm(w);
    if (n === 'ما' || n === 'لم') return MA_LINES.has(lineId) ? ctx.P.clay : null;
    if (n === 'الله' && lineId === 'l19') return null;
    const k = HOTMAP[n]; return k ? ctx.P[k] : null;
  }

  /* captions: y = baseline of the line (keep ≤ 1460) */
  function caption(ctx, t, o = {}) {
    const { X, P, E } = ctx; const y = o.y ?? 1400, size = o.size ?? 76;
    const C = chunks(ctx).find(c => t >= c.s && t < c.e); if (!C) return;
    const str = C.map(w => w.w).join(' ');
    const L = ctx.text.layout(X, str, { family: 'Cairo', weight: 900, size, maxWidth: 760, lineHeight: 1.18 });
    const yy = y - (L.lines.length - 1) * size * 1.18;
    const kin = E.expoOut(pr(t, C.s, C.s + 0.25)), kout = pr(t, C.e - 0.12, C.e);
    // soft plate behind the caption
    const pw = Math.min(840, L.width + 80), ph = L.lines.length * size * 1.18 + 46;
    X.save(); X.globalAlpha = 0.55 * kin * (1 - kout); X.fillStyle = '#060B14';
    X.beginPath(); X.roundRect(540 - pw / 2, yy - size * 1.02 - 8, pw, ph, 28); X.fill(); X.restore();
    let cur = -1; C.forEach((w, j) => { if (t >= w.s - 0.03) cur = j; });
    ctx.text.drawLayout(X, L, 540, yy, {
      perWord: (i) => {
        const w = C[i]; if (!w) return { skip: true };
        const said = t >= w.s - 0.03, k = E.expoOut(pr(t, w.s - 0.05, w.s + 0.2));
        const col = colorOf(ctx, w.w, w.line);
        const isCur = i === cur;
        return {
          alpha: (said ? 1 : 0.38) * (1 - kout),
          dy: (1 - kin) * 30 - (said ? 0 : 0) + (isCur ? -4 * (1 - k) : 0),
          scale: said ? 1 + 0.08 * (1 - k) * (isCur ? 1 : 0) : 0.97,
          color: said ? (col || P.ink) : P.ink,
          stroke: { width: 10, color: '#060B14' },
        };
      }
    });
    // underline sweep under colored words when spoken
    ctx.text.drawLayout(X, L, 540, yy, { perWord: (i, s, box) => {
      const w = C[i]; const col = w && colorOf(ctx, w.w, w.line);
      if (col && t >= w.s) { const k = E.expoOut(pr(t, w.s, w.s + 0.35)); X.save(); X.globalAlpha = 1 - kout; X.fillStyle = col; X.fillRect(box.x + box.w * (1 - k), box.base + 14, box.w * k, 6); X.restore(); }
      return { skip: true };
    } });
  }

  /* background: navy with slow light, dot grid, floating outline shapes */
  function bg(ctx, t, o = {}) {
    const { X, P, W, H } = ctx;
    X.fillStyle = P.bg; X.fillRect(0, 0, W, H);
    const cx = 540 + 160 * Math.sin(t * 0.21), cy = 760 + 120 * Math.cos(t * 0.17);
    const g = X.createRadialGradient(cx, cy, 40, cx, cy, 1100);
    g.addColorStop(0, o.glow || 'rgba(242,179,61,0.10)'); g.addColorStop(1, 'rgba(14,22,38,0)');
    X.fillStyle = g; X.fillRect(0, 0, W, H);
    // dot grid drifting
    X.save(); X.fillStyle = 'rgba(245,241,232,0.07)'; const off = (t * 14) % 60;
    for (let y = -60; y < H + 60; y += 60) for (let x = 0; x < W + 60; x += 60) { X.beginPath(); X.arc(x - off, y + off * 0.5, 2.2, 0, 6.283); X.fill(); }
    X.restore();
    shapes(ctx, t, o.shapes ?? 9, o.seed ?? 1);
  }
  function shapes(ctx, t, n, seed) {
    const { X, P } = ctx; const r = ctx.seeded(seed * 97 + 3);
    const cols = [P.acc, P.hi, P.clay, P.ink];
    for (let i = 0; i < n; i++) {
      const kind = i % 4, bx = r() * 1080, by = 180 + r() * 1150, sz = 18 + r() * 40, sp = 0.3 + r() * 0.5, ph = r() * 6.28, col = cols[Math.floor(r() * 4)];
      const x = bx + 40 * Math.sin(t * sp + ph), y = by + 30 * Math.cos(t * sp * 0.8 + ph), rot = t * sp * 0.8 + ph;
      X.save(); X.translate(x, y); X.rotate(rot); X.globalAlpha = 0.22; X.strokeStyle = col; X.fillStyle = col; X.lineWidth = 4;
      X.beginPath();
      if (kind === 0) X.arc(0, 0, sz * 0.6, 0, 6.283);
      else if (kind === 1) { X.moveTo(0, -sz * 0.6); X.lineTo(sz * 0.55, sz * 0.4); X.lineTo(-sz * 0.55, sz * 0.4); X.closePath(); }
      else if (kind === 2) { X.rect(-sz * 0.45, -sz * 0.45, sz * 0.9, sz * 0.9); }
      else { X.moveTo(-sz * 0.5, 0); X.lineTo(sz * 0.5, 0); X.moveTo(0, -sz * 0.5); X.lineTo(0, sz * 0.5); }
      X.stroke(); X.restore();
    }
  }

  /* helpers */
  const pill = (ctx, x, y, w, h, fill, alpha = 1) => { const X = ctx.X; X.save(); X.globalAlpha *= alpha; X.fillStyle = fill; X.beginPath(); X.roundRect(x - w / 2, y - h / 2, w, h, h / 2); X.fill(); X.restore(); };
  const card = (ctx, x, y, w, h, o = {}) => { const X = ctx.X; X.save(); X.globalAlpha *= o.alpha ?? 1; X.shadowColor = 'rgba(0,0,0,.35)'; X.shadowBlur = 40; X.shadowOffsetY = 16; X.fillStyle = o.fill || '#16223A'; X.beginPath(); X.roundRect(x - w / 2, y - h / 2, w, h, o.r ?? 36); X.fill(); X.shadowColor = 'transparent'; if (o.stroke) { X.strokeStyle = o.stroke; X.lineWidth = o.lw || 4; X.stroke(); } X.restore(); };
  const pop = (ctx, t, s, d = 0.35) => ctx.E.backOut(pr(t, s, s + d));   // 0..1 (engine backOut = soft, no overshoot)
  const label = (ctx, str, x, y, o = {}) => ctx.text(ctx.X, str, x, y, { family: o.family || 'display', size: o.size || 90, color: o.color || ctx.P.ink, weight: o.weight || 400, align: o.align || 'center', alpha: o.alpha, maxWidth: o.maxWidth || 960, stroke: o.stroke, shadow: o.shadow });
  const ring = (ctx, x, y, r, k, col, lw = 10) => { const X = ctx.X; if (k <= 0) return; X.save(); X.strokeStyle = col; X.lineWidth = lw; X.lineCap = 'round'; X.beginPath(); X.arc(x, y, r, -Math.PI / 2, -Math.PI / 2 + 6.283 * cl(k)); X.stroke(); X.restore(); };
  const burst = (ctx, t, s, x, y, col, n = 12, R = 160) => { const X = ctx.X, k = pr(t, s, s + 0.55); if (k <= 0 || k >= 1) return; const e = ctx.E.expoOut(k); X.save(); X.strokeStyle = col; X.lineWidth = 8 * (1 - k) + 1; X.lineCap = 'round'; for (let i = 0; i < n; i++) { const a = i / n * 6.283; X.beginPath(); X.moveTo(x + Math.cos(a) * R * 0.45 * e, y + Math.sin(a) * R * 0.45 * e); X.lineTo(x + Math.cos(a) * R * e, y + Math.sin(a) * R * e); X.stroke(); } X.restore(); };
  const W = (ctx, line, i) => ctx.wordTime(line, i).s;

  G.LIB = { caption, bg, shapes, pill, card, pop, label, ring, burst, W, cl, pr, norm };
}
export default G.LIB;
