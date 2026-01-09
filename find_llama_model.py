# -*- coding: utf-8 -*-
"""
Поиск правильного имени модели Llama в OpenRouter
"""
import requests
from config import get_api_key

api_key = get_api_key('OPENROUTER_API_KEY')

print("Поиск моделей Llama в OpenRouter...\n")

url = "https://openrouter.ai/api/v1/models"
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://github.com/chatlist-app",
    "X-Title": "ChatList"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        models = data.get('data', [])
        
        # Найти модели Llama
        llama_models = [m for m in models if 'llama' in m.get('id', '').lower()]
        free_llama = [m for m in llama_models if ':free' in m.get('id', '')]
        
        print(f"Найдено моделей Llama: {len(llama_models)}")
        print(f"Бесплатных моделей Llama: {len(free_llama)}\n")
        
        if free_llama:
            print("Бесплатные модели Llama:")
            for i, model in enumerate(free_llama[:5], 1):
                model_id = model.get('id', 'N/A')
                name = model.get('name', 'N/A')
                print(f"  {i}. {model_id}")
                print(f"     Название: {name}\n")
        else:
            print("Бесплатных моделей Llama не найдено")
            print("\nДоступные модели Llama (первые 5):")
            for i, model in enumerate(llama_models[:5], 1):
                model_id = model.get('id', 'N/A')
                name = model.get('name', 'N/A')
                print(f"  {i}. {model_id}")
                print(f"     Название: {name}\n")
    else:
        print(f"Ошибка: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Ошибка: {str(e)}")

