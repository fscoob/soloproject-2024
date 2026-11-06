/* icons.js — simple drawn icons (no images) */
import L from './lib.js';
const G = globalThis;
if (!G.ICO) {
  const person = (ctx, x, y, s, col, o = {}) => { const X = ctx.X; X.save(); X.translate(x, y); X.rotate(o.rot || 0); X.scale(s, s); X.globalAlpha *= o.alpha ?? 1; X.fillStyle = col;
    X.beginPath(); X.arc(0, -70, 38, 0, 6.283); X.fill(); X.beginPath(); X.moveTo(-70, 70); X.quadraticCurveTo(-70, -20, 0, -20); X.quadraticCurveTo(70, -20, 70, 70); X.closePath(); X.fill(); X.restore(); };
  const check = (ctx, x, y, s, k, col) => { if (k <= 0) return; ctx.drawPath(ctx.X, [[x - 40 * s, y], [x - 10 * s, y + 30 * s], [x + 45 * s, y - 35 * s]], k, { width: 16 * s, color: col, cap: 'round' }); };
  const xmark = (ctx, x, y, s, k, col, w = 22) => { const X = ctx.X; const k1 = L.cl(k * 2), k2 = L.cl(k * 2 - 1); X.save(); X.strokeStyle = col; X.lineWidth = w * s; X.lineCap = 'round';
    X.beginPath(); X.moveTo(x - 60 * s, y - 60 * s); X.lineTo(x - 60 * s + 120 * s * k1, y - 60 * s + 120 * s * k1); X.stroke();
    if (k2 > 0) { X.beginPath(); X.moveTo(x + 60 * s, y - 60 * s); X.lineTo(x + 60 * s - 120 * s * k2, y - 60 * s + 120 * s * k2); X.stroke(); } X.restore(); };
  const bubble = (ctx, x, y, w, h, fill, k, tail = 'right') => { const X = ctx.X; if (k <= 0) return; X.save(); X.translate(x, y + h / 2); X.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k); X.translate(0, -h / 2); X.globalAlpha *= L.cl(k * 1.5); X.fillStyle = fill;
    X.beginPath(); X.roundRect(-w / 2, -h / 2, w, h, 40); X.fill(); const tx = tail === 'right' ? w / 2 - 90 : -w / 2 + 90; X.beginPath(); X.moveTo(tx - 30, h / 2 - 4); X.lineTo(tx + (tail === 'right' ? 40 : -40), h / 2 + 50); X.lineTo(tx + 30, h / 2 - 4); X.fill(); X.restore(); };
  const coin = (ctx, x, y, r, col, rot = 0) => { const X = ctx.X; X.save(); X.translate(x, y); X.scale(Math.cos(rot), 1); X.fillStyle = col; X.beginPath(); X.arc(0, 0, r, 0, 6.283); X.fill(); X.strokeStyle = 'rgba(14,22,38,.35)'; X.lineWidth = r * 0.14; X.beginPath(); X.arc(0, 0, r * 0.68, 0, 6.283); X.stroke(); X.restore(); };
  const bill = (ctx, x, y, w, rot, col) => { const X = ctx.X, h = w * 0.48; X.save(); X.translate(x, y); X.rotate(rot); X.fillStyle = col; X.beginPath(); X.roundRect(-w / 2, -h / 2, w, h, 10); X.fill(); X.strokeStyle = 'rgba(14,22,38,.35)'; X.lineWidth = 5; X.beginPath(); X.roundRect(-w / 2 + 12, -h / 2 + 12, w - 24, h - 24, 6); X.stroke(); X.beginPath(); X.arc(0, 0, h * 0.22, 0, 6.283); X.stroke(); X.restore(); };
  const stamp = (ctx, t, s, str, x, y, col, o = {}) => { const k = L.pr(t, s, s + 0.28); if (k <= 0) return; const X = ctx.X, sc = 1.6 - 0.6 * ctx.E.expoOut(k), size = o.size || 110;
    X.save(); X.translate(x, y); X.rotate(o.rot ?? -0.12); X.scale(sc, sc); X.globalAlpha *= L.cl(k * 2) * (o.alpha ?? 1);
    X.font = ctx.font('Lalezar', 400, size); const w = X.measureText(str).width + 70; X.strokeStyle = col; X.lineWidth = 10; X.beginPath(); X.roundRect(-w / 2, -size * 0.78, w, size * 1.25, 18); X.stroke();
    ctx.text(X, str, 0, size * 0.3, { family: 'display', size, color: col }); X.restore(); };
  const shake = (t, s, amp = 14, d = 0.35) => { const k = L.pr(t, s, s + d); if (k <= 0 || k >= 1) return [0, 0]; const a = amp * 0.3 * (1 - k); return [a * Math.sin(t * 40), a * Math.cos(t * 33)]; };
  G.ICO = { person, check, xmark, bubble, coin, bill, stamp, shake };
}
export default G.ICO;
