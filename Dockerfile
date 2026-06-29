FROM python:3.12-slim

WORKDIR /app

# تثبيت المتطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ المشروع
COPY . .

# إنشاء المجلدات المطلوبة
RUN mkdir -p logs data config

# تعيين متغيرات البيئة
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# تشغيل التطبيق
CMD ["python", "src/main.py"]
