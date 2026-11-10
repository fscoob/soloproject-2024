// السنة في التذييل
document.getElementById('year').textContent = new Date().getFullYear();

// إظهار الأقسام بنعومة عند الوصول إليها
const io = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (e.isIntersecting) {
      e.target.classList.add('in');
      io.unobserve(e.target);
    }
  }
}, { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

// نموذج التواصل ← الخادم (server.js) ← قاعدة البيانات (SQL)
const form = document.getElementById('contact-form');
const status = form.querySelector('.status');

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  if (!form.checkValidity()) {
    status.className = 'status err';
    status.textContent = 'فضلاً عبّئ كل الحقول ببريد صحيح.';
    return;
  }
  const data = Object.fromEntries(new FormData(form));
  const btn = form.querySelector('button');
  btn.disabled = true;
  status.className = 'status';
  status.textContent = 'جاري الإرسال…';
  try {
    const res = await fetch('/api/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    const out = await res.json();
    if (!res.ok) throw new Error(out.error || 'تعذّر الإرسال');
    form.reset();
    status.className = 'status ok';
    status.textContent = 'وصلت رسالتك، شكراً لك ✓';
  } catch (err) {
    status.className = 'status err';
    status.textContent = err.message;
  } finally {
    btn.disabled = false;
  }
});
