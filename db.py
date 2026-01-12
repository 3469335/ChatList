"""
Модуль для работы с базой данных SQLite
"""
import sqlite3
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Определяем путь к базе данных
# Если запущено как исполняемый файл, сохраняем в AppData пользователя
# Иначе - в директории приложения
if getattr(sys, 'frozen', False):
    # Если запущено как исполняемый файл (PyInstaller)
    # Используем AppData пользователя для Windows
    if sys.platform == 'win32':
        app_data_dir = os.path.join(os.getenv('APPDATA', ''), 'ChatList')
    else:
        # Для Linux/Mac используем домашнюю директорию
        app_data_dir = os.path.join(os.path.expanduser('~'), '.chatlist')
    
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
    DB_NAME = os.path.join(app_data_dir, "chatlist.db")
else:
    # Если запущено как скрипт
    DB_NAME = "chatlist.db"


def get_db_connection():
    """Создать и вернуть соединение с базой данных"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
    return conn


def init_database():
    """Инициализировать базу данных, создать все таблицы"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица промтов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            prompt TEXT NOT NULL,
            tags TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags)")
    
    # Таблица моделей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            api_url TEXT NOT NULL,
            api_id TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            model_type TEXT,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_name ON models(name)")
    
    # Таблица результатов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER,
            model_id INTEGER NOT NULL,
            response TEXT NOT NULL,
            selected INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE SET NULL,
            FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_created_at ON results(created_at)")
    
    # Таблица настроек
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    conn.commit()
    conn.close()


# ========== CRUD операции для prompts ==========

def create_prompt(prompt: str, tags: str = "") -> int:
    """Создать новый промт"""
    conn = get_db_connection()
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO prompts (date, prompt, tags) VALUES (?, ?, ?)",
        (date, prompt, tags)
    )
    prompt_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prompt_id


def get_all_prompts() -> List[Dict]:
    """Получить все промты"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prompts ORDER BY date DESC")
    prompts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return prompts


def get_prompt_by_id(prompt_id: int) -> Optional[Dict]:
    """Получить промт по ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def search_prompts(query: str) -> List[Dict]:
    """Поиск промтов по тексту или тегам"""
    conn = get_db_connection()
    cursor = conn.cursor()
    search_pattern = f"%{query}%"
    cursor.execute(
        "SELECT * FROM prompts WHERE prompt LIKE ? OR tags LIKE ? ORDER BY date DESC",
        (search_pattern, search_pattern)
    )
    prompts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return prompts


def delete_prompt(prompt_id: int) -> bool:
    """Удалить промт"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ========== CRUD операции для models ==========

def create_model(name: str, api_url: str, api_id: str, is_active: int = 1, model_type: str = "") -> int:
    """Создать новую модель"""
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO models (name, api_url, api_id, is_active, model_type, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, api_url, api_id, is_active, model_type, created_at)
    )
    model_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return model_id


def get_active_models() -> List[Dict]:
    """Получить все активные модели"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM models WHERE is_active = 1 ORDER BY name")
    models = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return models


def get_all_models() -> List[Dict]:
    """Получить все модели"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM models ORDER BY name")
    models = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return models


def update_model_status(model_id: int, is_active: int) -> bool:
    """Обновить статус активности модели"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE models SET is_active = ? WHERE id = ?", (is_active, model_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def update_model(model_id: int, name: str, api_url: str, api_id: str, is_active: int = 1, model_type: str = "") -> bool:
    """Обновить модель"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE models SET name = ?, api_url = ?, api_id = ?, is_active = ?, model_type = ? WHERE id = ?",
        (name, api_url, api_id, is_active, model_type, model_id)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def delete_model(model_id: int) -> bool:
    """Удалить модель"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ========== CRUD операции для results ==========

def save_results(results_list: List[Dict]) -> int:
    """Сохранить список результатов"""
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0
    
    for result in results_list:
        cursor.execute(
            "INSERT INTO results (prompt_id, model_id, response, selected, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                result.get('prompt_id'),
                result.get('model_id'),
                result.get('response'),
                result.get('selected', 0),
                created_at
            )
        )
        count += 1
    
    conn.commit()
    conn.close()
    return count


def get_all_results() -> List[Dict]:
    """Получить все результаты"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, m.name as model_name, p.prompt as prompt_text
        FROM results r
        LEFT JOIN models m ON r.model_id = m.id
        LEFT JOIN prompts p ON r.prompt_id = p.id
        ORDER BY r.created_at DESC
    """)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_results_by_prompt(prompt_id: int) -> List[Dict]:
    """Получить результаты по ID промта"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, m.name as model_name
        FROM results r
        JOIN models m ON r.model_id = m.id
        WHERE r.prompt_id = ? AND r.selected = 1
        ORDER BY r.created_at
    """, (prompt_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def search_results(query: str) -> List[Dict]:
    """Поиск результатов по тексту ответа"""
    conn = get_db_connection()
    cursor = conn.cursor()
    search_pattern = f"%{query}%"
    cursor.execute("""
        SELECT r.*, m.name as model_name, p.prompt as prompt_text
        FROM results r
        LEFT JOIN models m ON r.model_id = m.id
        LEFT JOIN prompts p ON r.prompt_id = p.id
        WHERE r.response LIKE ?
        ORDER BY r.created_at DESC
    """, (search_pattern,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def delete_result(result_id: int) -> bool:
    """Удалить результат"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ========== CRUD операции для settings ==========

def get_setting(key: str, default: str = "") -> str:
    """Получить настройку"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key: str, value: str):
    """Установить настройку"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

