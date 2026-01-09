# -*- coding: utf-8 -*-
"""
Детальная проверка доступа к OpenRouter API
"""
import requests
from config import get_api_key, get_request_timeout

print("=" * 60)
print("Детальная проверка OpenRouter API")
print("=" * 60)

api_key = get_api_key('OPENROUTER_API_KEY')
if not api_key:
    print("\n[ERROR] API ключ не найден!")
    exit(1)

print(f"\n[OK] API ключ: {api_key[:20]}...{api_key[-10:]}")

# Тест 1: Проверка информации об аккаунте
print("\n" + "=" * 60)
print("Тест 1: Проверка информации об аккаунте")
print("=" * 60)

try:
    url = "https://openrouter.ai/api/v1/auth/key"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/chatlist-app",
        "X-Title": "ChatList"
    }
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Информация об аккаунте получена:")
        print(f"     Данные: {data}")
    else:
        print(f"[ERROR] Ошибка: {response.text}")
except Exception as e:
    print(f"[ERROR] Исключение: {str(e)}")

# Тест 2: Проверка доступных моделей
print("\n" + "=" * 60)
print("Тест 2: Список доступных моделей")
print("=" * 60)

try:
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/chatlist-app",
        "X-Title": "ChatList"
    }
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        models = data.get('data', [])
        print(f"[OK] Найдено моделей: {len(models)}")
        print("\nПервые 10 моделей:")
        for i, model in enumerate(models[:10], 1):
            model_id = model.get('id', 'N/A')
            name = model.get('name', 'N/A')
            print(f"  {i}. {model_id} - {name}")
    else:
        print(f"[ERROR] Ошибка: {response.text}")
except Exception as e:
    print(f"[ERROR] Исключение: {str(e)}")

# Тест 3: Простой запрос к модели
print("\n" + "=" * 60)
print("Тест 3: Простой запрос к модели")
print("=" * 60)

# Попробуем популярную модель
test_models = [
    "openai/gpt-3.5-turbo",
    "meta-llama/llama-3.1-8b-instruct",
    "google/gemini-pro"
]

for model_name in test_models:
    print(f"\nТестирование: {model_name}")
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/chatlist-app",
            "X-Title": "ChatList"
        }
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Hi! Say hello in one word."}]
        }
        response = requests.post(url, headers=headers, json=data, timeout=get_request_timeout())
        print(f"  Статус: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"  [OK] Ответ: {content}")
            break
        else:
            print(f"  [ERROR] {response.text[:200]}")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")

print("\n" + "=" * 60)
print("Проверка завершена")
print("=" * 60)

