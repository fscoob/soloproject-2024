import L from './lib.js'; import I from './icons.js';
MOTION.scene({ id: 's2',
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    L.bg(ctx, t, { seed: 2, glow: 'rgba(56,201,165,0.10)' });
    // «فسبحان الله» ornament
    const a0 = W('l4', 0), ka = E.expoOut(L.pr(t, a0 - 0.1, a0 + 0.5)) * (1 - L.pr(t, W('l5', 0) - 0.4, W('l5', 0)));
    if (ka > 0) { ctx.text(X, 'سبحان الله', 540, 330, { family: 'Aref Ruqaa', weight: 700, size: 120, color: P.hi, alpha: ka });
      ctx.drawPath(X, [[300, 380], [780, 380]], ka, { width: 4, color: P.hi }); }
    // wedding rings — interlock on «يتزوج»
    const r0 = W('l4', 2), kr = E.expoOut(L.pr(t, r0 - 0.2, r0 + 0.6));
    const ry = 650 - 120 * E.cubicInOut(L.pr(t, W('l5', 3), W('l5', 4)));
    const rfade = 1 - L.pr(t, W('l6', 0) - 0.3, W('l6', 0));
    if (kr > 0 && rfade > 0) {
      X.save(); X.globalAlpha = rfade;
      const sep = 70 + 160 * (1 - kr), sc = 1 - 0.35 * E.cubicInOut(L.pr(t, W('l5', 3), W('l5', 4)));
      X.save(); X.translate(540, ry); X.scale(sc, sc);
      L.ring(ctx, -sep, 0, 130, kr, P.acc, 22); L.ring(ctx, sep, 0, 130, E.expoOut(L.pr(t, r0, r0 + 0.7)), P.ink, 22);
      const gem = E.backOut(L.pr(t, r0 + 0.4, r0 + 0.8));
      if (gem > 0) { X.fillStyle = P.hi; X.beginPath(); X.moveTo(-sep, -130 - 40 * gem); X.lineTo(-sep + 30 * gem, -130 - 10 * gem); X.lineTo(-sep, -130 + 20 * gem); X.lineTo(-sep - 30 * gem, -130 - 10 * gem); X.closePath(); X.fill(); }
      X.restore(); X.restore(); L.burst(ctx, t, r0 + 0.2, 540, ry, P.acc, 14, 260);
    }
    // l5 list of «demands» — lines appear, stamp on «تفرض»
    const s5 = W('l5', 2);
    if (t > s5 - 0.2) {
      const k = E.expoOut(L.pr(t, s5 - 0.2, s5 + 0.4)), out = L.pr(t, W('l6', 0) - 0.3, W('l6', 0) + 0.2);
      X.save(); X.globalAlpha = 1 - out; X.translate(0, (1 - k) * 200);
      L.card(ctx, 540, 900, 640, 400, { fill: '#FFFFFF' });
      for (let i = 0; i < 4; i++) { const kk = E.expoOut(L.pr(t, s5 + i * 0.18, s5 + 0.4 + i * 0.18));
        X.fillStyle = 'rgba(14,22,38,.18)'; X.beginPath(); X.roundRect(320 + (1 - kk) * 40, 770 + i * 80, 380 * kk, 26, 13); X.fill();
        X.fillStyle = P.acc; X.beginPath(); X.arc(770, 783 + i * 80, 16 * kk, 0, 6.283); X.fill(); }
      I.stamp(ctx, t, W('l5', 4), 'تفرض', 600, 930, P.clay, { size: 120 });
      X.restore();
    }
    // l6 man + chains + lock on «ملزم»
    const s6 = W('l6', 0);
    if (t > s6 - 0.2) {
      const k = E.expoOut(L.pr(t, s6 - 0.2, s6 + 0.5));
      I.person(ctx, 540, 860 + (1 - k) * 120, 1.7, P.ink, { alpha: k });
      const kc = E.cubicInOut(L.pr(t, W('l6', 1), W('l6', 3)));
      for (let i = 0; i < 9; i++) { const a = -0.3 + i * 0.32; const kk = L.cl(kc * 9 - i);
        if (kk <= 0) continue; X.save(); X.translate(540 + Math.cos(a + 3.14) * 250 * (1 + 0), 860 + Math.sin(a) * 40 + i * 14 - 60); X.rotate(i % 2 ? 0.9 : -0.2);
        X.strokeStyle = P.mut; X.lineWidth = 12; X.globalAlpha = kk; X.beginPath(); X.ellipse(0, 0, 36, 20, 0, 0, 6.283); X.stroke(); X.restore();
        X.save(); X.translate(540 + 250 - i * 6, 860 + Math.sin(a) * 40 + i * 14 - 60); X.rotate(i % 2 ? -0.9 : 0.2);
        X.strokeStyle = P.mut; X.lineWidth = 12; X.globalAlpha = kk; X.beginPath(); X.ellipse(0, 0, 36, 20, 0, 0, 6.283); X.stroke(); X.restore(); }
      // padlock
      const lk = W('l6', 3), kl = E.expoOut(L.pr(t, lk - 0.05, lk + 0.3));
      if (kl > 0) { const sh = I.shake(t, lk + 0.25, 10); X.save(); X.translate(540 + sh[0], 600 + sh[1]); X.globalAlpha = kl; X.scale(0.7 + 0.3 * kl, 0.7 + 0.3 * kl);
        const close = E.cubicOut(L.pr(t, lk + 0.1, lk + 0.3));
        X.strokeStyle = P.clay; X.lineWidth = 22; X.beginPath(); X.arc(0, -50 + 30 * close - 30, 55, Math.PI, 0); X.lineTo(55, -20); X.stroke();
        X.fillStyle = P.clay; X.beginPath(); X.roundRect(-85, -30, 170, 140, 22); X.fill();
        X.fillStyle = P.bg; X.beginPath(); X.arc(0, 30, 16, 0, 6.283); X.fill(); X.fillRect(-6, 30, 12, 40); X.restore();
        ctx.text(X, 'ملزم', 540, 1180, { family: 'display', size: 130, color: P.clay, alpha: kl }); }
    }
    L.caption(ctx, t);
  } });
