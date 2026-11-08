const form = document.getElementById('reg');
const out = document.getElementById('out'), msg = document.getElementById('msg'), err = document.getElementById('err');
const toast = document.getElementById('toast');
function show(t) { toast.textContent = t; toast.hidden = false; clearTimeout(show.t); show.t = setTimeout(function () { toast.hidden = true; }, 2200); }
form.addEventListener('submit', function (e) {
  e.preventDefault();
  const child = form.child.value.trim(), parent = form.parent.value.trim();
  if (!child || !parent) { err.hidden = false; out.hidden = true; return; }
  err.hidden = true;
  msg.textContent = 'السلام عليكم، أبغى أسجّل في ' + form.kind.value + '.\n' +
    'اسم الطفل: ' + child + '\nالعمر: ' + form.age.value + ' سنوات\nولي الأمر: ' + parent + '\nالموعد المفضّل: ورشة السبت';
  out.hidden = false;
});
document.getElementById('copy').addEventListener('click', function () {
  const text = msg.textContent;
  const fallback = function () { const r = document.createRange(); r.selectNodeContents(msg); const s = getSelection(); s.removeAllRanges(); s.addRange(r); show('حدّدت النص، انسخه من القائمة'); };
  try { navigator.clipboard.writeText(text).then(function () { show('نُسخ النص'); }, fallback); } catch (x) { fallback(); }
});
