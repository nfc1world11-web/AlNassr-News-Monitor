"""
خدمة منع تكرار الأخبار
"""
from typing import Optional, Tuple
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database import SentNewsDB, db
from src.models.news import NewsItem
from src.logger import get_logger
from src.config import get_settings
from urllib.parse import urlparse, parse_qs

logger = get_logger("deduplication")


class DeduplicationService:
    """خدمة منع تكرار الأخبار"""
    
    SIMILARITY_THRESHOLD = 0.85  # 85% تشابه
    
    def __init__(self):
        self.settings = get_settings()
    
    def is_duplicate(self, news: NewsItem, session: Session) -> Tuple[bool, Optional[SentNewsDB]]:
        """التحقق من أن الخبر مكرر أم لا"""
        # 1. التحقق من الرابط المباشر
        existing = session.query(SentNewsDB).filter(
            SentNewsDB.source_url == news.url
        ).first()
        
        if existing:
            logger.info(f"خبر مكرر: رابط مطابق - {news.title}")
            return True, existing
        
        # 2. التحقق من canonical URL
        if news.canonical_url:
            existing = session.query(SentNewsDB).filter(
                SentNewsDB.canonical_url == news.canonical_url
            ).first()
            if existing:
                logger.info(f"خبر مكرر: canonical URL مطابق - {news.title}")
                return True, existing
        
        # 3. التحقق من hash المحتوى
        if news.content_hash:
            existing = session.query(SentNewsDB).filter(
                SentNewsDB.content_hash == news.content_hash
            ).first()
            if existing:
                logger.info(f"خبر مكرر: hash مطابق - {news.title}")
                return True, existing
        
        # 4. التحقق من تشابه العنوان
        normalized_title = self._normalize_title(news.title)
        similar = session.query(SentNewsDB).filter(
            SentNewsDB.published_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        for existing in similar:
            similarity = self._calculate_similarity(
                normalized_title,
                self._normalize_title(existing.normalized_title)
            )
            if similarity >= self.SIMILARITY_THRESHOLD:
                logger.info(f"خبر مكرر: تشابه عنوان {similarity*100:.1f}% - {news.title}")
                return True, existing
        
        return False, None
    
    @staticmethod
    def _normalize_title(title: str) -> str:
        """تنظيف العنوان للمقارنة"""
        return ' '.join(title.split()).lower().strip()
    
    @staticmethod
    def _calculate_similarity(a: str, b: str) -> float:
        """حساب نسبة التشابه بين نصين"""
        return SequenceMatcher(None, a, b).ratio()
    
    @staticmethod
    def clean_url(url: str) -> str:
        """تنظيف الرابط من معاملات التتبع"""
        parsed = urlparse(url)
        # إزالة معاملات التتبع الشهيرة
        keep_params = {k: v for k, v in parse_qs(parsed.query).items() 
                       if k not in ['utm_source', 'utm_campaign', 'utm_medium', 'utm_content', 'utm_term', 'fbclid', 'gclid']}
        
        if keep_params:
            # إعادة بناء query string
            new_query = '&'.join([f"{k}={v[0]}" for k, v in keep_params.items()])
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
        else:
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
