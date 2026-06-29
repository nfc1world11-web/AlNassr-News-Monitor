"""
ملف البداية الرئيسي
"""
import asyncio
import sys
from pathlib import Path

# إضافة المسار الحالي إلى sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings, ensure_directories
from src.database import db
from src.logger import setup_logging, get_logger
from src.scheduler import Scheduler
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
from datetime import datetime
import pytz

# إعداد السجلات
setup_logging()
logger = get_logger("main")

# إعداد الإعدادات
ensure_directories()
settings = get_settings()

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="AlNassr News Monitor",
    description="نظام مراقبة أخبار نادي النصر السعودي",
    version=settings.app_version
)

# متغير عام للمجدول
scheduler = None


@app.on_event("startup")
async def startup_event():
    """عند بدء التطبيق"""
    global scheduler
    
    logger.info("="*60)
    logger.info(f"🚀 بدء تشغيل {settings.app_name} v{settings.app_version}")
    logger.info("="*60)
    
    # إنشاء قاعدة البيانات
    try:
        db.init_db()
        logger.info("✅ تم إنشاء قاعدة البيانات")
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء قاعدة البيانات: {str(e)}")
    
    # بدء المجدول
    if settings.scheduler_enabled:
        try:
            scheduler = Scheduler()
            scheduler.start()
            logger.info("✅ تم بدء المجدول")
        except Exception as e:
            logger.error(f"❌ خطأ في بدء المجدول: {str(e)}")
    
    logger.info(f"🌐 لوحة التحكم متاحة على http://{settings.web_host}:{settings.web_port}")


@app.on_event("shutdown")
async def shutdown_event():
    """عند إيقاف التطبيق"""
    global scheduler
    
    logger.info("🛑 إيقاف التطبيق...")
    
    if scheduler:
        scheduler.stop()
        logger.info("✅ تم إيقاف المجدول")
    
    db.close()
    logger.info("✅ تم إغلاق قاعدة البيانات")


# ==================== مسارات الـ API ====================

@app.get("/health")
async def health_check():
    """فحص صحة الخدمة"""
    tz = pytz.timezone(settings.timezone)
    return JSONResponse({
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(tz).isoformat(),
        "scheduler_running": scheduler.is_running if scheduler else False
    })


@app.get("/")
async def root():
    """الصفحة الرئيسية - إعادة التوجيه إلى لوحة التحكم"""
    return JSONResponse({
        "message": "مرحباً بك في AlNassr News Monitor",
        "docs": "/docs",
        "health": "/health"
    })


@app.get("/api/status")
async def get_status():
    """الحصول على حالة النظام"""
    session = db.get_session()
    try:
        # آخر دورة بحث
        from src.database import NewsRunDB
        last_run = session.query(NewsRunDB).order_by(NewsRunDB.started_at.desc()).first()
        
        return JSONResponse({
            "status": "running",
            "last_run": {
                "started_at": last_run.started_at.isoformat() if last_run else None,
                "completed_at": last_run.completed_at.isoformat() if last_run and last_run.completed_at else None,
                "total_news_sent": last_run.total_articles_sent if last_run else 0
            } if last_run else None
        })
    finally:
        session.close()


@app.get("/api/news/sent")
async def get_sent_news(limit: int = 50):
    """الحصول على آخر الأخبار المرسلة"""
    session = db.get_session()
    try:
        from src.database import SentNewsDB
        news = session.query(SentNewsDB).order_by(SentNewsDB.sent_at.desc()).limit(limit).all()
        
        return JSONResponse({
            "count": len(news),
            "news": [
                {
                    "title": n.title,
                    "source": n.source_name,
                    "sent_at": n.sent_at.isoformat(),
                    "type": n.news_type,
                    "relevance_score": n.relevance_score
                }
                for n in news
            ]
        })
    finally:
        session.close()


def main():
    """بدء التطبيق"""
    logger.info(f"بدء تشغيل الخادم على {settings.web_host}:{settings.web_port}")
    
    uvicorn.run(
        app,
        host=settings.web_host,
        port=settings.web_port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
