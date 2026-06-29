"""
خدمة إرسال البريد الإلكتروني
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
import pytz
from jinja2 import Template
from src.models.news import NewsItem, SentNews
from src.logger import get_logger
from src.config import get_settings

logger = get_logger("email_service")


class EmailService:
    """خدمة إرسال البريد الإلكتروني"""
    
    def __init__(self):
        self.settings = get_settings()
        self.tz = pytz.timezone(self.settings.timezone)
    
    def send_news_digest(self, news_items: List[SentNews], batch_id: str) -> bool:
        """إرسال بريد يحتوي على مجموعة أخبار"""
        try:
            # ترتيب الأخبار حسب الأهمية ثم الحداثة
            sorted_news = sorted(
                news_items,
                key=lambda x: (-x.relevance_score, -x.published_at.timestamp())
            )
            
            html_content = self._generate_news_digest_html(sorted_news)
            subject = f"أخبار النصر السعودي - {datetime.now(self.tz).strftime('%d/%m/%Y %H:%M')}"
            
            return self._send_email(subject, html_content)
        
        except Exception as e:
            logger.error(f"خطأ في إرسال بريد الأخبار: {str(e)}")
            return False
    
    def send_no_news_email(self) -> bool:
        """إرسال بريد عندما لا توجد أخبار جديدة"""
        try:
            if not self.settings.send_no_news_email:
                return True
            
            current_time = datetime.now(self.tz).strftime('%d/%m/%Y %H:%M')
            html_content = f"""
            <html dir="rtl">
                <body style="font-family: Arial; background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                        <h2 style="color: #1a1a1a; text-align: right;">لا جديد بشأن النصر السعودي</h2>
                        <p style="color: #666; text-align: right; font-size: 16px;">
                            تم البحث في المصادر المحددة حتى <strong>{current_time}</strong>، ولم يتم العثور على أخبار جديدة مرتبطة بنادي النصر السعودي لم يتم إرسالها سابقاً.
                        </p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #999; text-align: center; font-size: 12px;">
                            AlNassr News Monitor - نظام مراقبة أخبار النصر السعودي
                        </p>
                    </div>
                </body>
            </html>
            """
            
            subject = "لا جديد بشأن النصر السعودي"
            return self._send_email(subject, html_content)
        
        except Exception as e:
            logger.error(f"خطأ في إرسال بريد 'لا جديد': {str(e)}")
            return False
    
    def _generate_news_digest_html(self, news_items: List[SentNews]) -> str:
        """توليد محتوى HTML للبريد"""
        news_html = ""
        
        for i, news in enumerate(news_items, 1):
            badge = ""
            if news.news_type == "official":
                badge = '🔴 رسمي'
            elif news.news_type == "rumor":
                badge = '⚠️ غير مؤكد'
            elif news.news_type == "match":
                badge = '⚽ مباراة'
            elif news.news_type == "transfer":
                badge = '🔄 انتقال'
            
            news_html += f"""
            <div style="background-color: #f9f9f9; padding: 15px; margin-bottom: 15px; border-right: 4px solid #c41e3a; border-radius: 5px;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #1a1a1a; font-size: 18px; text-align: right; flex: 1;">{news.title}</h3>
                    <span style="background-color: #e8e8e8; color: #333; padding: 5px 10px; border-radius: 5px; font-size: 12px; margin-right: 10px; white-space: nowrap;">{badge}</span>
                </div>
                <div style="color: #666; font-size: 13px; margin-bottom: 10px; text-align: right;">
                    <span style="margin-left: 20px;">📰 {news.source_name}</span>
                    <span style="margin-left: 20px;">⏰ {news.published_at.strftime('%H:%M - %d/%m/%Y')}</span>
                </div>
                <p style="color: #333; line-height: 1.6; text-align: right; margin: 10px 0;">{news.summary if hasattr(news, 'summary') else ''}</p>
                <div style="text-align: right; margin-top: 10px;">
                    <a href="#" style="color: #c41e3a; text-decoration: none; font-weight: bold;">قراءة الخبر من المصدر →</a>
                </div>
            </div>
            """
        
        html = f"""
        <html dir="rtl">
            <body style="font-family: Arial; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h1 style="color: #c41e3a; text-align: right; border-bottom: 3px solid #c41e3a; padding-bottom: 10px;">
                        ⚽ أخبار جديدة عن نادي النصر السعودي
                    </h1>
                    {news_html}
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #999; text-align: center; font-size: 12px;">
                        AlNassr News Monitor - نظام مراقبة أخبار النصر السعودي
                    </p>
                </div>
            </body>
        </html>
        """
        
        return html
    
    def _send_email(self, subject: str, html_content: str) -> bool:
        """إرسال البريد الفعلي عبر SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.settings.smtp_from
            msg['To'] = self.settings.email_recipient
            
            # إضافة المحتوى بصيغة HTML
            part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part)
            
            # الاتصال بخادم SMTP وإرسال البريد
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
                server.starttls()
                server.login(self.settings.smtp_username, self.settings.smtp_password)
                server.send_message(msg)
            
            logger.info(f"تم إرسال البريد بنجاح: {subject}")
            return True
        
        except Exception as e:
            logger.error(f"خطأ في إرسال البريد: {str(e)}")
            return False
