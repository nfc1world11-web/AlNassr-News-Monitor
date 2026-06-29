# اختبارات المشروع

import pytest
from src.services.deduplication_service import DeduplicationService
from src.services.ai_classifier import AIClassifier
from src.models.news import NewsItem
from datetime import datetime
import pytz


class TestDeduplication:
    """اختبارات خدمة منع التكرار"""
    
    def test_normalize_title(self):
        """اختبار تنظيف العنوان"""
        title = "   هذا   عنوان   به   مسافات   "
        normalized = DeduplicationService._normalize_title(title)
        assert normalized == "هذا عنوان به مسافات"
    
    def test_similarity_calculation(self):
        """اختبار حساب التشابه"""
        a = "النصر يفوز على الهلال"
        b = "النصر يفوز على الهلال"
        similarity = DeduplicationService._calculate_similarity(a, b)
        assert similarity == 1.0
    
    def test_clean_url(self):
        """اختبار تنظيف الرابط"""
        url = "https://example.com/news?utm_source=google&utm_campaign=summer&id=123"
        cleaned = DeduplicationService.clean_url(url)
        assert "utm_source" not in cleaned
        assert "id=123" in cleaned


class TestAIClassifier:
    """اختبارات المصنف الذكي"""
    
    def test_relevance_check_ar(self):
        """اختبار التحقق من الصلة بالعربية"""
        classifier = AIClassifier()
        text = "أخبار جديدة عن نادي النصر السعودي"
        assert classifier._check_relevance(text, "ar") is True
    
    def test_relevance_check_en(self):
        """اختبار التحقق من الصلة بالإنجليزية"""
        classifier = AIClassifier()
        text = "Latest news about Al Nassr FC"
        assert classifier._check_relevance(text, "en") is True
    
    def test_news_type_detection(self):
        """اختبار الكشف عن نوع الخبر"""
        classifier = AIClassifier()
        text = "النصر يفوز في مباراة ودية"
        news_type = classifier._detect_news_type(text)
        assert news_type == "match"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
