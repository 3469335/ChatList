# -*- coding: utf-8 -*-
"""
Скрипт для исправления настроек моделей в базе данных
Заменяет API ключи на имена переменных окружения
"""
import sqlite3

# Подключение к БД
conn = sqlite3.connect('chatlist.db')
cursor = conn.cursor()

# Получить все модели
cursor.execute('SELECT id, name, api_id FROM models')
models = cursor.fetchall()

print("Текущие модели:")
for model_id, name, api_id in models:
    print(f"ID: {model_id}, Name: {name}, API_ID: {api_id}")

print("\n" + "="*60)

# Определить правильные имена переменных для каждого ключа
# Если api_id начинается с "sk-", это скорее всего сам ключ, а не имя переменной
for model_id, name, api_id in models:
    if api_id.startswith('sk-'):
        # Это OpenRouter ключ
        new_api_id = 'OPENROUTER_API_KEY'
        print(f"\nМодель ID {model_id} ({name}):")
        print(f"  Старое значение: {api_id[:20]}...")
        print(f"  Новое значение: {new_api_id}")
        cursor.execute('UPDATE models SET api_id = ? WHERE id = ?', (new_api_id, model_id))
        print(f"  [OK] Обновлено!")
    elif api_id == 'env.local':
        # Это неправильное значение
        new_api_id = 'OPENROUTER_API_KEY'  # Или другое, в зависимости от модели
        print(f"\nМодель ID {model_id} ({name}):")
        print(f"  Старое значение: {api_id}")
        print(f"  Новое значение: {new_api_id}")
        cursor.execute('UPDATE models SET api_id = ? WHERE id = ?', (new_api_id, model_id))
        print(f"  [OK] Обновлено!")

conn.commit()

print("\n" + "="*60)
print("Обновленные модели:")
cursor.execute('SELECT id, name, api_id FROM models')
models = cursor.fetchall()
for model_id, name, api_id in models:
    print(f"ID: {model_id}, Name: {name}, API_ID: {api_id}")

conn.close()
print("\n[OK] Готово! Теперь убедитесь, что в файле .env есть переменная OPENROUTER_API_KEY с вашим ключом.")
