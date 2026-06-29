"""
نماذج البيانات الأساسية
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    """نموذج خبر واحد"""
    title: str
    summary: str
    url: str
    canonical_url: Optional[str] = None
    source_name: str
    published_at: datetime
    image_url: Optional[str] = None
    language: str = "ar"
    raw_content: Optional[str] = None
    query_used: Optional[str] = None
    content_hash: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClassificationResult(BaseModel):
    """نتيجة تصنيف الخبر"""
    is_relevant: bool
    relevance_score: float = Field(ge=0, le=10)
    news_type: str  # official, match, transfer, injury, statement, rumor, admin, tournament, general
    is_verified: bool = True
    requires_warning: bool = False
    warning_message: Optional[str] = None
    reason: str


class SentNews(BaseModel):
    """خبر تم إرساله"""
    id: Optional[int] = None
    title: str
    normalized_title: str
    source_name: str
    source_url: str
    canonical_url: Optional[str] = None
    published_at: datetime
    discovered_at: datetime
    content_hash: str
    sent_at: datetime
    email_batch_id: str
    relevance_score: float
    language: str
    news_type: str

    class Config:
        from_attributes = True


class NewsRun(BaseModel):
    """تسجيل دورة بحث"""
    id: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_sources_checked: int
    total_articles_found: int
    total_new_articles: int
    total_articles_sent: int
    status: str  # running, completed, failed
    error_details: Optional[str] = None

    class Config:
        from_attributes = True
