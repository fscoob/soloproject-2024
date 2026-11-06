import L from './lib.js'; import I from './icons.js';
MOTION.scene({ id: 's12',
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    L.bg(ctx, t, { seed: 12, shapes: 14 });
    // «سبحان الله» ornament
    const s0 = W('l36', 0), k0 = E.expoOut(L.pr(t, s0 - 0.1, s0 + 0.5));
    ctx.text(X, 'سبحان الله', 540, 340, { family: 'Aref Ruqaa', weight: 700, size: 120, color: P.hi, alpha: k0 });
    // «هذا الواقع» kashida stretch
    const w0 = W('l36', 3), kw = E.expoOut(L.pr(t, w0 - 0.1, w0 + 0.4));
    if (kw > 0) { ctx.text(X, 'هذا', 540, 560, { family: 'display', size: 130, color: P.ink, alpha: kw });
      ctx.text.drawKashida(X, 'الواقع', 540, 800, 820, { family: 'display', size: 260, color: P.acc }, E.expoInOut(L.pr(t, w0, w0 + 1.2)));
      L.burst(ctx, t, w0 + 0.05, 540, 720, P.acc, 16, 420); }
    // l37: small chips «يزعلون» drifting
    const z0 = W('l37', 4), kz = E.expoOut(L.pr(t, z0 - 0.05, z0 + 0.35)) * (1 - L.pr(t, W('l38', 0), W('l38', 0) + 0.4));
    if (kz > 0) { X.save(); X.globalAlpha = kz; X.translate(780, 1020); X.rotate(0.08); L.pill(ctx, 0, -25, 300, 110, P.clay); ctx.text(X, 'يزعلون', 0, 6, { family: 'display', size: 76, color: P.ink }); X.restore(); }
    // l38: underline pulse on «الواقع» + closing ring
    const r0 = W('l38', 2), kr = E.expoOut(L.pr(t, r0 - 0.1, r0 + 0.6));
    ctx.drawPath(X, [[900, 870], [540, 890], [180, 868]], kr, { width: 14, color: P.hi });
    const end = ctx.scene.end, ke = E.cubicInOut(L.pr(t, end - 1.4, end - 0.2));
    if (ke > 0) { L.ring(ctx, 540, 1100, 90, ke, P.acc, 10);  }
    L.caption(ctx, t);
  } });
