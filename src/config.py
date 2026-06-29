"""
إعدادات التطبيق
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """إعدادات التطبيق الرئيسية"""
    
    # قاعدة البيانات
    database_url: str = "sqlite:///./data/al_nassr_news.db"
    
    # البريد الإلكتروني
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "nfc1world11@gmail.com"
    smtp_password: str
    smtp_from: str = "nfc1world11@gmail.com"
    email_recipient: str = "nfc1world11@gmail.com"
    email_recipient_name: str = "مراقب النصر"
    send_no_news_email: bool = True
    
    # الذكاء الاصطناعي
    ai_provider: str = "openai"  # openai, anthropic, none
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    anthropic_api_key: Optional[str] = None
    minimum_relevance_threshold: int = 7
    
    # التطبيق
    app_name: str = "AlNassr News Monitor"
    app_version: str = "1.0.0"
    timezone: str = "Asia/Riyadh"
    check_interval_minutes: int = 5
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # المجدول
    scheduler_enabled: bool = True
    scheduler_workers: int = 1
    
    # لوحة التحكم
    web_host: str = "0.0.0.0"
    web_port: int = 8000
    dashboard_username: str = "admin"
    dashboard_password: str = "change-me"
    dashboard_enabled: bool = True
    
    # المصادر
    sources_config_file: str = "config/sources.yaml"
    
    # إعادة المحاولة
    max_retries: int = 3
    retry_delay_seconds: int = 5
    
    # تنبيهات الأخطاء
    error_alert_enabled: bool = True
    error_alert_threshold: int = 3
    error_alert_email: str = "nfc1world11@gmail.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """الحصول على الإعدادات المخزنة مؤقتاً"""
    return Settings()


def ensure_directories():
    """التأكد من وجود المجلدات الضرورية"""
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)
    Path("src/templates").mkdir(exist_ok=True)
