import L from './lib.js'; import I from './icons.js';
MOTION.scene({ id: 's11',
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    const j0 = W('l35', 4), dark = E.cubicInOut(L.pr(t, W('l35', 2), j0));
    const sh = I.shake(t, j0, 20, 0.5);
    X.save(); X.translate(sh[0], sh[1]);
    L.bg(ctx, t, { seed: 11, shapes: Math.round(9 * (1 - dark)) });
    // l32 calendar, day circled on «شهري»
    const c0 = W('l32', 0), out = L.pr(t, W('l33', 0) - 0.3, W('l33', 0) + 0.1);
    if (out < 1) { const k = E.expoOut(L.pr(t, c0 - 0.2, c0 + 0.5)); X.save(); X.globalAlpha = k * (1 - out); X.translate(0, (1 - k) * 80);
      L.card(ctx, 540, 760, 760, 660, { fill: '#F5F1E8' }); X.fillStyle = P.clay; X.beginPath(); X.roundRect(160, 430, 760, 130, [36, 36, 0, 0]); X.fill();
      ctx.text(X, 'كل شهر', 540, 520, { family: 'display', size: 80, color: P.ink });
      for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) { const n = r * 6 + c + 1; ctx.text(X, String(n), 810 - c * 108, 650 + r * 105, { family: 'Inter', weight: 700, size: 46, color: 'rgba(14,22,38,.55)', dir: 'ltr' }); }
      L.ring(ctx, 810, 635, 48, E.expoOut(L.pr(t, W('l32', 6) - 0.05, W('l32', 6) + 0.5)), P.acc, 10);
      const coin = L.pr(t, W('l32', 5), W('l32', 5) + 0.5); if (coin > 0 && coin < 1) I.coin(ctx, 810, 200 + 430 * E.cubicIn(coin), 50, P.acc, coin * 8);
      X.restore(); }
    // l33 rings + ? ; l34 payslip «راتب»
    const r0 = W('l33', 0), out2 = L.pr(t, W('l35', 0) - 0.3, W('l35', 0) + 0.1);
    if (t > r0 - 0.2 && out2 < 1) { X.save(); X.globalAlpha = 1 - out2;
      const k = E.expoOut(L.pr(t, r0 - 0.2, r0 + 0.4)), split = E.expoInOut(L.pr(t, W('l33', 3), W('l33', 5) + 0.3)), fadeR = 1 - L.pr(t, W('l34', 0) - 0.2, W('l34', 0) + 0.1);
      if (fadeR > 0) { X.save(); X.globalAlpha *= fadeR; L.ring(ctx, 540 - 70 - 140 * split, 680, 110, k, P.acc, 20); L.ring(ctx, 540 + 70 + 140 * split, 680, 110, k, P.ink, 20);
        ctx.text(X, '؟', 540, 740, { family: 'display', size: 200, color: P.clay, alpha: E.expoOut(L.pr(t, W('l33', 2), W('l33', 2) + 0.3)) }); X.restore(); }
      const p0 = W('l34', 0); if (t > p0 - 0.2) { const kp = E.expoOut(L.pr(t, p0 - 0.2, p0 + 0.4));
        X.save(); X.globalAlpha *= kp; X.translate(540, 740); X.rotate(-0.04 * kp); L.card(ctx, 0, 0, 560, 620, { fill: '#F5F1E8' });
        ctx.text(X, 'كشف راتب', 0, -200, { family: 'display', size: 80, color: P.bg });
        for (let i = 0; i < 4; i++) { X.fillStyle = 'rgba(14,22,38,.15)'; X.fillRect(-200, -110 + i * 70, 400 - i * 60, 22); }
        X.restore(); I.stamp(ctx, t, W('l34', 3), 'راتب', 560, 960, P.clay, { size: 120 }); }
      X.restore(); }
    // l35 dramatic: darken, chains, «جارية»
    if (dark > 0) { X.save(); X.fillStyle = `rgba(4,7,13,${0.75 * dark})`; X.fillRect(0, 0, 1080, 1920); X.restore();
      const kc = E.expoOut(L.pr(t, j0 - 0.3, j0 + 0.4));
      for (let i = 0; i < 7; i++) { const x = 140 + i * 133; X.save(); X.translate(x, 560 + (1 - kc) * -300); X.rotate(i % 2 ? Math.PI / 2 : 0); X.strokeStyle = P.mut; X.lineWidth = 16; X.globalAlpha = kc; X.beginPath(); X.ellipse(0, 0, 70, 38, 0, 0, 6.283); X.stroke(); X.restore(); }
      const kw = E.expoOut(L.pr(t, j0 - 0.05, j0 + 0.35));
      ctx.text(X, 'جارية', 540, 880, { family: 'display', size: 280 * (1.2 - 0.2 * kw), color: P.clay, alpha: kw });
      ctx.text(X, 'أو بالأحرى', 540, 1080, { family: 'display', size: 90, color: P.ink, alpha: E.expoOut(L.pr(t, W('l35', 1) - 0.1, W('l35', 1) + 0.3)) * 0.85 }); }
    X.restore();
    L.caption(ctx, t);
  } });
