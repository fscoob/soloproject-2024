import L from './lib.js'; import I from './icons.js';
// simple drawn icons for the three basics
const shirt = (X, c) => { X.fillStyle = c; X.beginPath(); X.moveTo(-30, -60); X.lineTo(-80, -40); X.lineTo(-100, 0); X.lineTo(-70, 15); X.lineTo(-55, -5); X.lineTo(-55, 70); X.lineTo(55, 70); X.lineTo(55, -5); X.lineTo(70, 15); X.lineTo(100, 0); X.lineTo(80, -40); X.lineTo(30, -60); X.quadraticCurveTo(0, -30, -30, -60); X.fill(); };
const house = (X, c) => { X.fillStyle = c; X.beginPath(); X.moveTo(0, -80); X.lineTo(95, 0); X.lineTo(70, 0); X.lineTo(70, 70); X.lineTo(-70, 70); X.lineTo(-70, 0); X.lineTo(-95, 0); X.closePath(); X.fill(); X.fillStyle = '#16223A'; X.fillRect(-20, 20, 40, 50); };
const plate = (X, c) => { X.strokeStyle = c; X.lineWidth = 12; X.beginPath(); X.arc(0, 0, 62, 0, 6.283); X.stroke(); X.beginPath(); X.arc(0, 0, 36, 0, 6.283); X.stroke(); X.lineCap = 'round'; X.beginPath(); X.moveTo(-95, -60); X.lineTo(-95, 60); X.moveTo(95, -60); X.lineTo(95, 60); X.stroke(); };
MOTION.scene({ id: 's9',
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    L.bg(ctx, t, { seed: 9, glow: 'rgba(56,201,165,0.10)' });
    ctx.text(X, 'الأساسيات', 540, 330, { family: 'display', size: 120, color: P.ink, alpha: E.expoOut(L.pr(t, W('l26', 0) - 0.1, W('l26', 0) + 0.4)) });
    const items = [[W('l26', 2), 'الكسوة', shirt], [W('l26', 3), 'المسكن', house], [W('l26', 4), 'الطعام', plate]];
    const ok = W('l27', 2);
    items.forEach(([s, str, ic], j) => {
      const k = E.expoOut(L.pr(t, s - 0.1, s + 0.4)); if (k <= 0) return;
      const y = 520 + j * 230;
      X.save(); X.globalAlpha = k; X.translate((1 - k) * 300, 0);
      L.card(ctx, 540, y, 820, 190, { fill: '#16223A', stroke: t > ok + j * 0.15 ? P.hi : 'rgba(245,241,232,.1)' });
      X.save(); X.translate(820, y); X.scale(0.75, 0.75); ic(X, P.acc); X.restore();
      ctx.text(X, str, 600, y + 30, { family: 'display', size: 100, color: P.ink, align: 'right' });
      const kc = E.expoOut(L.pr(t, ok + j * 0.15, ok + 0.4 + j * 0.15));
      if (kc > 0) { X.fillStyle = P.hi; X.beginPath(); X.arc(230, y, 62 * kc, 0, 6.283); X.fill(); I.check(ctx, 232, y + 4, 0.9, kc, P.bg); }
      X.restore();
    });
    // l28 «أتحدى» + stamp «منفّذ»
    I.stamp(ctx, t, W('l28', 0), 'أتحدى', 320, 1190, P.acc, { size: 84, rot: 0.06 });
    I.stamp(ctx, t, W('l28', 5) - 0.05, 'منفّذ', 760, 1200, P.hi, { size: 100, rot: -0.1 });
    L.caption(ctx, t);
  } });
