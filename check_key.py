# -*- coding: utf-8 -*-
from config import get_api_key

key = get_api_key('OPENROUTER_API_KEY')
print("Проверка API ключа OpenRouter:")
print(f"Длина: {len(key)} символов")
print(f"Начинается с: {key[:20]}")
print(f"Заканчивается на: {key[-20:]}")
print(f"\nПолный ключ: {key}")

