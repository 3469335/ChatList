"""
Модуль для загрузки конфигурации из .env файла
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


def get_api_key(api_id: str) -> str:
    """
    Получить API ключ по имени переменной окружения
    
    Args:
        api_id: Имя переменной окружения (например, 'OPENAI_API_KEY')
    
    Returns:
        Значение API ключа или пустая строка, если не найдено
    """
    return os.getenv(api_id, "")


def get_setting(key: str, default: str = "") -> str:
    """
    Получить настройку из переменных окружения
    
    Args:
        key: Ключ настройки
        default: Значение по умолчанию
    
    Returns:
        Значение настройки или default
    """
    return os.getenv(key, default)


def get_request_timeout() -> int:
    """Получить таймаут запросов в секундах"""
    return int(get_setting("REQUEST_TIMEOUT", "30"))


def get_max_results() -> int:
    """Получить максимальное количество результатов"""
    return int(get_setting("MAX_RESULTS_PER_REQUEST", "10"))

