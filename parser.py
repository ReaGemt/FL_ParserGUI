import os
import feedparser
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def parse_tasks() -> List[Dict[str, str]]:
    """Парсит RSS-ленту FL.ru и возвращает список задач."""
    rss_url = os.getenv('RSS_URL', 'https://www.fl.ru/rss/all.xml?subcategory=297&category=5')
    try:
        logger.info(f"Получаем RSS-ленту с {rss_url}")
        feed = feedparser.parse(rss_url)

        if feed.bozo:
            logger.error(f"Ошибка парсинга RSS: {feed.bozo_exception}")
            return []

        if not feed.entries:
            logger.warning("Нет данных в RSS-ленте.")
            return []

        return [
            {'Задача': entry.get('title', 'Без названия'), 'Ссылка': entry.get('link', '#')}
            for entry in feed.entries
        ]

    except Exception as e:
        logger.exception("Ошибка при парсинге RSS-ленты:")
        return []