import L from './lib.js'; import I from './icons.js';
MOTION.scene({ id: 's5',
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    const no = W('l15', 1), sh = I.shake(t, no, 18, 0.45);
    X.save(); X.translate(sh[0], sh[1]);
    L.bg(ctx, t, { seed: 5 });
    // expenses bar shrinking on «يقلل»
    const k0 = E.expoOut(L.pr(t, ctx.scene.start, ctx.scene.start + 0.5)), out = L.pr(t, W('l14', 0) - 0.3, W('l14', 0) + 0.1);
    if (out < 1) { X.save(); X.globalAlpha = k0 * (1 - out);
      ctx.text(X, 'المصاريف', 540, 430, { family: 'display', size: 120, color: P.ink });
      const shrink = E.expoInOut(L.pr(t, W('l13', 3), W('l13', 6) + 0.3)), w = 820 * (1 - 0.55 * shrink);
      X.fillStyle = 'rgba(31,41,55,.08)'; X.beginPath(); X.roundRect(130, 520, 820, 120, 60); X.fill();
      X.fillStyle = shrink > 0.05 ? P.acc : P.hi; X.beginPath(); X.roundRect(950 - w, 520, w, 120, 60); X.fill();
      // scissors line
      if (shrink > 0 && shrink < 1) { X.strokeStyle = P.clay; X.setLineDash([16, 12]); X.lineWidth = 6; X.beginPath(); X.moveTo(950 - w, 490); X.lineTo(950 - w, 670); X.stroke(); X.setLineDash([]); }
      ctx.text(X, '↓', 950 - w - 70, 610, { family: 'Inter', weight: 900, size: 110, color: P.clay, alpha: shrink, dir: 'ltr' });
      I.person(ctx, 540, 980, 1.6, P.ink); X.restore(); }
    // l14 «ما تقدّر» — a heart cracks
    const c0 = W('l14', 2), kh = E.expoOut(L.pr(t, W('l14', 0) - 0.2, W('l14', 0) + 0.4)) * (1 - L.pr(t, W('l15', 0) - 0.2, W('l15', 0) + 0.1));
    if (kh > 0) { const crack = E.expoOut(L.pr(t, c0, c0 + 0.4)); X.save(); X.globalAlpha = kh; X.translate(540, 700); X.scale(kh * 1.6, kh * 1.6);
      [[-1, -crack * 22], [1, crack * 22]].forEach(([side, dx]) => { X.save(); X.translate(dx, 0); X.rotate(side * crack * 0.12); X.beginPath(); X.moveTo(0, 90);
        if (side < 0) { X.bezierCurveTo(-130, 0, -120, -110, -60, -110); X.bezierCurveTo(-20, -110, 0, -80, 0, -60); X.lineTo(-18, -20); X.lineTo(10, 10); X.lineTo(-12, 50); }
        else { X.bezierCurveTo(130, 0, 120, -110, 60, -110); X.bezierCurveTo(20, -110, 0, -80, 0, -60); X.lineTo(-18, -20); X.lineTo(10, 10); X.lineTo(-12, 50); }
        X.closePath(); X.fillStyle = P.clay; X.fill(); X.restore(); }); X.restore();
      ctx.text(X, 'ما تقدّر', 540, 1050, { family: 'display', size: 120, color: P.ink, alpha: E.expoOut(L.pr(t, c0, c0 + 0.3)) * kh }); }
    // l15 «لا! هذا حقي»
    const b = W('l15', 0), kb = E.expoOut(L.pr(t, b - 0.05, b + 0.3));
    if (kb > 0) { I.bubble(ctx, 540, 640, 760, 300, P.clay, kb, 'left'); ctx.text(X, 'لا!', 540, 610, { family: 'display', size: 130, color: P.ink, alpha: kb });
      ctx.text(X, 'هذا حقي', 540, 740, { family: 'display', size: 110, color: P.ink, alpha: E.expoOut(L.pr(t, W('l15', 3) - 0.05, W('l15', 3) + 0.25)) });
      L.burst(ctx, t, no, 540, 640, P.clay, 16, 420);
      const m = W('l15', 5), km = E.expoOut(L.pr(t, m - 0.05, m + 0.3)); if (km > 0) { X.save(); X.globalAlpha = km; L.pill(ctx, 540, 1000, 440, 120, P.acc); ctx.text(X, 'مصروف', 540, 1030, { family: 'display', size: 90, color: '#FFFFFF' }); X.restore(); } }
    X.restore();
    L.caption(ctx, t);
  } });
