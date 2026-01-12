"""
Модуль для логирования
"""
import logging
import os
from datetime import datetime
import version

# Создаем директорию для логов, если её нет
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Настройка логирования
LOG_FILE = os.path.join(LOG_DIR, f"chatlist_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s - ChatList v{version.__version__} - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ChatList')

# Логировать версию при старте
logger.info(f"ChatList v{version.__version__} started")


def log_api_request(model_name: str, prompt: str, success: bool, error: str = None):
    """Логировать запрос к API"""
    if success:
        logger.info(f"API Request - Model: {model_name}, Prompt: {prompt[:100]}..., Status: Success")
    else:
        logger.error(f"API Request - Model: {model_name}, Prompt: {prompt[:100]}..., Error: {error}")


def log_error(message: str, exception: Exception = None):
    """Логировать ошибку"""
    if exception:
        logger.error(f"{message}: {str(exception)}", exc_info=True)
    else:
        logger.error(message)


def log_info(message: str):
    """Логировать информационное сообщение"""
    logger.info(message)

