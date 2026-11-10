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
