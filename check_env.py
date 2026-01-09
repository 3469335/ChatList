# -*- coding: utf-8 -*-
"""Проверка загрузки переменных окружения"""
from config import get_api_key
import os

print("=" * 60)
print("Проверка переменных окружения")
print("=" * 60)

# Проверить OPENROUTER_API_KEY
key = get_api_key('OPENROUTER_API_KEY')
if key:
    print(f"\n[OK] OPENROUTER_API_KEY найден")
    print(f"     Длина: {len(key)} символов")
    print(f"     Начинается с: {key[:15]}...")
    print(f"     Заканчивается на: ...{key[-10:]}")
else:
    print("\n[ERROR] OPENROUTER_API_KEY не найден!")
    print("     Убедитесь, что в файле .env есть строка:")
    print("     OPENROUTER_API_KEY=sk-or-v1-...")

# Проверить другие ключи
print("\n" + "=" * 60)
print("Другие переменные окружения:")
for var_name in ['OPENAI_API_KEY', 'DEEPSEEK_API_KEY', 'GROQ_API_KEY', 'HUGGINGFACE_API_KEY']:
    value = get_api_key(var_name)
    if value:
        print(f"  {var_name}: [OK] ({len(value)} символов)")
    else:
        print(f"  {var_name}: [не установлен]")

print("\n" + "=" * 60)

