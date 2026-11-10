# -*- coding: utf-8 -*-
"""
مواصفات ريل: قاعدة بيانات شركة (أقسام ← إدارات ← موظفين)
=========================================================
هذا الملف هو «المحتوى» فقط، ويكتبه الوكلاء:
  - وكيل الكتابة (motion-writer):  BLOCKS ← خطوات الكود ونوع نتيجة كل خطوة
  - وكيل الشرح   (motion-explainer): CAPTIONS / NOTES / ER_NOTES / PANEL_NOTES
  - وكيل التصميم (motion-designer):  META['theme'] والعنوان
  - وكيل العرض   (motion-presenter): يشغّل sql_reel.py و code_typer.py ويراجع الإطارات
"""

META = {
    'title': 'قاعدة بيانات شركة بـ SQL 🔥',
    'handle': 'F A H A D   M O H A M M E D',
    'assets': 'assets/sql',
    'json': 'sql.json',
    'char_time': 0.024, 'gap': 0.06, 'file_pause': 0.45,
    'theme': {'bg': '#0F1A17', 'tabbar': '#0A1210', 'tab': '#18262A', 'line_hl': '#1A2C26',
              'cursor': '#C8A45D', 'handle': '#C8A45D', 'title': '#F3EEE4',
              'glow': '#123A31', 'glow2': '#3A3020'},
    'outro': {'name': 'F A H A D   M O H A M M E D', 'sub': 'SQL · Database Design'},
}

# ------------------------------------------------------------ وكيل الكتابة
BLOCKS = [
    dict(file='01_database.sql', code=[
        '-- 1) إنشاء قاعدة بيانات الشركة',
        'CREATE DATABASE company;',
        'USE company;',
    ], result=('msg', ['Query OK, 1 row affected', 'Database changed → company'])),

    dict(file='02_tables.sql', code=[
        '-- 2) جدول الأقسام',
        'CREATE TABLE departments (',
        '  id   INT PRIMARY KEY,',
        '  name VARCHAR(50) NOT NULL',
        ');',
    ], result=('schema', 'departments')),
    dict(file='02_tables.sql', code=[
        '',
        '-- 3) الإدارات داخل كل قسم',
        'CREATE TABLE divisions (',
        '  id   INT PRIMARY KEY,',
        '  name VARCHAR(50) NOT NULL,',
        '  department_id INT,',
        '  FOREIGN KEY (department_id)',
        '    REFERENCES departments(id)',
        ');',
    ], result=('schema', 'divisions')),
    dict(file='02_tables.sql', code=[
        '',
        '-- 4) الموظفين وبياناتهم',
        'CREATE TABLE employees (',
        '  id     INT PRIMARY KEY,',
        '  name   VARCHAR(50) NOT NULL,',
        '  job    VARCHAR(50),',
        '  salary DECIMAL(10,2),',
        '  division_id INT,',
        '  FOREIGN KEY (division_id)',
        '    REFERENCES divisions(id)',
        ');',
    ], result=('schema', 'employees')),
    dict(file=None, code=[], result=('er', None)),          # مخطط العلاقات

    dict(file='03_data.sql', code=[
        '-- 5) إدخال البيانات',
        'INSERT INTO departments VALUES',
        "  (1, 'تقنية المعلومات'),",
        "  (2, 'المالية'),",
        "  (3, 'الموارد البشرية');",
    ], result=('query', 'SELECT * FROM departments;')),
    dict(file='03_data.sql', code=[
        '',
        'INSERT INTO divisions VALUES',
        "  (1, 'البرمجة',  1),",
        "  (2, 'الشبكات',  1),",
        "  (3, 'الحسابات', 2),",
        "  (4, 'التوظيف',  3);",
    ], result=('query', 'SELECT * FROM divisions;')),
    dict(file='03_data.sql', code=[
        '',
        'INSERT INTO employees VALUES',
        "  (1, 'فهد',  'مطوّر',  12000, 1),",
        "  (2, 'سارة', 'مهندسة شبكات', 11000, 2),",
        "  (3, 'خالد', 'محاسب', 9500, 3),",
        "  (4, 'نورة', 'أخصائية توظيف', 9000, 4),",
        "  (5, 'ريم',  'مطوّرة', 12500, 1);",
    ], result=('query', 'SELECT * FROM employees;')),

    dict(file='04_join.sql', code=[
        '-- 6) الربط: مين يشتغل وين؟',
        'SELECT e.name,',
        '       v.name AS division,',
        '       d.name AS department',
        'FROM employees e',
        'JOIN divisions v',
        '  ON v.id = e.division_id',
        'JOIN departments d',
        '  ON d.id = v.department_id;',
    ], result=('query', None)),
    dict(file='04_join.sql', code=[
        '',
        '-- 7) عدد الموظفين بكل قسم',
        'SELECT d.name,',
        '       COUNT(e.id)   AS staff,',
        '       AVG(e.salary) AS avg_salary',
        'FROM departments d',
        'JOIN divisions v',
        '  ON v.department_id = d.id',
        'LEFT JOIN employees e',
        '  ON e.division_id = v.id',
        'GROUP BY d.id, d.name;',
    ], result=('query', None)),
]


