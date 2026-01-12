"""
Модуль для загрузки конфигурации из .env файла
"""
import os
import sys
import shutil
from dotenv import load_dotenv

# Определяем путь к директории приложения
if getattr(sys, 'frozen', False):
    # Если запущено как исполняемый файл (PyInstaller)
    APP_DIR = os.path.dirname(sys.executable)
else:
    # Если запущено как скрипт
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Путь к .env файлу
ENV_FILE = os.path.join(APP_DIR, '.env')
ENV_EXAMPLE_FILE = os.path.join(APP_DIR, '.env.example')

# Если .env не существует, но есть .env.example, копируем его
if not os.path.exists(ENV_FILE) and os.path.exists(ENV_EXAMPLE_FILE):
    try:
        shutil.copy2(ENV_EXAMPLE_FILE, ENV_FILE)
    except Exception:
        pass  # Игнорируем ошибки копирования

# Загружаем переменные окружения из .env файла
load_dotenv(ENV_FILE)


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

