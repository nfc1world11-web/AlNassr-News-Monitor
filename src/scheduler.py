"""
مجدول المهام
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import pytz
from src.logger import get_logger
from src.config import get_settings
from src.database import db, NewsRunDB
from src.services.news_collector import NewsCollector
from src.services.deduplication_service import DeduplicationService
from src.services.ai_classifier import AIClassifier
from src.services.email_service import EmailService
from sqlalchemy.orm import Session
import uuid

logger = get_logger("scheduler")


class Scheduler:
    """جدول المهام الرئيسي"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.settings = get_settings()
        self.tz = pytz.timezone(self.settings.timezone)
        self.is_running = False
        
        # تهيئة الخدمات
        self.news_collector = NewsCollector()
        self.dedup_service = DeduplicationService()
        self.classifier = AIClassifier()
        self.email_service = EmailService()
    
    def start(self):
        """بدء المجدول"""
        logger.info(f"بدء المجدول - الفاصل الزمني: {self.settings.check_interval_minutes} دقيقة")
        
        # إضافة مهمة البحث عن الأخبار
        self.scheduler.add_job(
            self.fetch_and_send_news,
            IntervalTrigger(minutes=self.settings.check_interval_minutes),
            id='news_check',
            name='البحث عن الأخبار وإرسالها',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("✅ تم بدء المجدول بنجاح")
    
    def stop(self):
        """إيقاف المجدول"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("✅ تم إيقاف المجدول")
    
    def fetch_and_send_news(self):
        """جلب الأخبار وتصنيفها وإرسالها"""
        session = db.get_session()
        batch_id = str(uuid.uuid4())
        
        try:
            # تسجيل بدء الدورة
            run = NewsRunDB(
                started_at=datetime.now(pytz.UTC),
                status="running"
            )
            session.add(run)
            session.commit()
            
            logger.info(f"🔍 بدء دورة البحث {batch_id}")
            
            # 1. جمع الأخبار
            all_news = self.news_collector.collect_from_all_sources()
            run.total_articles_found = len(all_news)
            
            if not all_news:
                logger.info("📭 لم يتم العثور على أخبار جديدة")
                if self.settings.send_no_news_email:
                    self.email_service.send_no_news_email()
                run.status = "completed"
                session.commit()
                return
            
            logger.info(f"📰 تم جمع {len(all_news)} خبر")
            
            # 2. تصنيف وفلترة الأخبار
            relevant_news = []
            for news in all_news:
                classification = self.classifier.classify(news)
                
                if classification.is_relevant and classification.relevance_score >= self.settings.minimum_relevance_threshold:
                    # إنشاء كائن الخبر المرسل
                    from src.models.news import SentNews
                    sent_news = SentNews(
                        title=news.title,
                        normalized_title=self.news_collector.normalize_title(news.title),
                        source_name=news.source_name,
                        source_url=news.url,
                        canonical_url=news.canonical_url,
                        published_at=news.published_at,
                        discovered_at=datetime.now(pytz.UTC),
                        content_hash=news.content_hash or self.news_collector.calculate_content_hash(news.title),
                        sent_at=datetime.now(pytz.UTC),
                        email_batch_id=batch_id,
                        relevance_score=classification.relevance_score,
                        language=news.language,
                        news_type=classification.news_type
                    )
                    
                    # 3. التحقق من عدم التكرار
                    is_dup, _ = self.dedup_service.is_duplicate(news, session)
                    if not is_dup:
                        relevant_news.append(sent_news)
            
            run.total_new_articles = len(relevant_news)
            
            # 4. إرسال البريد
            if relevant_news:
                if self.email_service.send_news_digest(relevant_news, batch_id):
                    # حفظ الأخبار المرسلة
                    for news in relevant_news:
                        db_news = NewsRunDB.__table__.insert().values(
                            title=news.title,
                            normalized_title=news.normalized_title,
                            source_name=news.source_name,
                            source_url=news.source_url,
                            canonical_url=news.canonical_url,
                            published_at=news.published_at,
                            discovered_at=news.discovered_at,
                            content_hash=news.content_hash,
                            sent_at=news.sent_at,
                            email_batch_id=news.email_batch_id,
                            relevance_score=news.relevance_score,
                            language=news.language,
                            news_type=news.news_type
                        )
                        session.execute(db_news)
                    
                    run.total_articles_sent = len(relevant_news)
                    logger.info(f"✅ تم إرسال {len(relevant_news)} خبر عبر البريد الإلكتروني")
                else:
                    logger.error("❌ فشل إرسال البريد الإلكتروني")
                    run.error_details = "فشل إرسال البريد الإلكتروني"
            else:
                logger.info("📭 لم تتمكن من العثور على أخبار جديدة وذات صلة")
                if self.settings.send_no_news_email:
                    self.email_service.send_no_news_email()
            
            run.completed_at = datetime.now(pytz.UTC)
            run.status = "completed"
            session.commit()
            
            logger.info(f"✅ انتهت دورة البحث {batch_id}")
        
        except Exception as e:
            logger.error(f"❌ خطأ في دورة البحث: {str(e)}")
            run.status = "failed"
            run.error_details = str(e)
            run.completed_at = datetime.now(pytz.UTC)
            session.commit()
        
        finally:
            session.close()
