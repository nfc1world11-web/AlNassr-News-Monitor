"""
خدمة التصنيف الذكي باستخدام AI
"""
from typing import Optional
from src.models.news import NewsItem, ClassificationResult
from src.logger import get_logger
from src.config import get_settings

logger = get_logger("ai_classifier")


class AIClassifier:
    """مصنف الأخبار باستخدام الذكاء الاصطناعي"""
    
    KEYWORDS_AL_NASSR = {
        'ar': [
            'النصر', 'نادي النصر', 'الفريق الأول', 'الرياض',
            'كريستيانو رونالدو', 'كريستيانو', 'رونالدو',
            'ساديو ماني', 'ماني', 'تاليسكا', 'عبدالفتاح',
            'المدرب', 'الإدارة', 'النصراوي', 'الكوكب الدري'
        ],
        'en': [
            'Al Nassr', 'Al-Nassr', 'Nassr', 'Cristiano Ronaldo', 'Ronaldo',
            'Sadio Mane', 'Mane', 'Talisca', 'Abdulfattah',
            'Riyadh', 'Saudi Arabia', 'Al Nassr FC', 'Saudi Pro League'
        ]
    }
    
    NEWS_TYPES = {
        'official': ['رسمي', 'بيان', 'الموقع الرسمي'],
        'match': ['مباراة', 'نتيجة', 'لقاء', 'ديربي'],
        'transfer': ['انتقال', 'تعاقد', 'عقد', 'صفقة', 'transfer'],
        'injury': ['إصابة', 'دخول الإصابة', 'الملعب الطبي'],
        'statement': ['تصريح', 'تعليق', 'قال'],
        'rumor': ['إشاعة', 'قد يصل', 'من المتوقع', 'rumor'],
        'admin': ['إدارة', 'حوكمة', 'قرار'],
        'tournament': ['بطولة', 'ترتيب', 'الدوري'],
        'general': ['خبر عام', 'نشاط']
    }
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        
        if self.settings.ai_provider == "openai" and self.settings.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.settings.openai_api_key)
                logger.info("تم تحميل OpenAI client")
            except ImportError:
                logger.warning("لم يتم العثور على مكتبة OpenAI")
    
    def classify(self, news: NewsItem) -> ClassificationResult:
        """تصنيف الخبر"""
        
        # إذا كان لدينا API key، استخدم AI
        if self.client:
            return self._classify_with_ai(news)
        else:
            # وإلا استخدم قواعد نصية بسيطة
            return self._classify_with_rules(news)
    
    def _classify_with_rules(self, news: NewsItem) -> ClassificationResult:
        """تصنيف باستخدام قواعد نصية"""
        
        text = f"{news.title} {news.summary}".lower()
        
        # التحقق من الصلة بالنادي
        is_relevant = self._check_relevance(text, news.language)
        
        if not is_relevant:
            return ClassificationResult(
                is_relevant=False,
                relevance_score=2,
                news_type="general",
                reason="الخبر لا يتعلق بنادي النصر السعودي"
            )
        
        # تحديد نوع الخبر
        news_type = self._detect_news_type(text)
        
        # تحديد درجة الأهمية
        relevance_score = self._calculate_relevance_score(text, news_type)
        
        # التحقق من التحقق من الخبر
        is_verified = not any(keyword in text for keyword in self.NEWS_TYPES['rumor'])
        
        return ClassificationResult(
            is_relevant=True,
            relevance_score=relevance_score,
            news_type=news_type,
            is_verified=is_verified,
            requires_warning=not is_verified,
            warning_message="⚠️ خبر غير مؤكد" if not is_verified else None,
            reason="تم تصنيف الخبر بناءً على القواعد النصية"
        )
    
    def _classify_with_ai(self, news: NewsItem) -> ClassificationResult:
        """تصنيف باستخدام OpenAI"""
        try:
            prompt = f"""
قيم الخبر التالي المتعلق بنادي النصر السعودي:

العنوان: {news.title}
الملخص: {news.summary}

أجب بصيغة JSON:
{{
  "is_relevant": boolean (هل الخبر فعلاً عن النصر السعودي؟),
  "relevance_score": number (1-10),
  "news_type": string (official, match, transfer, injury, statement, rumor, admin, tournament, general),
  "is_verified": boolean,
  "requires_warning": boolean,
  "reason": string
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return ClassificationResult(**result)
        
        except Exception as e:
            logger.error(f"خطأ في التصنيف بـ AI: {str(e)}")
            # العودة للقواعس النصية
            return self._classify_with_rules(news)
    
    def _check_relevance(self, text: str, language: str) -> bool:
        """التحقق من صلة الخبر بالنادي"""
        keywords = self.KEYWORDS_AL_NASSR.get(language, self.KEYWORDS_AL_NASSR['ar'])
        return any(keyword in text for keyword in keywords)
    
    def _detect_news_type(self, text: str) -> str:
        """الكشف عن نوع الخبر"""
        for news_type, keywords in self.NEWS_TYPES.items():
            if any(keyword in text for keyword in keywords):
                return news_type
        return "general"
    
    def _calculate_relevance_score(self, text: str, news_type: str) -> float:
        """حساب درجة الأهمية"""
        score = 5.0
        
        # إضافة نقاط بناءً على النوع
        if news_type in ['official', 'match', 'transfer']:
            score += 3.0
        elif news_type in ['injury', 'statement']:
            score += 2.0
        elif news_type == 'rumor':
            score -= 2.0
        
        # الحد بين 1 و 10
        return max(1.0, min(10.0, score))