# شروحات كل خطوة: شريط الخطوة أسفل الفيديو + أسهم مساعدة على الكود
# note: (رقم السطر داخل الكتلة, النص المستهدف, الشرح, نوع: arrow|spot, زوم, توقف)


# ------------------------------------------------------------ وكيل الشرح
# شريط الخطوة أسفل الفيديو (رقم الكتلة ← النص)
CAPTIONS = {
    1: 'الخطوة 1: إنشاء قاعدة البيانات', 2: 'الخطوة 2: جدول الأقسام',
    3: 'الخطوة 3: الإدارات داخل الأقسام', 4: 'الخطوة 4: جدول الموظفين',
    5: 'العلاقات: قسم ← إدارات ← موظفين', 6: 'الخطوة 5: إدخال البيانات',
    9: 'الخطوة 6: ربط الجداول بـ JOIN', 10: 'الخطوة 7: التجميع بـ GROUP BY',
}


def n(line, match, text, kind='arrow', zoom=None, wait=1.1):
    """سهم شرح: رقم السطر داخل الكتلة، النص المستهدف، الشرح، arrow|spot، زوم، توقف."""
    return dict(line=line, match=match, text=text, kind=kind, zoom=zoom, wait=wait)


SPOT = dict(kind='spot', zoom=1.15, wait=1.6)

