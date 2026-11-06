import L from './lib.js'; import I from './icons.js';
MOTION.scene({ id: 's10',
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    L.bg(ctx, t, { seed: 10, glow: 'rgba(239,91,69,0.10)' });
    const s0 = W('l29', 0), tgt = W('l29', 4), out = L.pr(t, W('l30', 0) - 0.3, W('l30', 0) + 0.1);
    if (out < 1) { X.save(); X.globalAlpha = 1 - out;
      ctx.text(X, 'المشكلة كلها', 540, 340, { family: 'display', size: 120, color: P.clay, alpha: E.expoOut(L.pr(t, s0 - 0.1, s0 + 0.4)) });
      // arrows converge to the center target
      for (let i = 0; i < 10; i++) { const a = i / 10 * 6.283 + 0.3, q = E.cubicInOut(L.pr(t, s0 + 0.3 + i * 0.07, tgt + i * 0.03)); if (q <= 0) continue;
        const R0 = 520, R1 = 190, R = R0 + (R1 - R0) * q, x = 540 + Math.cos(a) * R, y = 760 + Math.sin(a) * R * 0.85;
        X.save(); X.translate(x, y); X.rotate(a + Math.PI); X.fillStyle = i % 2 ? P.clay : P.ink; X.globalAlpha *= 0.85;
        X.beginPath(); X.moveTo(40, 0); X.lineTo(-10, -26); X.lineTo(-10, -10); X.lineTo(-60, -10); X.lineTo(-60, 10); X.lineTo(-10, 10); X.lineTo(-10, 26); X.closePath(); X.fill(); X.restore(); }
      const kt = E.expoOut(L.pr(t, tgt - 0.05, tgt + 0.35));
      if (kt > 0) { X.save(); X.translate(540, 760); X.scale(0.6 + 0.4 * kt, 0.6 + 0.4 * kt); X.globalAlpha *= kt;
        [150, 105, 60].forEach((r, j) => { X.fillStyle = j % 2 ? P.ink : P.acc; X.beginPath(); X.arc(0, 0, r, 0, 6.283); X.fill(); }); X.restore();
        L.burst(ctx, t, tgt + 0.1, 540, 760, P.acc, 14, 260);
        ctx.text(X, 'المصروف', 540, 1100, { family: 'display', size: 140, color: P.acc, alpha: kt }); }
      X.restore(); }
    // l30 envelope «مبلغ مخصص» ; l31 question marks «كيف جايز؟»
    const e0 = W('l30', 2);
    if (t > e0 - 0.3) { const k = E.expoOut(L.pr(t, e0 - 0.3, e0 + 0.4));
      X.save(); X.translate(540, 700); X.scale(k * 1.2, k * 1.2); X.fillStyle = '#F5F1E8'; X.beginPath(); X.roundRect(-220, -140, 440, 280, 26); X.fill();
      X.strokeStyle = 'rgba(14,22,38,.25)'; X.lineWidth = 6; X.beginPath(); X.moveTo(-220, -140); X.lineTo(0, 30); X.lineTo(220, -140); X.stroke();
      X.fillStyle = P.clay; X.beginPath(); X.arc(0, 30, 34, 0, 6.283); X.fill(); X.restore();
      ctx.text(X, 'مبلغ مخصص', 540, 1060, { family: 'display', size: 120, color: P.acc, alpha: E.expoOut(L.pr(t, W('l30', 3) - 0.05, W('l30', 3) + 0.3)) });
      const q0 = W('l31', 4); for (let i = 0; i < 3; i++) { const kq = E.expoOut(L.pr(t, q0 + i * 0.12, q0 + 0.35 + i * 0.12)); if (kq <= 0) continue;
        ctx.text(X, '؟', [250, 830, 540][i], [480, 470, 420][i] - 10 * Math.sin(t * 3 + i), { family: 'display', size: [150, 130, 190][i] * kq, color: P.clay, alpha: kq }); } }
    L.caption(ctx, t);
  } });
