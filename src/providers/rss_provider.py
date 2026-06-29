"""
مزود RSS عام
"""
import feedparser
from typing import List, Dict, Any
from datetime import datetime
import pytz
from src.models.news import NewsItem
from src.providers.base_provider import BaseProvider
from src.logger import get_logger
from src.services.news_collector import NewsCollector

logger = get_logger("rss_provider")


class RSSProvider(BaseProvider):
    """مزود RSS عام"""
    
    def __init__(self, name: str, url: str, priority: int = 5):
        super().__init__(name)
        self.url = url
        self.priority = priority
        self.tz = pytz.timezone("Asia/Riyadh")
    
    def fetch(self, query: str = None) -> List[NewsItem]:
        """جلب الأخبار من مصدر RSS"""
        all_news: List[NewsItem] = []
        
        try:
            logger.info(f"جلب الأخبار من {self.name}: {self.url}")
            
            feed = feedparser.parse(self.url)
            
            if not feed.entries:
                logger.warning(f"لم يتم العثور على أخبار من {self.name}")
                return all_news
            
            for entry in feed.entries[:20]:  # أول 20 خبر
                try:
                    # محاولة الحصول على تاريخ النشر
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6]).replace(tzinfo=pytz.UTC)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6]).replace(tzinfo=pytz.UTC)
                    else:
                        published_at = datetime.now(pytz.UTC)
                    
                    summary = entry.get('summary', '')[:500]
                    if not summary and hasattr(entry, 'description'):
                        summary = entry.description[:500]
                    
                    news = NewsItem(
                        title=entry.get('title', 'بدون عنوان'),
                        summary=summary,
                        url=entry.get('link', ''),
                        canonical_url=entry.get('link', ''),
                        source_name=self.name,
                        published_at=published_at,
                        image_url=self._extract_image(entry),
                        language="ar",  # يتم تحديده لاحقاً
                        query_used=self.name,
                        content_hash=NewsCollector.calculate_content_hash(
                            entry.get('title', '') + summary
                        )
                    )
                    
                    all_news.append(news)
                
                except Exception as e:
                    logger.warning(f"خطأ في معالجة الخبر من {self.name}: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"خطأ في جلب أخبار {self.name}: {str(e)}")
        
        logger.info(f"تم جلب {len(all_news)} خبر من {self.name}")
        return all_news
    
    @staticmethod
    def _extract_image(entry: Dict[str, Any]) -> str:
        """استخراج صورة من الخبر إن وجدت"""
        if hasattr(entry, 'media_content') and entry.media_content:
            return entry.media_content[0]['url']
        if 'image' in entry:
            return entry['image']['href']
        return None
