"""
خدمة مسح مواقع الأخبار وجمع الأخبار
"""
import hashlib
from typing import List
from datetime import datetime, timezone
import pytz
from src.models.news import NewsItem
from src.logger import get_logger
from src.config import get_settings

logger = get_logger("news_collector")


class NewsCollector:
    """جامع الأخبار من المصادر المختلفة"""
    
    def __init__(self):
        self.settings = get_settings()
        self.tz = pytz.timezone(self.settings.timezone)
    
    def collect_from_all_sources(self) -> List[NewsItem]:
        """جمع الأخبار من جميع المصادر"""
        all_news: List[NewsItem] = []
        
        try:
            # سيتم تحميل المصادر من config/sources.yaml
            logger.info("بدء جمع الأخبار من جميع المصادر")
            
            # هنا سيتم إضافة منطق جمع الأخبار من كل مصدر
            
            logger.info(f"تم جمع {len(all_news)} خبر")
            return all_news
        
        except Exception as e:
            logger.error(f"خطأ في جمع الأخبار: {str(e)}")
            return []
    
    @staticmethod
    def calculate_content_hash(content: str) -> str:
        """حساب hash لمحتوى الخبر"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def normalize_title(title: str) -> str:
        """تنظيف وتوحيد عنوان الخبر"""
        # إزالة المسافات الزائدة
        title = ' '.join(title.split())
        # تحويل لأحرف صغيرة للمقارنة
        return title.lower().strip()
