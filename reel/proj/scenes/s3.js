import L from './lib.js'; import I from './icons.js';
MOTION.scene({ id: 's3',
  setup(ctx) {
    this.rain = ctx.particles2D({ count: 46, seed: 31, spawn: (i, r) => ({ x: r.range(120, 960), y: r.range(-200, 120), vx: r.gauss() * 30, vy: r.range(380, 720), r: r.range(16, 30), color: r.pick([ctx.P.acc, '#FFD36E', ctx.P.acc]), delay: r.range(0, 1.2), life: 2.6, shape: 'circle' }), gravity: 300 });
  },
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    L.bg(ctx, t, { seed: 3 });
    // «مثلاً» → woman's request as a phone-like demand card, then money stack on «مبلغ كبير»
    const m0 = W('l7', 5), km = E.expoOut(L.pr(t, m0 - 0.1, m0 + 0.6));
    const out = L.pr(t, W('l9', 0) - 0.4, W('l9', 0));
    // stack of bills growing
    const n = Math.floor(L.cl(L.pr(t, m0, W('l7', 7)) * 14));
    X.save(); X.globalAlpha = 1 - out; X.translate(0, out * -140); const sc = 1 - 0.35 * out; X.translate(540, 820); X.scale(sc, sc); X.translate(-540, -820);
    for (let i = 0; i < (km > 0 ? Math.max(1, n) : 0); i++) { const kk = E.expoOut(L.pr(t, m0 + i * 0.1, m0 + 0.25 + i * 0.1)); I.bill(ctx, 540 + Math.sin(i * 1.7) * 14, 980 - i * 30 - (1 - kk) * 80, 420, Math.sin(i * 2.3) * 0.05, i % 2 ? '#3FAF7E' : '#56C08F'); }
    if (km > 0) { const kb = E.expoOut(L.pr(t, W('l7', 6), W('l7', 6) + 0.4)); ctx.text(X, 'مبلغ كبير', 540, 470, { family: 'display', size: 140 * (0.85 + 0.15 * kb), color: P.acc, alpha: kb }); }
    X.restore();
    // coins rain on «كبير»
    const rs = W('l7', 6);
    if (t > rs && t < rs + 4) this.rain.draw(X, t - rs, 1 - L.pr(t, rs + 3, rs + 4));
    // «كمصروف» pill
    const ks = W('l7', 7), kp = E.expoOut(L.pr(t, ks - 0.05, ks + 0.35)) * (1 - L.pr(t, W('l8', 0) - 0.2, W('l8', 0) + 0.1));
    if (kp > 0) { X.save(); X.globalAlpha = kp; L.pill(ctx, 540, 1150, 420, 120, P.acc); ctx.text(X, 'كمصروف', 540, 1178, { family: 'display', size: 84, color: P.bg }); X.restore(); }
    // l8 «هذا مصروفي» speech bubble
    const b0 = W('l8', 1), kbub = E.expoOut(L.pr(t, b0 - 0.05, b0 + 0.35)) * (1 - out);
    if (kbub > 0) { I.bubble(ctx, 540, 1110, 640, 190, P.ink, kbub); ctx.text(X, 'هذا مصروفي!', 540, 1140, { family: 'display', size: 100, color: P.bg, alpha: kbub }); }
    // l9 man pays: bills fly from him to the bubble side + check «عادي»
    const p0 = W('l9', 0);
    if (t > p0 - 0.3) {
      const k = E.expoOut(L.pr(t, p0 - 0.3, p0 + 0.4));
      I.person(ctx, 300, 1040 + (1 - k) * 100, 1.4, P.ink, { alpha: k });
      const pay = W('l9', 2);
      for (let i = 0; i < 4; i++) { const q = L.pr(t, pay + i * 0.15, pay + 0.8 + i * 0.15); if (q <= 0 || q >= 1) continue; const e = E.cubicInOut(q);
        I.bill(ctx, 300 + 480 * e, 900 - Math.sin(e * 3.14) * 260, 160, e * 3, '#56C08F'); }
      const cc = W('l9', 3); I.coin(ctx, 780, 980, 90 * E.backOut(L.pr(t, pay + 0.5, pay + 0.9)), P.acc, 0);
      const kc = L.pr(t, cc, cc + 0.4); if (kc > 0) { X.save(); X.fillStyle = P.hi; X.globalAlpha = kc; X.beginPath(); X.arc(780, 700, 80, 0, 6.283); X.fill(); X.restore(); I.check(ctx, 785, 705, 1.1, E.expoOut(kc), P.bg); }
      ctx.text(X, 'عادي', 780, 600, { family: 'display', size: 90, color: P.hi, alpha: kc });
    }
    L.caption(ctx, t);
  } });
