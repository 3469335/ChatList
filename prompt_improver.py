"""
Модуль для улучшения промтов с помощью AI
"""
import re
import json
import requests
from typing import List, Dict, Optional
from network import APIError
from config import get_api_key, get_request_timeout
import logger


# Системные промпты для улучшения промтов
SYSTEM_PROMPTS = {
    'general': """Ты эксперт по улучшению промптов для AI. Твоя задача - улучшить предоставленный промпт, сделав его более четким, конкретным и эффективным.

Ответь в следующем формате JSON:
{
  "improved": "улучшенный промпт",
  "variants": ["вариант 1", "вариант 2", "вариант 3"]
}

Улучши промпт так, чтобы он:
1. Был более конкретным и понятным
2. Включал необходимый контекст
3. Использовал четкие инструкции
4. Был структурированным, если это уместно""",

    'code': """Ты эксперт по написанию промптов для программирования. Улучши предоставленный промпт для задач программирования.

Ответь в следующем формате JSON:
{
  "improved": "улучшенный промпт для программирования",
  "variants": ["вариант 1", "вариант 2", "вариант 3"]
}

Улучши промпт так, чтобы он:
1. Ясно указывал язык программирования
2. Включал требования к стилю кода
3. Указывал формат ответа (код, объяснение, тесты)
4. Был технически точным""",

    'analysis': """Ты эксперт по написанию промптов для аналитических задач. Улучши предоставленный промпт для анализа данных или текста.

Ответь в следующем формате JSON:
{
  "improved": "улучшенный промпт для анализа",
  "variants": ["вариант 1", "вариант 2", "вариант 3"]
}

Улучши промпт так, чтобы он:
1. Ясно указывал цель анализа
2. Включал критерии оценки
3. Указывал формат вывода (список, таблица, вывод)
4. Был структурированным и логичным""",

    'creative': """Ты эксперт по написанию креативных промптов. Улучши предоставленный промпт для творческих задач.

Ответь в следующем формате JSON:
{
  "improved": "улучшенный креативный промпт",
  "variants": ["вариант 1", "вариант 2", "вариант 3"]
}

Улучши промпт так, чтобы он:
1. Вдохновлял на творчество
2. Включал стиль, тон и атмосферу
3. Указывал желаемый формат (текст, сценарий, идея)
4. Был оригинальным и интересным"""
}


def build_improvement_prompt(original_prompt: str, task_type: str = 'general') -> str:
    """
    Формирует системный промпт для улучшения промта
    
    Args:
        original_prompt: Исходный промпт
        task_type: Тип задачи ('general', 'code', 'analysis', 'creative')
    
    Returns:
        Полный промпт для отправки модели
    """
    system_prompt = SYSTEM_PROMPTS.get(task_type, SYSTEM_PROMPTS['general'])
    
    user_message = f"""Улучши следующий промпт:

{original_prompt}

Верни ответ в формате JSON с ключами 'improved' и 'variants' (массив из 2-3 строк)."""
    
    return system_prompt, user_message


def parse_ai_response(response_text: str) -> Dict[str, any]:
    """
    Парсит ответ AI и извлекает улучшенные варианты промтов
    
    Args:
        response_text: Текст ответа от AI
    
    Returns:
        Словарь с ключами 'improved' и 'variants' (список)
    """
    # Попытка извлечь JSON из ответа (может быть в markdown код-блоках)
    # Сначала пытаемся найти JSON в код-блоках
    code_block_pattern = r'```(?:json)?\s*(\{[\s\S]*?\})'
    code_block_match = re.search(code_block_pattern, response_text, re.DOTALL)
    if code_block_match:
        try:
            json_str = code_block_match.group(1).strip()
            data = json.loads(json_str)
            improved = data.get('improved', '')
            variants = data.get('variants', [])
            
            if improved:
                # Убедиться, что variants - это список
                if isinstance(variants, str):
                    variants = [variants]
                elif not isinstance(variants, list):
                    variants = []
                
                # Ограничить количество вариантов до 3
                variants = variants[:3]
                
                return {
                    'improved': improved.strip(),
                    'variants': [v.strip() if isinstance(v, str) else str(v) for v in variants if v]
                }
        except (json.JSONDecodeError, AttributeError):
            pass
    
    # Если не найден в код-блоке, пытаемся найти обычный JSON
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*"improved"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    json_match = re.search(json_pattern, response_text, re.DOTALL)
    if json_match:
        try:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            improved = data.get('improved', '')
            variants = data.get('variants', [])
            
            if improved:
                if isinstance(variants, str):
                    variants = [variants]
                elif not isinstance(variants, list):
                    variants = []
                
                variants = variants[:3]
                
                return {
                    'improved': improved.strip(),
                    'variants': [v.strip() if isinstance(v, str) else str(v) for v in variants if v]
                }
        except json.JSONDecodeError:
            pass
    
    # Если JSON не найден, попробуем извлечь текст другим способом
    # Ищем улучшенный промпт после ключевых слов
    improved_match = re.search(r'(?:улучшенный|improved|improved prompt)[:：\n]?\s*(.+?)(?:\n\n|\n(?:вариант|variant|alternatives)|$)', 
                               response_text, re.IGNORECASE | re.DOTALL)
    
    if improved_match:
        improved = improved_match.group(1).strip()
    else:
        # Если ничего не найдено, используем весь ответ как улучшенный промпт
        improved = response_text.strip()
    
    # Ищем варианты
    variants = []
    variant_patterns = [
        r'(?:вариант|variant)\s*\d+[:：]?\s*(.+?)(?=\n(?:вариант|variant|\n\n|$))',
        r'(?:альтернатива|alternative)\s*\d+[:：]?\s*(.+?)(?=\n(?:альтернатива|alternative|\n\n|$))',
    ]
    
    for pattern in variant_patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
        if matches:
            variants = [m.strip() for m in matches[:3]]
            break
    
    return {
        'improved': improved,
        'variants': variants if variants else []
    }


