# AlNassr News Monitor - دليل استخدام مفصل

## 📋 المحتويات

1. [المتطلبات](#المتطلبات)
2. [التثبيت المحلي](#التثبيت-المحلي)
3. [إعداد Gmail](#إعداد-gmail)
4. [التشغيل](#التشغيل)
5. [Docker](#docker)
6. [التشغيل على VPS](#التشغيل-على-vps)
7. [لوحة التحكم](#لوحة-التحكم)
8. [الإعدادات المتقدمة](#الإعدادات-المتقدمة)
9. [حل المشاكل](#حل-المشاكل)

---

## 🖥️ المتطلبات

### الحد الأدنى:
- **Python 3.12** أو أحدث
- **SQLite** (مدمج مع Python)
- اتصال إنترنت
- بريد Gmail (أو بريد آخر متوافق مع SMTP)

### اختياري:
- **OpenAI API Key** (للتصنيف الذكي)
- **Docker و Docker Compose** (للتشغيل في containers)
- **VPS أو خادم Linux** (للتشغيل المستمر)

---

## 🚀 التثبيت المحلي

### 1️⃣ استنساخ المشروع

```bash
git clone https://github.com/nfc1world11-web/AlNassr-News-Monitor.git
cd AlNassr-News-Monitor
```

### 2️⃣ إنشاء بيئة افتراضية

**على Linux/Mac:**
```bash
python3.12 -m venv venv
source venv/bin/activate
```

**على Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ تثبيت المتطلبات

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ إعداد متغيرات البيئة

```bash
cp .env.example .env
```

**ثم عدّل `.env` بالمحرر:**

```bash
nano .env      # على Linux/Mac
# أو
code .env      # إذا كنت تستخدم VS Code
```

---

## 📧 إعداد Gmail

### الخطوة 1: تفعيل المصادقة ذات العاملين (2FA)

1. اذهب إلى: https://myaccount.google.com/security
2. ابحث عن "2-Step Verification"
3. اتبع التعليمات لتفعيله

### الخطوة 2: إنشاء كلمة مرور التطبيق

1. بعد تفعيل 2FA، اذهب إلى: https://myaccount.google.com/apppasswords
2. اختر "Mail" و"Windows Computer" (أو جهازك)
3. ستظهر لك كلمة مرور مكونة من **16 حرف**
4. انسخها إلى `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=nfc1world11@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # 16 حرف
SMTP_FROM=nfc1world11@gmail.com
EMAIL_RECIPIENT=nfc1world11@gmail.com
EMAIL_RECIPIENT_NAME=مراقب النصر
```

---

## ▶️ التشغيل

### تشغيل محلي مباشر:

```bash
source venv/bin/activate  # أو venv\Scripts\activate على Windows
python src/main.py
```

**ستري رسالة مثل:**
```
2024-06-29 15:30:00 - INFO - بدء تشغيل AlNassr News Monitor v1.0.0
2024-06-29 15:30:01 - INFO - تم إنشاء جداول قاعدة البيانات
2024-06-29 15:30:02 - INFO - تم بدء المجدول
2024-06-29 15:30:03 - INFO - لوحة التحكم متاحة على http://localhost:8000
```

### الوصول إلى لوحة التحكم:

افتح المتصفح على:
```
http://localhost:8000
```

**بيانات الدخول:**
- المستخدم: `admin`
- كلمة المرور: القيمة في `DASHBOARD_PASSWORD` من `.env`

---

## 🐳 Docker

### 1️⃣ بناء الصورة:

```bash
docker build -t al-nassr-monitor .
```

### 2️⃣ التشغيل باستخدام Docker Compose:

```bash
# أول مرة
docker-compose up -d

# الرجوع إلى الشاشة
docker-compose logs -f

# الإيقاف
docker-compose down
```

### 3️⃣ الوصول إلى التطبيق:

سيكون متاحاً على:
```
http://localhost:8000
```

### 4️⃣ تعديل الإعدادات:

عدّل متغيرات البيئة في `docker-compose.yml` قبل التشغيل.

---

## 🖥️ التشغيل على VPS (Linux)

### 1️⃣ تثبيت المتطلبات:

```bash
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3-pip git curl
```

### 2️⃣ نسخ المشروع:

```bash
cd /opt
sudo git clone https://github.com/nfc1world11-web/AlNassr-News-Monitor.git
sudo chown -R $USER:$USER AlNassr-News-Monitor
cd AlNassr-News-Monitor
```

### 3️⃣ إعداد البيئة:

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env

# عدّل .env بالإعدادات الخاصة بك
nano .env
```

### 4️⃣ إنشاء خدمة systemd:

```bash
# نسخ ملف الخدمة
sudo cp al-nassr-news-monitor.service /etc/systemd/system/

# تحديث systemd
sudo systemctl daemon-reload

# تفعيل الخدمة (تشغيل تلقائي عند بدء النظام)
sudo systemctl enable al-nassr-news-monitor

# بدء الخدمة
sudo systemctl start al-nassr-news-monitor
```

### 5️⃣ التحقق من الحالة:

```bash
# حالة الخدمة
sudo systemctl status al-nassr-news-monitor

# مراقبة السجلات مباشرة
sudo journalctl -u al-nassr-news-monitor -f

# أو قراءة ملف السجل
tail -f logs/app.log
```

### 6️⃣ الأوامر المفيدة:

```bash
# إيقاف الخدمة
sudo systemctl stop al-nassr-news-monitor

# إعادة تشغيل الخدمة
sudo systemctl restart al-nassr-news-monitor

# تعطيل الخدمة (لا تشغيل تلقائي)
sudo systemctl disable al-nassr-news-monitor
```

---

## 🎮 لوحة التحكم

### الواجهة الرئيسية:

تعرض:
- حالة النظام الحالية
- آخر وقت بحث
- عدد الأخبار في آخر دورة
- آخر 20 خبر تم اكتشافه

### المميزات:

✅ **عرض الحالة** - معلومات عن آخر دورة بحث
✅ **السجلات** - جميع العمليات والأخطاء
✅ **الإعدادات** - تعديل البريد وحد الأهمية والمصادر
✅ **البحث اليدوي** - تشغيل فحص فوري
✅ **بريد تجريبي** - إرسال بريد اختبار

---

## ⚙️ الإعدادات المتقدمة

### تغيير الفاصل الزمني:

في `.env`:
```env
CHECK_INTERVAL_MINUTES=5  # اجعلها 10 أو 15 أو أي قيمة تريد
```

### تغيير حد الأهمية:

```env
MINIMUM_RELEVANCE_THRESHOLD=7  # 1-10 (7 = لا ترسل أخبار أقل من 7/10)
```

### تعطيل رسائل "لا جديد":

```env
SEND_NO_NEWS_EMAIL=false  # أو true
```

### استخدام الذكاء الاصطناعي:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

**أو بدون AI:**
```env
AI_PROVIDER=none
```

### مستوى السجلات:

```env
LOG_LEVEL=DEBUG   # DEBUG, INFO, WARNING, ERROR
```

---

## 🔧 حل المشاكل

### ❌ لا يتم إرسال رسائل بريد

**الحل:**
1. تحقق من بيانات Gmail في `.env`
2. تأكد من تفعيل 2FA
3. تأكد من كلمة مرور التطبيق (16 حرف)
4. جرب إرسال بريد اختبار من لوحة التحكم

**أمر الاختبار:**
```bash
source venv/bin/activate
python -c "from src.services.email_service import EmailService; EmailService().send_no_news_email()"
```

### ❌ خطأ في الاتصال بـ OpenAI

**الحل:**
1. تحقق من مفتاح API
2. تأكد من أن الحساب نشط وله رصيد
3. جرب `AI_PROVIDER=none` للقوالب البسيطة

### ❌ قاعدة البيانات تسبب مشاكل

**الحل:**
```bash
rm data/al_nassr_news.db
python src/main.py  # سيعيد إنشاء قاعدة البيانات
```

### ❌ المشروع لا يشتغل على Windows

**الحل:**
```bash
# تأكد من استخدام الأوامر الصحيحة
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

---

## 📞 الدعم والمساعدة

**للإبلاغ عن مشاكل:**
- 🐛 GitHub Issues: https://github.com/nfc1world11-web/AlNassr-News-Monitor/issues
- 📧 البريد: nfc1world11@gmail.com

---

## 📝 الترخيص

هذا المشروع مرخص تحت **MIT License**

---

**تم آخر تحديث:** يونيو 2024  
**الحالة:** ✅ جاهز للإنتاج
