import L from './lib.js'; import I from './icons.js';
MOTION.scene({ id: 's7',
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    const x0 = W('l18', 3), sh = I.shake(t, x0, 16, 0.4);
    X.save(); X.translate(sh[0], sh[1]);
    L.bg(ctx, t, { seed: 7, glow: 'rgba(239,91,69,0.10)' });
    // «مفهومة خطأ»: the ayah card (miniature) gets an X
    const out = L.pr(t, W('l19', 0) - 0.3, W('l19', 0) + 0.1);
    if (out < 1) { X.save(); X.globalAlpha = 1 - out;
      const k = E.expoOut(L.pr(t, ctx.scene.start, ctx.scene.start + 0.5));
      ctx.text(X, 'مفهومة', 540, 400, { family: 'display', size: 120, color: P.ink, alpha: k });
      L.card(ctx, 540, 700, 640, 300, { fill: '#1A2742', stroke: 'rgba(245,241,232,.15)' });
      for (let i = 0; i < 3; i++) { X.fillStyle = 'rgba(245,241,232,.25)'; X.beginPath(); X.roundRect(290, 620 + i * 60, 500 - i * 90, 22, 11); X.fill(); }
      I.xmark(ctx, 540, 700, 1.6, E.expoOut(L.pr(t, x0 - 0.05, x0 + 0.35)), P.clay, 26);
      L.burst(ctx, t, x0 + 0.1, 540, 700, P.clay, 14, 330);
      I.stamp(ctx, t, x0, 'خطأ', 540, 1060, P.clay, { size: 130 });
      I.stamp(ctx, t, W('l18', 5), 'خطأ', 300, 900, P.clay, { size: 80, rot: 0.15, alpha: 0.7 });
      X.restore(); }
    // l19-l20: quote card «اصرف … مصروف شهري» crossed out, stamp «لم يقل»
    const q0 = W('l19', 0);
    if (t > q0 + 0.05) {
      const k = E.expoOut(L.pr(t, q0 + 0.05, q0 + 0.5));
      ctx.text(X, 'الله سبحانه وتعالى', 540, 360, { family: 'Aref Ruqaa', weight: 700, size: 92, color: P.hi, alpha: k });
      const n0 = W('l19', 6), kn = E.expoOut(L.pr(t, n0 - 0.05, n0 + 0.3));
      if (kn > 0) { X.save(); X.translate(540, 520); X.scale(0.8 + 0.2 * kn, 0.8 + 0.2 * kn); X.globalAlpha = kn; L.pill(ctx, 0, -30, 400, 130, P.clay); ctx.text(X, 'لم يقل', 0, 8, { family: 'display', size: 100, color: P.ink }); X.restore(); }
      const c0 = W('l20', 0), kc = E.expoOut(L.pr(t, c0 - 0.15, c0 + 0.4));
      if (kc > 0) { X.save(); X.globalAlpha = kc; X.translate(0, (1 - kc) * 60);
        L.card(ctx, 540, 860, 860, 380, { fill: '#F5F1E8' });
        ctx.text(X, '“', 170, 780, { family: 'Inter', weight: 900, size: 160, color: P.acc, dir: 'ltr' });
        const Ly = ctx.text.layout(X, 'اصرف للفتيات أو الزوجة مصروف شهري', { family: 'display', size: 88, maxWidth: 720, lineHeight: 1.25 });
        const B = ctx.text.drawLayout(X, Ly, 540, 830, { color: P.bg, perWord: i => ({ alpha: E.expoOut(L.pr(t, W('l20', i) - 0.1, W('l20', i) + 0.2)) > 0.01 ? 1 : 0.15 }) });
        // red strike through every line when «شهري» lands
        const ks = E.expoInOut(L.pr(t, W('l20', 5) + 0.15, W('l20', 5) + 0.6));
        if (ks > 0) { const rows = {}; B.forEach(b => { const r = Math.round(b.base); (rows[r] = rows[r] || []).push(b); });
          Object.values(rows).forEach((bs, j) => { const x1 = Math.min(...bs.map(b => b.x)) - 10, x2 = Math.max(...bs.map(b => b.x + b.w)) + 10, y = bs[0].base - 30, kk = L.cl(ks * 2 - j);
            X.strokeStyle = P.clay; X.lineWidth = 12; X.lineCap = 'round'; X.beginPath(); X.moveTo(x2, y); X.lineTo(x2 - (x2 - x1) * kk, y + 4); X.stroke(); }); }
        X.restore(); }
    }
    X.restore();
    L.caption(ctx, t);
  } });
