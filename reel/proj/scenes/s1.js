import L from './lib.js'; import I from './icons.js';
MOTION.scene({ id: 's1',
  draw(t, lt, ctx) {
    const { X, P, E, at } = ctx; const W = (l, i) => L.W(ctx, l, i);
    // hook push-in on the whole frame during the first 1.2 s
    const z = 1.12 - 0.12 * E.expoOut(L.pr(t, 0, 1.2));
    X.save(); X.translate(540, 760); X.scale(z, z); X.translate(-540, -760);
    L.bg(ctx, t, { seed: 1 });
    // big ring drawing from frame 0
    { const ro = 1 - L.pr(t, W('l2', 0) - 0.3, W('l2', 0) + 0.2); X.save(); X.globalAlpha = ro; L.ring(ctx, 540, 560, 250, E.expoOut(L.pr(t, 0, 1.1)), P.acc, 12);
    L.ring(ctx, 540, 560, 285, E.expoOut(L.pr(t, 0.15, 1.3)), 'rgba(31,41,55,.25)', 4); X.restore(); }
    // title rises
    { const fo = L.pr(t, W('l2', 0) - 0.35, W('l2', 0) + 0.05); if (fo < 1) { X.save(); X.globalAlpha = 1 - fo; X.translate(540, 560); X.scale(1 + 0.25 * fo, 1 + 0.25 * fo); X.translate(-540, -560); ctx.FX.riseUp(ctx, t, { text: 'بعض التصرفات', s: 0.25, y: 600, size: 150, accent: [1], underline: true }); X.restore(); } }
    // l2: people + question mark
    const s2 = W('l2', 0);
    if (t > s2 - 0.3) {
      const k = E.expoOut(L.pr(t, s2 - 0.2, s2 + 0.5));
      [[-260, 0], [0, -30], [260, 0]].forEach(([dx, dy], j) => {
        const kk = E.expoOut(L.pr(t, s2 - 0.2 + j * 0.08, s2 + 0.5 + j * 0.08));
        I.person(ctx, 540 + dx, 760 + dy + (1 - kk) * 160, 1.25, j === 1 ? P.acc : P.mut, { alpha: kk });
      });
      // question mark over the middle one
      const q = W('l2', 2), kq = E.expoOut(L.pr(t, q - 0.05, q + 0.35));
      if (kq > 0) { const sh = I.shake(t, W('l2', 4), 8); X.save(); X.translate(540 + sh[0], 470 + sh[1]); X.scale(0.6 + 0.4 * kq, 0.6 + 0.4 * kq); X.globalAlpha = kq;
        ctx.text(X, '؟', 0, 80, { family: 'display', size: 300, color: P.acc }); X.restore(); L.burst(ctx, t, q, 540, 400, P.acc, 12, 200); }
      // l3 chips
      const c1 = W('l3', 1), c2 = W('l3', 5);
      [[c1, 'ما عندهم حيلة', 1010], [c2, 'بلا سنع', 1140]].forEach(([s, str, y], j) => {
        const kc = E.expoOut(L.pr(t, s - 0.05, s + 0.35)); if (kc <= 0) return;
        X.save(); X.globalAlpha = kc; X.translate((j ? -1 : 1) * 300 * (1 - kc), 0);
        X.font = ctx.font('Lalezar', 400, 76); const w = X.measureText(str).width + 80;
        L.pill(ctx, 540, y - 22, w, 112, P.clay); ctx.text(X, str, 540, y + 4, { family: 'display', size: 76, color: '#FFFFFF' }); X.restore();
      });
      void k;
    }
    X.restore();
    L.caption(ctx, t);
  } });
