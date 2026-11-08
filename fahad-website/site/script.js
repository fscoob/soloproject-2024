const toast = document.getElementById('toast');
function show(t) { toast.textContent = t; toast.hidden = false; clearTimeout(show.t); show.t = setTimeout(function () { toast.hidden = true; }, 2000); }
document.getElementById('copy').addEventListener('click', function () {
  try { navigator.clipboard.writeText('fahad.scoob').then(function () { show('نُسخ: fahad.scoob'); }, function () { show('fahad.scoob'); }); }
  catch (e) { show('fahad.scoob'); }
});
