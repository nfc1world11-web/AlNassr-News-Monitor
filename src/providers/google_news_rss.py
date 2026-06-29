"""
مزود Google News RSS
"""
import feedparser
from typing import List
from datetime import datetime
import pytz
from src.models.news import NewsItem
from src.providers.base_provider import BaseProvider
from src.logger import get_logger
from src.services.news_collector import NewsCollector

logger = get_logger("google_news_rss")


class GoogleNewsRss(BaseProvider):
    """مزود أخبار Google News RSS"""
    
    QUERIES_AR = [
        "النصر السعودي",
        "نادي النصر",
        "Al Nassr",
        "النصر الرياض"
    ]
    
    QUERIES_EN = [
        "Al Nassr",
        "Al Nassr FC",
        "Cristiano Ronaldo Al Nassr",
        "Sadio Mane Al Nassr"
    ]
    
    def __init__(self):
        super().__init__("Google News RSS")
        self.tz = pytz.timezone("Asia/Riyadh")
    
    def fetch(self, query: str = None) -> List[NewsItem]:
        """جلب الأخبار من Google News RSS"""
        all_news: List[NewsItem] = []
        
        queries = self.QUERIES_AR + self.QUERIES_EN
        
        for q in queries:
            try:
                url = f"https://news.google.com/rss/search?q={q}"
                logger.info(f"جلب الأخبار من Google News: {q}")
                
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:10]:  # أول 10 نتائج
                    try:
                        published_at = datetime(*entry.published_parsed[:6]).replace(tzinfo=pytz.UTC)
                        
                        news = NewsItem(
                            title=entry.title,
                            summary=entry.summary[:500],
                            url=entry.link,
                            canonical_url=entry.link,
                            source_name="Google News",
                            published_at=published_at,
                            language="ar" if any(c for c in q if ord(c) > 127) else "en",
                            query_used=q,
                            content_hash=NewsCollector.calculate_content_hash(entry.title + entry.summary)
                        )
                        
                        all_news.append(news)
                    except Exception as e:
                        logger.warning(f"خطأ في معالجة الخبر من Google News: {str(e)}")
                        continue
            
            except Exception as e:
                logger.error(f"خطأ في جلب أخبار Google News للاستعلام '{q}': {str(e)}")
                continue
        
        logger.info(f"تم جلب {len(all_news)} خبر من Google News")
        return all_news
