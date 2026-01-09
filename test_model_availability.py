# -*- coding: utf-8 -*-
"""
Проверка доступности моделей OpenRouter
"""
import requests
from config import get_api_key

api_key = get_api_key('OPENROUTER_API_KEY')

print("Проверка доступности моделей OpenRouter...\n")

# Получить список доступных моделей
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
        
        # Получить модели из базы данных
        import sqlite3
        conn = sqlite3.connect('chatlist.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM models WHERE model_type = ?', ('openrouter',))
        db_models = cursor.fetchall()
        conn.close()
        
        print(f"Всего моделей в OpenRouter: {len(models)}")
        print(f"Моделей в базе данных: {len(db_models)}\n")
        
        # Проверить каждую модель из БД
        available_models = [m.get('id', '') for m in models]
        
        for model_id, model_name in db_models:
            print(f"Проверка: {model_name}")
            if model_name in available_models:
                print(f"  [OK] Модель доступна")
            else:
                print(f"  [ERROR] Модель не найдена в списке доступных!")
                # Найти похожие модели
                similar = [m for m in available_models if model_name.split(':')[0] in m or model_name.split('/')[-1] in m]
                if similar:
                    print(f"  Похожие доступные модели:")
                    for sim in similar[:3]:
                        print(f"    - {sim}")
            print()
    else:
        print(f"Ошибка получения списка моделей: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Ошибка: {str(e)}")

