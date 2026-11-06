import L from './lib.js'; import I from './icons.js';
MOTION.scene({ id: 's4',
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    const crash = W('l10', 4), sh = I.shake(t, crash, 22, 0.5);
    X.save(); X.translate(sh[0], sh[1]);
    L.bg(ctx, t, { seed: 4, glow: t > crash ? 'rgba(239,91,69,0.12)' : 'rgba(242,179,61,0.10)' });
    // chart frame
    const k0 = E.expoOut(L.pr(t, ctx.scene.start, ctx.scene.start + 0.6));
    const fade = 1 - L.pr(t, W('l11', 0) - 0.3, W('l11', 0) + 0.1);
    X.save(); X.globalAlpha = k0 * fade;
    L.card(ctx, 540, 720, 860, 640, { fill: '#121D33', stroke: 'rgba(245,241,232,.08)' });
    X.strokeStyle = 'rgba(245,241,232,.08)'; X.lineWidth = 2; for (let i = 0; i < 5; i++) { X.beginPath(); X.moveTo(150, 480 + i * 110); X.lineTo(930, 480 + i * 110); X.stroke(); }
    const up = [[160, 900], [280, 840], [380, 860], [480, 760], [580, 700], [680, 640], [760, 560]];
    const ku = E.cubicInOut(L.pr(t, W('l10', 0), crash));
    const tip = ctx.drawPath(X, up, ku, { width: 12, color: P.hi, tip: { r: 12, color: P.hi } });
    if (t > crash) { const kd = E.expoOut(L.pr(t, crash, crash + 0.6)); const dn = [[760, 560], [820, 820], [870, 760], [920, 980]];
      ctx.drawPath(X, dn, kd, { width: 12, color: P.clay, tip: { r: 14, color: P.clay } });
      L.burst(ctx, t, crash + 0.1, 820, 820, P.clay, 10, 150); }
    void tip; X.restore();
    ctx.text(X, 'فجأة', 540, 340, { family: 'display', size: 150, color: P.clay, alpha: E.expoOut(L.pr(t, W('l10', 1) - 0.05, W('l10', 1) + 0.3)) * fade });
    // l11 hourglass flip on «يقلّب»
    const h0 = W('l11', 0), kh = E.expoOut(L.pr(t, h0 - 0.2, h0 + 0.4)) * (1 - L.pr(t, W('l12', 4) - 0.3, W('l12', 4)));
    if (kh > 0) {
      const flip = E.expoInOut(L.pr(t, W('l11', 3) - 0.1, W('l11', 3) + 0.6));
      X.save(); X.translate(540, 700); X.rotate(flip * Math.PI); X.globalAlpha = kh; X.scale(kh, kh);
      X.fillStyle = P.acc; X.fillRect(-150, -230, 300, 26); X.fillRect(-150, 204, 300, 26);
      X.strokeStyle = P.ink; X.lineWidth = 12; X.beginPath(); X.moveTo(-120, -204); X.lineTo(120, -204); X.lineTo(14, 0); X.lineTo(120, 204); X.lineTo(-120, 204); X.lineTo(-14, 0); X.closePath(); X.stroke();
      const sand = 0.3 + 0.7 * ((ctx.scene.start + lt) % 1);
      X.fillStyle = P.acc; X.beginPath(); X.moveTo(-90 * (1 - sand * 0.6), -180 + 160 * sand); X.lineTo(90 * (1 - sand * 0.6), -180 + 160 * sand); X.lineTo(10, -10); X.lineTo(-10, -10); X.closePath(); X.fill();
      X.beginPath(); X.moveTo(-100, 190); X.lineTo(100, 190); X.lineTo(30 + 40 * sand, 190 - 90 * sand); X.lineTo(-30 - 40 * sand, 190 - 90 * sand); X.closePath(); X.fill();
      X.restore();
    }
    // l12 chips falling: تقشّف · صعوبة في الحياة
    [[W('l12', 4), 'تقشّف', 420, -0.08], [W('l12', 5), 'صعوبة في الحياة', 640, 0.06]].forEach(([s, str, y, rot]) => {
      const q = L.pr(t, s - 0.05, s + 0.5); if (q <= 0) return; const e = E.bounceOut(q);
      X.save(); X.translate(540, y + 500 * e); X.rotate(rot * e); X.font = ctx.font('Lalezar', 400, 110); const w = X.measureText(str).width + 90;
      L.pill(ctx, 0, -30, w, 160, P.clay); ctx.text(X, str, 0, 8, { family: 'display', size: 110, color: P.ink }); X.restore();
    });
    // down arrows
    if (t > W('l12', 4)) for (let i = 0; i < 3; i++) { const y = ((t * 260 + i * 120) % 360) + 300; ctx.text(X, '↓', 140 + i * 400, y, { family: 'Inter', weight: 900, size: 90, color: P.clay, alpha: 0.35, dir: 'ltr' }); }
    X.restore();
    L.caption(ctx, t);
  } });