# شرح كل عنصر في الكود (أكثر من سهم على نفس السطر يظهرون بالتتابع)
NOTES = {
    1: [n(0, '--', 'سطر يبدأ بـ -- = تعليق، SQL يتجاهله'),
        n(1, 'CREATE DATABASE', 'ننشئ قاعدة بيانات جديدة'),
        n(1, 'company', 'اسم القاعدة'),
        n(1, ';', 'الفاصلة المنقوطة = نهاية الأمر', wait=0.9),
        n(2, 'USE', 'نختار القاعدة اللي بنشتغل عليها')],
    2: [n(1, 'CREATE TABLE', 'ننشئ جدول جديد'),
        n(1, 'departments', 'اسم الجدول: الأقسام'),
        n(2, 'id', 'عمود رقم القسم'),
        n(2, 'INT', 'INT = رقم صحيح', wait=0.9),
        n(2, 'PRIMARY KEY', '🔑 مفتاح أساسي: فريد ولا يتكرر', wait=1.4),
        n(3, 'VARCHAR(50)', 'نص لين 50 حرف'),
        n(3, 'NOT NULL', 'إجباري: ما يصير فاضي'),
        n(4, ');', 'نهاية تعريف الجدول', wait=0.8)],
    3: [n(2, 'divisions', 'جدول الإدارات'),
        n(3, 'PRIMARY KEY', '🔑 رقم فريد لكل إدارة', wait=0.9),
        n(5, 'department_id', 'عمود يحفظ رقم القسم التابع له'),
        n(6, 'FOREIGN KEY', '🔗 مفتاح أجنبي: يشير لجدول ثاني', wait=1.3),
        n(7, 'REFERENCES departments(id)', '🔗 مربوط بـ id في جدول الأقسام', **SPOT)],
    4: [n(2, 'employees', 'جدول الموظفين'),
        n(3, 'id', '🔑 رقم الموظف', wait=0.9),
        n(4, 'NOT NULL', 'الاسم إجباري', wait=0.9),
        n(5, 'job', 'المسمى الوظيفي (اختياري)'),
        n(6, 'DECIMAL(10,2)', 'رقم عشري: 10 خانات، منها 2 بعد الفاصلة', wait=1.4),
        n(7, 'division_id', 'رقم الإدارة اللي يتبع لها'),
        n(8, 'FOREIGN KEY', '🔗 مفتاح أجنبي ثاني', wait=0.9),
        n(9, 'REFERENCES divisions(id)', '🔗 كل موظف يتبع إدارة', **SPOT)],
    6: [n(1, 'INSERT INTO', 'نضيف صفوف للجدول'),
        n(1, 'VALUES', 'القيم بنفس ترتيب الأعمدة'),
        n(2, "'تقنية المعلومات'", "النص يُكتب بين ' '"),
        n(4, ';', 'آخر صف ينتهي بـ ; وما قبله بـ ,', wait=1.3)],
    7: [n(2, '1),', 'رقم القسم: 1 = تقنية المعلومات', wait=1.3),
        n(4, '2),', '2 = المالية', wait=0.9)],
    8: [n(2, '12000', 'الراتب', wait=0.9),
        n(2, '1),', 'رقم الإدارة (FK) = البرمجة', wait=1.3),
        n(3, "'مهندسة شبكات'", 'المسمى الوظيفي', wait=0.9)],
    9: [n(1, 'SELECT', 'نختار الأعمدة اللي نبي نعرضها'),
        n(1, 'e.name', 'e = اختصار جدول الموظفين'),
        n(2, 'AS', 'AS = اسم جديد للعمود في النتيجة'),
        n(4, 'FROM employees e', 'نبدأ من جدول الموظفين'),
        n(5, 'JOIN', 'نضم جدول الإدارات'),
        n(6, 'v.id = e.division_id', '🔑 = 🔗 نطابق المفتاحين', **SPOT),
        n(8, 'd.id = v.department_id', 'وكل إدارة ← قسمها', kind='spot', wait=1.4)],
    10: [n(3, 'COUNT(e.id)', 'نعدّ الموظفين'),
         n(4, 'AVG(e.salary)', 'متوسط الرواتب'),
         n(8, 'LEFT JOIN', 'يشمل حتى الإدارات اللي ما فيها موظفين', wait=1.5),
         n(10, 'GROUP BY', 'نجمع النتيجة لكل قسم', **SPOT)],
}

# أسهم على مخطط العلاقات (إحداثيات داخل صورة ER، الوقت نسبةً لنهاية العرض)
ER_NOTES = [
    ((96, 198, 596, 242), 'PK: المفتاح الأساسي لكل قسم', -6.0, 1.3),
    ((246, 558, 746, 602), '1 قسم ← عدة إدارات', -4.6, 1.5),
    ((396, 962, 896, 1006), '1 إدارة ← عدة موظفين', -3.0, 1.6),
]

# أسهم على لوحة النتائج تحت الكود: (رقم الكتلة) ← [(قيمة أول عمود أو header, اسم العمود, الشرح)]
PANEL_NOTES = {
    2: [('id', 'key', 'PK = مفتاح أساسي')],
    3: [('department_id', 'references', '🔗 مربوط بجدول الأقسام')],
    4: [('division_id', 'references', '🔗 مربوط بجدول الإدارات')],
    8: [('header', 'division_id', 'أرقام الإدارات (FK)')],
    9: [('header', 'department', 'جاي من جدول ثالث عبر الربط')],
    10: [('header', 'staff', 'نتيجة COUNT لكل قسم')],
}
