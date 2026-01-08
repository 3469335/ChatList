# Схема базы данных ChatList

## Общая информация

База данных: SQLite  
Файл БД: `chatlist.db` (создается автоматически при первом запуске)

## Таблицы

### 1. Таблица `prompts` (Промты)

Хранит сохраненные пользователем промты (запросы).

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор промта |
| date | TEXT | NOT NULL | Дата создания промта (ISO формат: YYYY-MM-DD HH:MM:SS) |
| prompt | TEXT | NOT NULL | Текст промта |
| tags | TEXT | NULL | Теги через запятую (например: "python, api, test") |

**Индексы:**
- `idx_prompts_date` на поле `date`
- `idx_prompts_tags` на поле `tags`

**Пример данных:**
```sql
INSERT INTO prompts (date, prompt, tags) 
VALUES ('2024-01-15 10:30:00', 'Объясни разницу между списком и кортежем в Python', 'python, basics');
```

---

### 2. Таблица `models` (Модели нейросетей)

Хранит информацию о доступных моделях нейросетей и их API-конфигурации.

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор модели |
| name | TEXT | NOT NULL UNIQUE | Название модели (например: "GPT-4", "DeepSeek Chat") |
| api_url | TEXT | NOT NULL | URL API эндпоинта |
| api_id | TEXT | NOT NULL | Имя переменной окружения с API-ключом (например: "OPENAI_API_KEY") |
| is_active | INTEGER | NOT NULL DEFAULT 1 | Флаг активности (1 - активна, 0 - неактивна) |
| model_type | TEXT | NULL | Тип модели для определения способа запроса ("openai", "deepseek", "groq", etc.) |
| created_at | TEXT | NOT NULL | Дата создания записи |

**Индексы:**
- `idx_models_is_active` на поле `is_active`
- `idx_models_name` на поле `name`

**Пример данных:**
```sql
INSERT INTO models (name, api_url, api_id, is_active, model_type, created_at) 
VALUES 
  ('GPT-4', 'https://api.openai.com/v1/chat/completions', 'OPENAI_API_KEY', 1, 'openai', '2024-01-15 10:00:00'),
  ('DeepSeek Chat', 'https://api.deepseek.com/v1/chat/completions', 'DEEPSEEK_API_KEY', 1, 'deepseek', '2024-01-15 10:00:00'),
  ('Llama 3 (Groq)', 'https://api.groq.com/openai/v1/chat/completions', 'GROQ_API_KEY', 1, 'groq', '2024-01-15 10:00:00');
```

**Примечание:** API-ключи хранятся в файле `.env`, а не в базе данных. В таблице хранится только имя переменной окружения.

---

### 3. Таблица `results` (Результаты)

Хранит сохраненные пользователем результаты ответов моделей.

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор результата |
| prompt_id | INTEGER | NULL | Ссылка на промт из таблицы prompts (может быть NULL для несохраненных промтов) |
| model_id | INTEGER | NOT NULL | Ссылка на модель из таблицы models |
| response | TEXT | NOT NULL | Текст ответа модели |
| selected | INTEGER | NOT NULL DEFAULT 0 | Флаг выбора пользователем (1 - выбран, 0 - не выбран) |
| created_at | TEXT | NOT NULL | Дата и время создания записи |

**Индексы:**
- `idx_results_prompt_id` на поле `prompt_id`
- `idx_results_model_id` на поле `model_id`
- `idx_results_created_at` на поле `created_at`

**Внешние ключи:**
- `FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE SET NULL`
- `FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE`

**Пример данных:**
```sql
INSERT INTO results (prompt_id, model_id, response, selected, created_at) 
VALUES 
  (1, 1, 'Список - это изменяемая коллекция...', 1, '2024-01-15 10:35:00'),
  (1, 2, 'Основное отличие списка от кортежа...', 0, '2024-01-15 10:35:01');
```

---

### 4. Таблица `settings` (Настройки)

Хранит настройки приложения в формате ключ-значение.

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| key | TEXT | PRIMARY KEY | Ключ настройки |
| value | TEXT | NULL | Значение настройки |

**Пример данных:**
```sql
INSERT INTO settings (key, value) 
VALUES 
  ('request_timeout', '30'),
  ('max_results_per_request', '10'),
  ('auto_save_prompts', '1'),
  ('export_format', 'markdown');
```

---

## SQL скрипт создания базы данных

```sql
-- Таблица промтов
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    prompt TEXT NOT NULL,
    tags TEXT
);

CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date);
CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags);

-- Таблица моделей
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    api_url TEXT NOT NULL,
    api_id TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    model_type TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active);
CREATE INDEX IF NOT EXISTS idx_models_name ON models(name);

-- Таблица результатов
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER,
    model_id INTEGER NOT NULL,
    response TEXT NOT NULL,
    selected INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE SET NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id);
CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id);
CREATE INDEX IF NOT EXISTS idx_results_created_at ON results(created_at);

-- Таблица настроек
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

---

## Связи между таблицами

```
prompts (1) ──< (0..N) results
models (1) ──< (1..N) results
```

- Один промт может иметь множество результатов (ответы от разных моделей)
- Одна модель может иметь множество результатов (ответы на разные промты)
- Результат всегда связан с моделью, но может быть не связан с сохраненным промтом

---

## Запросы для работы с данными

### Получить все активные модели
```sql
SELECT * FROM models WHERE is_active = 1 ORDER BY name;
```

### Получить все промты с результатами
```sql
SELECT p.*, COUNT(r.id) as results_count 
FROM prompts p 
LEFT JOIN results r ON p.id = r.prompt_id 
GROUP BY p.id 
ORDER BY p.date DESC;
```

### Получить сохраненные результаты для промта
```sql
SELECT r.*, m.name as model_name 
FROM results r 
JOIN models m ON r.model_id = m.id 
WHERE r.prompt_id = ? AND r.selected = 1 
ORDER BY r.created_at;
```

### Поиск промтов по тегам
```sql
SELECT * FROM prompts 
WHERE tags LIKE '%?%' 
ORDER BY date DESC;
```

### Получить настройку
```sql
SELECT value FROM settings WHERE key = ?;
```

### Установить настройку
```sql
INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);
```