def improve_prompt(prompt_text: str, model_name: str, api_key: str, task_type: str = 'general') -> Dict[str, any]:
    """
    Улучшает промпт с помощью AI
    
    Args:
        prompt_text: Исходный текст промпта
        model_name: Название модели для улучшения
        api_key: API ключ
        task_type: Тип задачи ('general', 'code', 'analysis', 'creative')
    
    Returns:
        Словарь с ключами 'improved' и 'variants'
    
    Raises:
        APIError: При ошибках API
        ValueError: При некорректных входных данных
    """
    if not prompt_text or not prompt_text.strip():
        raise ValueError("Промпт не может быть пустым")
    
    if len(prompt_text) > 5000:
        raise ValueError("Промпт слишком длинный (максимум 5000 символов)")
    
    if not api_key:
        raise ValueError("API ключ не указан")
    
    logger.log_api_request(f"Улучшение промта (тип: {task_type})", model_name, len(prompt_text))
    
    try:
        system_prompt, user_message = build_improvement_prompt(prompt_text, task_type)
        
        # Отправляем запрос к OpenRouter с системным промптом и пользовательским сообщением
        response = send_improvement_request(model_name, system_prompt, user_message, api_key)
        
        # Парсим ответ
        result = parse_ai_response(response)
        
        logger.log_info(f"Промт улучшен успешно. Модель: {model_name}")
        return result
        
    except APIError as e:
        logger.log_error(f"Ошибка API при улучшении промта: {str(e)}")
        raise
    except Exception as e:
        logger.log_error(f"Неожиданная ошибка при улучшении промта: {str(e)}")
        raise APIError(f"Ошибка при улучшении промта: {str(e)}")


def generate_prompt_variants(prompt_text: str, model_name: str, api_key: str, count: int = 3) -> List[str]:
    """
    Генерирует варианты переформулировки промпта
    
    Args:
        prompt_text: Исходный текст промпта
        model_name: Название модели
        api_key: API ключ
        count: Количество вариантов (2-5, по умолчанию 3)
    
    Returns:
        Список вариантов промптов
    """
    result = improve_prompt(prompt_text, model_name, api_key, 'general')
    variants = result.get('variants', [])
    
    # Ограничиваем количество вариантов
    count = max(2, min(5, count))
    return variants[:count]


def send_improvement_request(model_name: str, system_prompt: str, user_message: str, api_key: str) -> str:
    """
    Отправляет запрос к OpenRouter API с системным промптом и пользовательским сообщением
    
    Args:
        model_name: Название модели
        system_prompt: Системный промпт
        user_message: Пользовательское сообщение
        api_key: API ключ
    
    Returns:
        Текст ответа модели
    
    Raises:
        APIError: При ошибках API
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/chatlist-app",
        "X-Title": "ChatList"
    }
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=get_request_timeout()
        )
        
        if response.status_code == 404:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error_msg = error_data.get('error', {}).get('message', 'Model not found')
            raise APIError(f"OpenRouter API error: Model '{model_name}' not found (404). {error_msg}")
        
        response.raise_for_status()
        result = response.json()
        
        if 'choices' not in result or len(result['choices']) == 0:
            raise APIError(f"OpenRouter API error: No response from model '{model_name}'")
        
        return result['choices'][0]['message']['content']
    except APIError:
        raise
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                if 'error' in error_data:
                    error_msg = error_data['error'].get('message', error_msg)
            except:
                pass
        raise APIError(f"OpenRouter API error: {error_msg}")
    except (KeyError, IndexError) as e:
        raise APIError(f"Invalid OpenRouter API response: {str(e)}")


def adapt_prompt_for_type(prompt_text: str, prompt_type: str, model_name: str, api_key: str) -> str:
    """
    Адаптирует промпт под определенный тип задачи
    
    Args:
        prompt_text: Исходный текст промпта
        prompt_type: Тип задачи ('code', 'analysis', 'creative')
        model_name: Название модели
        api_key: API ключ
    
    Returns:
        Адаптированный промпт
    """
    if prompt_type not in ['code', 'analysis', 'creative']:
        prompt_type = 'general'
    
    result = improve_prompt(prompt_text, model_name, api_key, prompt_type)
    return result.get('improved', prompt_text)

