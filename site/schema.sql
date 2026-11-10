-- جدول رسائل نموذج التواصل
CREATE TABLE IF NOT EXISTS messages (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT    NOT NULL,
  email      TEXT    NOT NULL,
  message    TEXT    NOT NULL,
  created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_messages_created ON messages (created_at);

-- أمثلة استعلامات:
-- آخر 10 رسائل:
--   SELECT name, email, message, created_at FROM messages ORDER BY id DESC LIMIT 10;
-- عدد الرسائل لكل يوم:
--   SELECT date(created_at) AS day, COUNT(*) FROM messages GROUP BY day;
