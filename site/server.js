// خادم الموقع: يعرض الملفات ويحفظ رسائل التواصل في قاعدة بيانات SQLite
// التشغيل: node server.js   (Node 22.13 أو أحدث، بدون أي حزم إضافية)
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { DatabaseSync } = require('node:sqlite');

const PORT = process.env.PORT || 3000;
const ROOT = __dirname;
const ADMIN_TOKEN = process.env.ADMIN_TOKEN; // لقراءة الرسائل: /api/messages?token=...

// 1) الاتصال بقاعدة البيانات وإنشاء الجدول من schema.sql
const db = new DatabaseSync(path.join(ROOT, 'site.db'));
db.exec(fs.readFileSync(path.join(ROOT, 'schema.sql'), 'utf8'));

// 2) استعلامات جاهزة (Prepared) — تحمي من حقن SQL
const insertMsg = db.prepare(
  'INSERT INTO messages (name, email, message) VALUES (?, ?, ?)'
);
const listMsgs = db.prepare(
  'SELECT id, name, email, message, created_at FROM messages ORDER BY id DESC LIMIT 50'
);

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.png': 'image/png',
  '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
};
const PUBLIC = new Set(['/index.html', '/style.css', '/app.js']);

function json(res, code, body) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body));
}

function readBody(req, limit = 10_000) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (c) => {
      data += c;
      if (data.length > limit) reject(new Error('too large'));
    });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');

  // 3) API: حفظ رسالة جديدة
  if (url.pathname === '/api/messages' && req.method === 'POST') {
    try {
      const { name = '', email = '', message = '' } = JSON.parse(await readBody(req));
      const n = String(name).trim(), e = String(email).trim(), m = String(message).trim();
      if (!n || !m || !EMAIL.test(e) || n.length > 80 || e.length > 120 || m.length > 2000) {
        return json(res, 400, { error: 'تحقق من البيانات المدخلة.' });
      }
      const r = insertMsg.run(n, e, m);
      return json(res, 201, { ok: true, id: Number(r.lastInsertRowid) });
    } catch {
      return json(res, 400, { error: 'طلب غير صالح.' });
    }
  }

  // 4) API: قراءة الرسائل (لك أنت فقط عبر رمز سري)
  if (url.pathname === '/api/messages' && req.method === 'GET') {
    if (!ADMIN_TOKEN || url.searchParams.get('token') !== ADMIN_TOKEN) {
      return json(res, 401, { error: 'غير مصرّح' });
    }
    return json(res, 200, listMsgs.all());
  }

  // 5) الملفات الثابتة
  let p = url.pathname === '/' ? '/index.html' : decodeURIComponent(url.pathname);
  if (!PUBLIC.has(p) && !p.startsWith('/assets/')) return json(res, 404, { error: 'غير موجود' });
  const file = path.join(ROOT, path.normalize(p));
  if (!file.startsWith(ROOT)) return json(res, 403, { error: 'ممنوع' });
  fs.readFile(file, (err, buf) => {
    if (err) return json(res, 404, { error: 'غير موجود' });
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
    res.end(buf);
  });
});

server.listen(PORT, () => console.log(`✓ http://localhost:${PORT}`));
