# ChatList

Приложение для сравнения ответов различных нейросетей на один и тот же промт.

## Описание

ChatList — это Python-приложение с графическим интерфейсом на PyQt5, которое позволяет:
- Отправлять один промт в несколько нейросетей одновременно
- Сравнивать ответы разных моделей в удобной таблице
- Сохранять промты и результаты в базу данных SQLite
- Экспортировать результаты в Markdown или JSON
- Управлять списком моделей и их настройками

## Требования

- Python 3.11+
- PyQt5
- SQLite (встроен в Python)
- Библиотеки: requests, python-dotenv

## Установка

1. Клонируйте репозиторий или скачайте файлы проекта

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта и добавьте ваши API ключи:
```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# OpenRouter API Key
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Настройки приложения
REQUEST_TIMEOUT=30
MAX_RESULTS_PER_REQUEST=10
```

## Использование

### Запуск приложения

```bash
python main.py
```

### Добавление моделей

1. В правой панели нажмите "Добавить модель"
2. Заполните форму:
   - **Название**: Имя модели (например, "GPT-4")
   - **API URL**: URL эндпоинта API
   - **API Key (env var)**: Имя переменной окружения с ключом (например, "OPENAI_API_KEY")
   - **Тип модели**: openai, deepseek, groq, openrouter или other
   - **Активна**: Отметьте, если модель должна использоваться по умолчанию

### Примеры моделей для OpenRouter

OpenRouter поддерживает множество моделей. Примеры конфигурации:

- **GPT-4**: 
  - Название: `openai/gpt-4`
  - API URL: `https://openrouter.ai/api/v1/chat/completions`
  - API Key: `OPENROUTER_API_KEY`
  - Тип: `openrouter`

- **Claude 3.5 Sonnet**:
  - Название: `anthropic/claude-3.5-sonnet`
  - API URL: `https://openrouter.ai/api/v1/chat/completions`
  - API Key: `OPENROUTER_API_KEY`
  - Тип: `openrouter`

- **Llama 3.1 70B**:
  - Название: `meta-llama/llama-3.1-70b-instruct`
  - API URL: `https://openrouter.ai/api/v1/chat/completions`
  - API Key: `OPENROUTER_API_KEY`
  - Тип: `openrouter`

### Работа с промтами

1. Введите промт в центральной области
2. Опционально добавьте теги через запятую
3. Нажмите "Отправить" для отправки во все активные модели
4. Результаты появятся в таблице ниже
5. Отметьте нужные результаты чекбоксами
6. Нажмите "Сохранить выбранные результаты" для сохранения в БД

### Экспорт результатов

Используйте меню "Файл" → "Экспорт в Markdown" или "Экспорт в JSON" для сохранения результатов в файл.

## Структура проекта

```
ChatList/
├── main.py          # Главный модуль с GUI
├── db.py            # Работа с базой данных SQLite
├── models.py        # Логика работы с моделями
├── network.py       # HTTP-запросы к API
├── config.py        # Загрузка конфигурации из .env
├── logger.py        # Логирование
├── requirements.txt # Зависимости
├── build.bat        # Скрипт сборки исполняемого файла
└── chatlist.db      # База данных SQLite (создается автоматически)
```

## База данных

Приложение использует SQLite базу данных `chatlist.db`, которая создается автоматически при первом запуске.

### Таблицы:
- **prompts** - сохраненные промты
- **models** - настройки моделей нейросетей
- **results** - сохраненные результаты ответов
- **settings** - настройки приложения

## Сборка исполняемого файла

Для создания исполняемого файла Windows:

```bash
build.bat
```

Исполняемый файл будет создан в папке `dist\PyQtApp.exe`

## Логирование

Логи сохраняются в папке `logs/` с именем файла `chatlist_YYYYMMDD.log`

## Поддерживаемые API

- OpenAI
- DeepSeek
- Groq
- OpenRouter (поддерживает множество моделей)
- Любые API, совместимые с форматом OpenAI

## Лицензия

См. файл LICENSE

## Автор

ChatList - приложение для сравнения ответов нейросетей
