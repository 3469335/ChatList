"""
Модуль для отправки HTTP-запросов к API нейросетей
"""
import requests
import json
from typing import Dict, Optional
from config import get_api_key, get_request_timeout


class APIError(Exception):
    """Исключение для ошибок API"""
    pass


def send_openai_request(model_name: str, prompt: str, api_key: str) -> str:
    """
    Отправить запрос к OpenAI API
    
    Args:
        model_name: Название модели (например, 'gpt-4')
        prompt: Текст промта
        api_key: API ключ
    
    Returns:
        Текст ответа модели
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=get_request_timeout()
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        raise APIError(f"OpenAI API error: {str(e)}")
    except (KeyError, IndexError) as e:
        raise APIError(f"Invalid OpenAI API response: {str(e)}")


def send_deepseek_request(model_name: str, prompt: str, api_key: str) -> str:
    """
    Отправить запрос к DeepSeek API
    
    Args:
        model_name: Название модели
        prompt: Текст промта
        api_key: API ключ
    
    Returns:
        Текст ответа модели
    """
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=get_request_timeout()
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        raise APIError(f"DeepSeek API error: {str(e)}")
    except (KeyError, IndexError) as e:
        raise APIError(f"Invalid DeepSeek API response: {str(e)}")


def send_openrouter_request(model_name: str, prompt: str, api_key: str) -> str:
    """
    Отправить запрос к OpenRouter API
    
    Args:
        model_name: Название модели (например, 'openai/gpt-4')
        prompt: Текст промта
        api_key: API ключ
    
    Returns:
        Текст ответа модели
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/chatlist-app",  # Опционально
        "X-Title": "ChatList"  # Опционально
    }
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=get_request_timeout()
        )
        
        # Улучшенная обработка ошибок
        if response.status_code == 404:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error_msg = error_data.get('error', {}).get('message', 'Model not found')
            raise APIError(f"OpenRouter API error: Model '{model_name}' not found (404). {error_msg}")
        
        response.raise_for_status()
        result = response.json()
        
        # Проверка наличия ответа
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


def send_groq_request(model_name: str, prompt: str, api_key: str) -> str:
    """
    Отправить запрос к Groq API
    
    Args:
        model_name: Название модели
        prompt: Текст промта
        api_key: API ключ
    
    Returns:
        Текст ответа модели
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=get_request_timeout()
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        raise APIError(f"Groq API error: {str(e)}")
    except (KeyError, IndexError) as e:
        raise APIError(f"Invalid Groq API response: {str(e)}")


def send_request(model: Dict, prompt: str) -> str:
    """
    Универсальная функция для отправки запроса к API модели
    
    Args:
        model: Словарь с информацией о модели (name, api_url, api_id, model_type)
        prompt: Текст промта
    
    Returns:
        Текст ответа модели
    
    Raises:
        APIError: При ошибке запроса
    """
    api_key = get_api_key(model['api_id'])
    if not api_key:
        raise APIError(f"API key not found for {model['api_id']}")
    
    model_type = model.get('model_type', '').lower()
    model_name = model.get('name', '')
    api_url = model.get('api_url', '').lower()
    
    # Определяем тип API и вызываем соответствующую функцию
    # Порядок важен - более специфичные проверки первыми
    
    if 'openrouter' in model_type or 'openrouter' in api_url:
        return send_openrouter_request(model_name, prompt, api_key)
    elif 'openai' in model_type or 'openai' in api_url or 'azure-openai' in model_type:
        return send_openai_request(model_name, prompt, api_key)
    elif 'deepseek' in model_type or 'deepseek' in api_url:
        return send_deepseek_request(model_name, prompt, api_key)
    elif 'groq' in model_type or 'groq' in api_url:
        return send_groq_request(model_name, prompt, api_key)
    elif 'anthropic' in model_type or 'anthropic' in api_url:
        # Anthropic Claude использует свой формат, но может быть через прокси
        return send_generic_request(model, prompt, api_key)
    elif 'google' in model_type or 'google' in api_url or 'gemini' in api_url:
        # Google Gemini через OpenAI-совместимый API
        return send_generic_request(model, prompt, api_key)
    elif 'mistral' in model_type or 'mistral' in api_url:
        # Mistral через OpenAI-совместимый API
        return send_generic_request(model, prompt, api_key)
    elif 'cohere' in model_type or 'cohere' in api_url:
        # Cohere через OpenAI-совместимый API
        return send_generic_request(model, prompt, api_key)
    elif 'perplexity' in model_type or 'perplexity' in api_url:
        # Perplexity через OpenAI-совместимый API
        return send_generic_request(model, prompt, api_key)
    elif 'together' in model_type or 'together' in api_url:
        # Together AI через OpenAI-совместимый API
        return send_generic_request(model, prompt, api_key)
    elif 'replicate' in model_type or 'replicate' in api_url:
        # Replicate через OpenAI-совместимый API
        return send_generic_request(model, prompt, api_key)
    elif 'huggingface' in model_type or 'huggingface' in api_url or 'hf.co' in api_url:
        # Hugging Face Inference API через OpenAI-совместимый формат
        return send_generic_request(model, prompt, api_key)
    elif 'ollama' in model_type or 'ollama' in api_url:
        # Ollama локальные модели через OpenAI-совместимый API
        return send_generic_request(model, prompt, api_key)
    elif 'localai' in model_type or 'localai' in api_url or 'local' in model_type:
        # LocalAI через OpenAI-совместимый API
        return send_generic_request(model, prompt, api_key)
    else:
        # Попытка универсального запроса для совместимых API
        return send_generic_request(model, prompt, api_key)


def send_generic_request(model: Dict, prompt: str, api_key: str) -> str:
    """
    Универсальный запрос для API, совместимых с OpenAI форматом
    
    Args:
        model: Словарь с информацией о модели
        prompt: Текст промта
        api_key: API ключ
    
    Returns:
        Текст ответа модели
    """
    url = model['api_url']
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model.get('name', ''),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=get_request_timeout()
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        raise APIError(f"API request error: {str(e)}")
    except (KeyError, IndexError) as e:
        raise APIError(f"Invalid API response: {str(e)}")

