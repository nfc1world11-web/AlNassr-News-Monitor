"""
مزود الأخبار الأساسي - قاعدة لجميع المزودين
"""
from abc import ABC, abstractmethod
from typing import List
from src.models.news import NewsItem


class BaseProvider(ABC):
    """قاعدة لجميع مزودي الأخبار"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def fetch(self, query: str = None) -> List[NewsItem]:
        """جلب الأخبار من المصدر"""
        pass
