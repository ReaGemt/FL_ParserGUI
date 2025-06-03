import os
import feedparser
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s, %(levelname)s, %(message)s')
logger = logging.getLogger(__name__)


def parse_tasks():
    """
    Парсим RSS-ленту с задачами с сайта fl.ru.
    URL берётся из переменной окружения, либо используется значение по умолчанию.
    """
    rss_url = os.getenv('RSS_URL', 'https://www.fl.ru/rss/all.xml?subcategory=297&category=5')
    try:
        logger.info(f"Получаем RSS-ленту с {rss_url}")
        feed = feedparser.parse(rss_url)

        if feed.bozo:
            logger.error("Ошибка при парсинге RSS-ленты.")
            return []

        if not feed.entries:
            logger.warning("Нет данных в RSS-ленте.")
            return []

        work = []
        for entry in feed.entries:
            task_name = entry.get('title', 'Без названия')
            link = entry.get('link', '#')
            work.append({
                'Задача': task_name,
                'Ссылка': link
            })

        logger.info(f"Найдено {len(work)} задач(и) в RSS-ленте.")
        return work

    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return []
