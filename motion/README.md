# Motion v1 — مونتاج «كأنك تكتب الكود»

يولّد ريل 9:16 لشاشة على مكتب تُكتب عليها أسطر كود حرفاً حرفاً بالتوقيت اللي تحدده
(على إيقاع أغنية مثلاً)، مع صوت كيبورد وعنوان وحركة كاميرا خفيفة.

## المتطلبات
Python 3 + `pip install pillow numpy` + ffmpeg

## الاستخدام
```bash
python3 code_typer.py example.json -o reel.mp4                       # مشهد مرسوم تلقائياً
python3 code_typer.py example.json -o reel.mp4 --music song.mp3 --music-start 62
python3 code_typer.py example.json --preview 6 -o frame.png          # معاينة إطار واحد
```

### صورتك الحقيقية بدل المشهد المرسوم
صوّر شاشتك (عمودي) وحدد زواياها الأربع بالبكسل: أعلى يسار، أعلى يمين، أسفل يمين، أسفل يسار:
```bash
python3 code_typer.py example.json -o reel.mp4 --bg desk.jpg --screen 120,610,980,650,975,1150,115,1190
```

## ملف السكربت (JSON)
```json
{
  "title": "Claude + Motion V1 = 🤯",
  "handle": "@your.handle",
  "file": "dream.js",
  "lines": [
    {"at": 0.4, "type": 0.9, "code": "// 1:47"},
    {"at": 1.8, "type": 2.2, "code": "while (alive) dream.big();"}
  ]
}
```
- `at`: ثانية بداية كتابة السطر — طابقها مع بداية كل جملة في الأغنية
- `type`: كم ثانية تستغرق كتابته
- `duration` (اختياري): طول الفيديو، الافتراضي = آخر سطر + 2.5 ث

خيارات أخرى: `--music-volume`، `--clicks-volume`، `--no-clicks`.

## وضع الشاشة السوداء، وعدة ملفات، وعرض النتيجة
راجع `fahad.json` كمثال كامل: موقع بـ HTML ثم CSS ثم JS ثم SQL ثم الخادم ثم terminal، وفي النهاية يتمرّر الموقع الناتج.
```bash
python3 code_typer.py fahad.json -o fahad_reel.mp4
```
- `"mode": "plain"`: نافذة محرر على خلفية سوداء. `"desk"` تعني شاشة على مكتب.
- `"file"` في أي سطر يفتح تبويباً جديداً، و`"terminal"` يعرض طرفية.
- ما تحتاج `at` و`type`. التوقيت يُحسب تلقائياً من `char_time` (ثوانٍ لكل حرف) و`gap`.
- `"instant": true` يُظهر السطر مرة وحدة، مثل مخرجات الطرفية.
- `"result": {"image": "...png", "hold": 7}` تعرض صورة الموقع في النهاية وتمرّرها.
- `"theme"` يغيّر الألوان: `cursor` و`title` و`handle` و`glow` و`bg` …
- الخطوط العربية في `fonts/` (IBM Plex Sans Arabic، رخصة OFL).

## موسيقى خلفية تعليمية (Lo-fi) بدون حقوق
`lofi.py` يولّد موسيقى هادئة أصلية بالكود: بيانو كهربائي، باص، إيقاع خفيف، وخشخشة أسطوانة.
```bash
python3 lofi.py -o music.wav --seconds 50            # غيّر --seed للحن مختلف و--bpm للسرعة
python3 code_typer.py fahad.json -o reel.mp4 --music music.wav --music-volume 0.7 --clicks-volume 0.55
```

## ريل SQL: قاعدة بيانات شركة (أقسام ← إدارات ← موظفين)
`sql_reel.py` ينفّذ كل خطوة SQL **فعلياً** على قاعدة SQLite، ويرسم نتيجتها: رسالة، أو بنية جدول، أو جدول نتائج، أو مخطط علاقات ER. وبعدها يكتب `sql.json`.
```bash
python3 sql_reel.py
python3 lofi.py --style energetic -o assets/sql/music.wav --seconds 70
python3 code_typer.py sql.json -o sql_reel.mp4 --music assets/sql/music.wav --music-volume 0.75 --clicks-volume 0.5
```
- عدّل الخطوات والبيانات في `BLOCKS` داخل `sql_reel.py`. كل كتلة فيها كود ونتيجة:
  `('msg', [...])` أو `('schema', 'table')` أو `('query', 'SELECT ...')` أو `('er', None)`.
- في `code_typer` تنعرض النتيجة بسطر `{"show": "img.png", "pane": "bottom"|"full", "hold": 2}`.
- `lofi.py --style energetic`: موسيقى تعليمية حماسية بسرعة 118 BPM، فيها مقدمة ثم بناء ثم ذروة.

## تأثير Swarm Rebuild
الشاشة تتفكك لسرب جزيئات ذهبية يطير ويعيد بناء المشهد التالي. أضف `"transition": "swarm"` لأي عرض `pane: "full"`:
```json
{"show": "assets/sql/step05.png", "pane": "full", "transition": "swarm", "hold": 5.2}
{"show": "assets/sql/outro.png", "pane": "full", "transition": "swarm", "out": false, "hold": 4.6}
```
- `"out": false` يعني المشهد يبقى للنهاية بدون ما يرجع للكود، ويُستخدم للختام.
- في ريل SQL: الكود يتحول لمخطط العلاقات ثم يرجع، وفي النهاية تتحول الشاشة لختمك واسمك.

## الأسهم المساعدة والتأثيرات التعليمية
تنضاف كسطور في ملف JSON، وتظهر فوق الكود أو فوق أي عرض كامل:
```json
{"caption": "الخطوة 3: الإدارات داخل الأقسام"}
{"note": "🔗 هنا الربط بالقسم", "match": "REFERENCES departments(id)", "line": 12,
 "kind": "spot", "zoom": 1.15, "hold": 4, "wait": 1.4}
{"note": "1 قسم ← عدة إدارات", "rect": [246, 558, 746, 602], "kind": "spot", "delay": -4.8, "hold": 1.7}
```
- `caption`: شريط شرح الخطوة أسفل الفيديو، ينزلق للداخل ويبقى لين يجي الشريط اللي بعده.
- `note`: فقاعة شرح بالعربي تظهر بحركة «بوب»، ومنها سهم منحني ينرسم للهدف، وعند وصوله تطلع شرارات ذهبية.
- `match` + `line`: الكلمة المستهدفة ورقم سطرها في الملف (العد يبدأ من 0)، وحولها مربع إبراز.
- `rect`: هدف على صورة عرض كامل، مثل مخطط ER.
- `kind: "spot"`: يعتّم كل شي ما عدا الهدف. أما `"arrow"` فيعرض مربع وسهم بس.
- `zoom`: تقريب الكاميرا على الهدف، ووقته يختفي العنوان.
- `wait`: يوقّف الكتابة عشان المشاهد يلحق يقرأ.
- تلقائياً: شرارة ونبضة كاميرا خفيفة عند ظهور كل نتيجة.
