# -*- coding: utf-8 -*-
"""
Исправление имен моделей в базе данных
"""
import sqlite3

conn = sqlite3.connect('chatlist.db')
cursor = conn.cursor()

print("Текущие модели:")
cursor.execute('SELECT id, name, model_type FROM models')
models = cursor.fetchall()
for m in models:
    print(f"  ID {m[0]}: {m[1]} ({m[2]})")

print("\nИсправление моделей...")

# Исправить модель ID 1 - "OI" неверное имя, заменим на рабочую модель
cursor.execute('UPDATE models SET name = ?, model_type = ? WHERE id = 1', 
               ('meta-llama/llama-3.1-8b-instruct:free', 'openrouter'))
print("  [OK] Модель ID 1: OI -> meta-llama/llama-3.1-8b-instruct:free")

# Исправить модель ID 2 - добавить :free
cursor.execute('UPDATE models SET name = ?, model_type = ? WHERE id = 2', 
               ('xiaomi/mimo-v2-flash:free', 'openrouter'))
print("  [OK] Модель ID 2: xiaomi/mimo-v2-flash -> xiaomi/mimo-v2-flash:free")

conn.commit()

print("\nОбновленные модели:")
cursor.execute('SELECT id, name, model_type FROM models')
models = cursor.fetchall()
for m in models:
    print(f"  ID {m[0]}: {m[1]} ({m[2]})")

conn.close()
print("\n[OK] Готово!")

