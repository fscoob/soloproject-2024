import L from './lib.js'; import I from './icons.js';
const AYAH = 'الرِّجَالُ قَوَّامُونَ عَلَى النِّسَاءِ';
MOTION.scene({ id: 's6',
  draw(t, lt, ctx) {
    const { X, P, E } = ctx; const W = (l, i) => L.W(ctx, l, i);
    L.bg(ctx, t, { seed: 6, shapes: 4, glow: 'rgba(56,201,165,0.12)' });
    // open book drawn (lines) on «وتستند»
    const b0 = W('l16', 0), kb = E.expoOut(L.pr(t, b0 - 0.2, b0 + 0.7)), ko = L.pr(t, W('l17', 2), W('l17', 3) - 0.1);
    if (kb > 0 && ko < 1) { X.save(); X.globalAlpha = kb * (1 - ko); X.translate(540, 760);
      const op = E.cubicInOut(L.pr(t, b0, b0 + 0.9));
      [-1, 1].forEach(s => { X.save(); X.scale(s, 1); X.transform(1, 0, -0.08 * (1 - op), 1, 0, 0);
        X.fillStyle = '#FFFFFF'; X.beginPath(); X.moveTo(0, -200); X.quadraticCurveTo(150, -240, 330 * (0.3 + 0.7 * op), -200); X.lineTo(330 * (0.3 + 0.7 * op), 200); X.quadraticCurveTo(150, 160, 0, 200); X.closePath(); X.fill();
        X.fillStyle = 'rgba(14,22,38,.15)'; for (let i = 0; i < 6; i++) X.fillRect(40, -140 + i * 52, 240 * op * (i === 5 ? 0.6 : 1), 12); X.restore(); });
      X.strokeStyle = P.hi; X.lineWidth = 8; X.beginPath(); X.moveTo(0, -200); X.lineTo(0, 200); X.stroke(); X.restore();
      ctx.text(X, 'آية', 540, 420, { family: 'display', size: 140, color: P.hi, alpha: E.expoOut(L.pr(t, W('l16', 2) - 0.05, W('l16', 2) + 0.3)) * (1 - ko) }); }
    // ayah card
    const a0 = W('l17', 3) - 0.15;
    if (t > a0 - 0.3) {
      const k = E.expoOut(L.pr(t, a0 - 0.3, a0 + 0.4));
      X.save(); X.globalAlpha = k; X.translate(0, (1 - k) * 80);
      L.card(ctx, 540, 760, 920, 560, { fill: '#FFFFFF', r: 40 });
      // ornamental frame
      X.strokeStyle = P.hi; X.lineWidth = 5; X.beginPath(); X.roundRect(110, 510, 860, 500, 28); X.stroke();
      X.lineWidth = 2; X.beginPath(); X.roundRect(126, 526, 828, 468, 20); X.stroke();
      [[110, 510], [970, 510], [110, 1010], [970, 1010]].forEach(([x, y]) => { X.save(); X.translate(x, y); X.rotate(0.785); X.fillStyle = P.hi; X.fillRect(-16, -16, 32, 32); X.restore(); });
      ctx.text(X, 'قال تعالى', 540, 610, { family: 'Cairo', weight: 700, size: 46, color: '#5A6478' });
      // the verse revealed right→left word by word with the voice
      const Ly = ctx.text.layout(X, AYAH, { family: 'Amiri Quran', weight: 400, size: 124, maxWidth: 820 });
      ctx.text.drawLayout(X, Ly, 540, 800, { color: '#0E1626', perWord: i => ({ reveal: E.cubicOut(L.pr(t, W('l17', 3 + i) - 0.12, W('l17', 3 + i) + 0.35)) }) });
      ctx.text(X, '[النساء: 34]', 540, 940, { family: 'Cairo', weight: 700, size: 44, color: P.hi, alpha: E.expoOut(L.pr(t, W('l17', 6) + 0.2, W('l17', 6) + 0.6)) });
      X.restore();
    }
    L.caption(ctx, t);
  } });
