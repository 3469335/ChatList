# -*- coding: utf-8 -*-
"""
Проверка нового API ключа OpenRouter
"""
import requests
from config import get_api_key, get_request_timeout

print("=" * 60)
print("Проверка нового API ключа OpenRouter")
print("=" * 60)

api_key = get_api_key('OPENROUTER_API_KEY')
if not api_key:
    print("\n[ERROR] API ключ не найден!")
    exit(1)

print(f"\n[OK] API ключ загружен")
print(f"     Длина: {len(api_key)} символов")
print(f"     Начинается с: {api_key[:20]}...")
print(f"     Заканчивается на: ...{api_key[-20:]}")

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
        print(f"[OK] Информация об аккаунте:")
        print(f"     Данные: {data}")
    else:
        error_text = response.text
        print(f"[ERROR] Ошибка: {error_text}")
except Exception as e:
    print(f"[ERROR] Исключение: {str(e)}")

# Тест 2: Простой запрос к бесплатной модели
print("\n" + "=" * 60)
print("Тест 2: Запрос к бесплатной модели")
print("=" * 60)

test_models = [
    "xiaomi/mimo-v2-flash:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-flash-1.5-8b:free"
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
            "messages": [{"role": "user", "content": "Say hello in one word."}]
        }
        response = requests.post(url, headers=headers, json=data, timeout=get_request_timeout())
        print(f"  Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"  [OK] Ответ: {content}")
            print(f"\n[SUCCESS] Ключ работает! Модель {model_name} отвечает.")
            break
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"  [ERROR] {error_msg}")
            except:
                print(f"  [ERROR] {response.text[:200]}")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")

print("\n" + "=" * 60)
print("Проверка завершена")
print("=" * 60)

