# -*- coding: utf-8 -*-
"""
Проверка доступа к бесплатным моделям OpenRouter
"""
import requests
from config import get_api_key, get_request_timeout

api_key = get_api_key('OPENROUTER_API_KEY')

print("=" * 60)
print("Проверка бесплатных моделей OpenRouter")
print("=" * 60)

# Список бесплатных моделей (из предыдущего вывода)
free_models = [
    "xiaomi/mimo-v2-flash:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-flash-1.5-8b:free"
]

print(f"\nТестирование {len(free_models)} бесплатных моделей...\n")

success_count = 0
for model_name in free_models:
    print(f"Модель: {model_name}")
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
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"  [OK] Ответ: {content}")
            success_count += 1
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error_msg = error_data.get('error', {}).get('message', response.text[:100])
            print(f"  [ERROR] {response.status_code}: {error_msg}")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    print()

print("=" * 60)
print(f"Результат: {success_count}/{len(free_models)} моделей работают")
print("=" * 60)

if success_count > 0:
    print("\n[OK] Доступ к бесплатным моделям работает!")
    print("     Используйте модели с суффиксом :free в названии.")
else:
    print("\n[WARNING] Нет доступа даже к бесплатным моделям.")
    print("          Возможные причины:")
    print("          1. Необходима регистрация аккаунта на openrouter.ai")
    print("          2. Необходимо пополнить баланс (даже для бесплатных моделей)")
    print("          3. API ключ неверный или истек")

