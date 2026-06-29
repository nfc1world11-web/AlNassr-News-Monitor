"""
إدارة قاعدة البيانات
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from src.config import get_settings
from src.logger import get_logger

logger = get_logger("database")

Base = declarative_base()


class SentNewsDB(Base):
    """جدول الأخبار المرسلة"""
    __tablename__ = "sent_news"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    normalized_title = Column(String(500), nullable=False, index=True)
    source_name = Column(String(200), nullable=False)
    source_url = Column(String(2000), nullable=False, unique=True, index=True)
    canonical_url = Column(String(2000), nullable=True, index=True)
    published_at = Column(DateTime, nullable=False, index=True)
    discovered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    content_hash = Column(String(64), nullable=False, index=True)
    sent_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    email_batch_id = Column(String(100), nullable=False, index=True)
    relevance_score = Column(Float, nullable=False)
    language = Column(String(10), default="ar")
    news_type = Column(String(50), nullable=False)


class NewsRunDB(Base):
    """جدول تسجيل دورات البحث"""
    __tablename__ = "news_runs"
    
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_sources_checked = Column(Integer, default=0)
    total_articles_found = Column(Integer, default=0)
    total_new_articles = Column(Integer, default=0)
    total_articles_sent = Column(Integer, default=0)
    status = Column(String(50), default="running")  # running, completed, failed
    error_details = Column(Text, nullable=True)


class Database:
    """مدير قاعدة البيانات"""
    
    def __init__(self):
        settings = get_settings()
        self.engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def init_db(self):
        """إنشاء جميع الجداول"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("تم إنشاء جداول قاعدة البيانات")
    
    def get_session(self) -> Session:
        """الحصول على جلسة جديدة"""
        return self.SessionLocal()
    
    def close(self):
        """إغلاق الاتصال"""
        self.engine.dispose()


# متغير عام لقاعدة البيانات
db = Database()
