"""
تسجيل السجلات بشكل احترافي
"""
import logging
import logging.handlers
from pathlib import Path
from pythonjsonlogger import jsonlogger
from src.config import get_settings


def setup_logging():
    """إعداد نظام التسجيل"""
    settings = get_settings()
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(exist_ok=True)
    
    # إنشاء مسجل رئيسي
    logger = logging.getLogger("al_nassr_monitor")
    logger.setLevel(getattr(logging, settings.log_level))
    
    # معالج الملف بصيغة JSON
    file_handler = logging.handlers.RotatingFileHandler(
        settings.log_file,
        maxBytes=10_485_760,  # 10MB
        backupCount=5
    )
    file_formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # معالج وحدة التحكم
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """الحصول على مسجل باسم معين"""
    return logging.getLogger(f"al_nassr_monitor.{name}")
