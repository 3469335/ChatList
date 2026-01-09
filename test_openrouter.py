# -*- coding: utf-8 -*-
"""
Скрипт для проверки доступа к моделям OpenRouter
"""
import sys
from config import get_api_key
from network import send_openrouter_request, APIError
import sqlite3

print("=" * 60)
print("Проверка доступа к OpenRouter API")
print("=" * 60)

# Проверить наличие ключа
api_key = get_api_key('OPENROUTER_API_KEY')
if not api_key:
    print("\n[ERROR] OPENROUTER_API_KEY не найден в .env файле!")
    print("        Убедитесь, что файл .env содержит:")
    print("        OPENROUTER_API_KEY=sk-or-v1-...")
    sys.exit(1)

print(f"\n[OK] API ключ найден: {api_key[:15]}...{api_key[-10:]}")
print(f"     Длина ключа: {len(api_key)} символов")

# Получить модели из базы данных
print("\n" + "=" * 60)
print("Модели в базе данных:")
print("=" * 60)

conn = sqlite3.connect('chatlist.db')
cursor = conn.cursor()
cursor.execute('SELECT id, name, api_id, model_type, is_active FROM models WHERE model_type = ? OR api_id = ?', 
               ('openrouter', 'OPENROUTER_API_KEY'))
models = cursor.fetchall()
conn.close()

if not models:
    print("\n[WARNING] Не найдено моделей OpenRouter в базе данных!")
    print("          Добавьте модели через интерфейс приложения.")
    sys.exit(1)

print(f"\nНайдено моделей: {len(models)}")
for model_id, name, api_id, model_type, is_active in models:
    status = "активна" if is_active else "неактивна"
    print(f"  ID {model_id}: {name} ({model_type}) - {status}")

# Тестировать доступ к моделям
print("\n" + "=" * 60)
print("Тестирование доступа к моделям")
print("=" * 60)

test_prompt = "Привет! Ответь одним предложением: работает ли у тебя доступ к OpenRouter?"

for model_id, name, api_id, model_type, is_active in models:
    if not is_active:
        print(f"\n[SKIP] Модель '{name}' пропущена (неактивна)")
        continue
    
    print(f"\nТестирование модели: {name}")
    print(f"  ID модели в OpenRouter: {name}")
    
    try:
        response = send_openrouter_request(name, test_prompt, api_key)
        print(f"  [OK] Запрос успешен!")
        print(f"  Ответ: {response[:100]}...")
        if len(response) > 100:
            print(f"  (полный ответ: {len(response)} символов)")
    except APIError as e:
        print(f"  [ERROR] Ошибка API: {str(e)}")
    except Exception as e:
        print(f"  [ERROR] Неожиданная ошибка: {str(e)}")

print("\n" + "=" * 60)
print("Проверка завершена")
print("=" * 60)

