"""
__init__.py للمشروع
"""
from src.config import get_settings, ensure_directories
from src.logger import setup_logging, get_logger

# إعداد المجلدات والسجلات
ensure_directories()
setup_logging()

__version__ = "1.0.0"
__author__ = "AlNassr News Monitor Team"
