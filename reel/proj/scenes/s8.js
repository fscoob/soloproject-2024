import L from './lib.js'; import I from './icons.js';
const HEART = 'M540 920 C 360 790 300 690 360 600 C 420 520 520 540 540 620 C 560 540 660 520 720 600 C 780 690 720 790 540 920 Z';
MOTION.scene({ id: 's8',
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    L.bg(ctx, t, { seed: 8, glow: 'rgba(56,201,165,0.14)' });
    // «بالإحسان» — heart drawn + kashida stretch
    const h0 = W('l21', 0), out = L.pr(t, W('l23', 0) - 0.3, W('l23', 0) + 0.1);
    if (out < 1) { X.save(); X.globalAlpha = 1 - out;
      ctx.drawPath(X, HEART, E.cubicInOut(L.pr(t, h0, W('l21', 3) + 0.2)), { width: 14, color: P.hi, tip: { r: 10, color: P.hi } });
      const ih = W('l21', 3), kf = E.expoOut(L.pr(t, ih, ih + 0.4)); if (kf > 0) { X.save(); X.globalAlpha *= 0.9 * kf; X.translate(540, 730); X.scale(0.7 + 0.3 * kf, 0.7 + 0.3 * kf); X.translate(-540, -730); X.fillStyle = P.hi; X.fill(new Path2D(HEART)); X.restore(); }
      ctx.text.drawKashida(X, 'بالإحسان', 540, 1130, 760, { family: 'display', size: 150, color: P.hi }, E.expoInOut(L.pr(t, ih, ih + 0.9)));
      // coin dropping into heart on l22
      const c = W('l22', 2), q = L.pr(t, c - 0.1, c + 0.6); if (q > 0 && q < 1) I.coin(ctx, 540, 300 + 440 * E.cubicIn(q), 60, P.acc, q * 9);
      L.burst(ctx, t, W('l22', 4), 540, 730, P.acc, 12, 300);
      X.restore(); }
    // l23-l24: «الطلبات» → gift items pop around: حلا · مكياج · هذا
    const g0 = W('l23', 5);
    if (t > g0 - 0.3) {
      const fo = L.pr(t, W('l25', 0) - 0.3, W('l25', 0) + 0.2);
      X.save(); X.globalAlpha = 1 - fo;
      const k = E.expoOut(L.pr(t, g0 - 0.2, g0 + 0.4));
      // envelope of money «خذي هذا المبلغ»
      X.save(); X.translate(540, 720); X.scale(k, k); X.fillStyle = '#FFFFFF'; X.beginPath(); X.roundRect(-200, -130, 400, 260, 24); X.fill();
      X.strokeStyle = 'rgba(14,22,38,.25)'; X.lineWidth = 6; X.beginPath(); X.moveTo(-200, -130); X.lineTo(0, 20); X.lineTo(200, -130); X.stroke();
      const up = E.expoOut(L.pr(t, W('l23', 8), W('l23', 8) + 0.5)); I.bill(ctx, 0, -60 - 80 * up, 240, 0, '#56C08F'); X.restore();
      [[W('l24', 4), 'حلا', 250, 470, P.acc], [W('l24', 6), 'هذا', 830, 470, P.ink], [W('l24', 8), 'مكياج', 540, 1040, P.acc]].forEach(([s, str, x, y, col], j) => {
        const kk = E.expoOut(L.pr(t, s - 0.08, s + 0.3)); if (kk <= 0) return; const fl = 10 * Math.sin(t * 2 + j);
        X.save(); X.translate(x, y + fl); X.scale(0.6 + 0.4 * kk, 0.6 + 0.4 * kk); X.globalAlpha *= kk;
        X.fillStyle = col; X.beginPath(); X.roundRect(-110, -70, 220, 150, 22); X.fill(); X.fillStyle = P.bg; X.fillRect(-10, -70, 20, 150);
        X.strokeStyle = col; X.lineWidth = 10; X.beginPath(); X.ellipse(-30, -90, 30, 18, 0.4, 0, 6.283); X.ellipse(30, -90, 30, 18, -0.4, 0, 6.283); X.stroke();
        ctx.text(X, str, 0, 150, { family: 'display', size: 76, color: P.ink }); X.restore(); });
      X.restore();
    }
    // l25: «يجي بالإحسان» — big word again with hand-drawn underline
    const r = W('l25', 0);
    if (t > r - 0.2) { const k = E.expoOut(L.pr(t, r - 0.2, r + 0.4));
      ctx.text(X, 'يجي', 540, 520, { family: 'display', size: 110, color: P.ink, alpha: k });
      ctx.text(X, 'بالإحسان', 540, 760, { family: 'display', size: 210 * (0.9 + 0.1 * k), color: P.hi, alpha: k });
      ctx.drawPath(X, [[820, 820], [600, 838], [300, 822]], E.expoOut(L.pr(t, W('l25', 3), W('l25', 3) + 0.5)), { width: 12, color: P.acc }); }
    L.caption(ctx, t);
  } });
