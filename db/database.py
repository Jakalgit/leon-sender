import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "chats.db")


def get_connection():
    """Создает и возвращает соединение с базой данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """Создает таблицу транзакций, если она не существует."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL UNIQUE
        )
    """)

    conn.commit()
    conn.close()


def row_to_dict(row):
    """Преобразует sqlite3.Row в обычный словарь."""
    return dict(row) if row else None


def add_chat(chat_id: str):
    """Добавляет чат в базу данных."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO chats (chat_id) 
            VALUES (?)
        """, (chat_id,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Ошибка добавления чата: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_chats():
    """Получает список чатов, в которых есть бот."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM chats")
    rows = cursor.fetchall()
    conn.close()

    return [row_to_dict(row) for row in rows]


def chat_exists(chat_id: str) -> bool:
    """Проверяет, есть ли чат с таким chat_id в базе."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM chats WHERE chat_id = ? LIMIT 1", (chat_id,))
    exists = cursor.fetchone() is not None

    conn.close()
    return exists


def remove_chat(chat_id: str):
    """Удаляет чат из базы данных."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()


create_tables()