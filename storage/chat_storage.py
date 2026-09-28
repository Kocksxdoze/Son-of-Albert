import sqlite3
import uuid
import os
from datetime import datetime

class ChatManager:
    def __init__(self, db_path: str = "storage/empasis.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Создает таблицы для хранения бесед и сообщений."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    text TEXT NOT NULL,
                    is_crisis INTEGER DEFAULT 0,
                    is_term INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chats_user ON chats(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat ON chat_messages(chat_id)")
            conn.commit()

    def create_chat(self, user_id: int, title: str = "Новый диалог") -> dict:
        """Создает новый диалог для пользователя."""
        chat_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chats (id, user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (chat_id, user_id, title, now, now))
            conn.commit()

        return {
            "id": chat_id,
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now
        }

    def get_user_chats(self, user_id: int) -> list[dict]:
        """Возвращает все диалоги пользователя, отсортированные по времени обновления."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, title, created_at, updated_at 
                FROM chats 
                WHERE user_id = ? 
                ORDER BY updated_at DESC
            """, (user_id,))
            return [
                {
                    "id": r["id"],
                    "user_id": r["user_id"],
                    "title": r["title"],
                    "created_at": str(r["created_at"])[:16],
                    "updated_at": str(r["updated_at"])[:16]
                }
                for r in cursor.fetchall()
            ]

    def get_chat_messages(self, chat_id: str) -> list[dict]:
        """Возвращает историю сообщений для конкретного диалога."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, sender, text, is_crisis, is_term, created_at 
                FROM chat_messages 
                WHERE chat_id = ? 
                ORDER BY id ASC
            """, (chat_id,))
            return [
                {
                    "id": r["id"],
                    "sender": r["sender"],
                    "text": r["text"],
                    "isCrisis": bool(r["is_crisis"]),
                    "isTerm": bool(r["is_term"]),
                    "created_at": str(r["created_at"])[:16]
                }
                for r in cursor.fetchall()
            ]

    def add_message(self, chat_id: str, sender: str, text: str, is_crisis: bool = False, is_term: bool = False) -> dict:
        """Добавляет реплику в диалог и обновляет время активности чата."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_messages (chat_id, sender, text, is_crisis, is_term, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (chat_id, sender, text, 1 if is_crisis else 0, 1 if is_term else 0, now))
            msg_id = cursor.lastrowid

            # Обновляем заголовок диалога, если это первая реплика пользователя
            if sender == "user":
                cursor.execute("SELECT title FROM chats WHERE id = ?", (chat_id,))
                chat_row = cursor.fetchone()
                if chat_row and chat_row["title"] in ["Новый диалог", "New chat", "Yangi suhbat"]:
                    # Формируем компактное имя темы из начала сообщения
                    new_title = text.strip()
                    if len(new_title) > 32:
                        new_title = new_title[:32].rstrip() + "..."
                    cursor.execute("UPDATE chats SET title = ?, updated_at = ? WHERE id = ?", (new_title, now, chat_id))
                else:
                    cursor.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
            else:
                cursor.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))

            conn.commit()

        return {
            "id": msg_id,
            "chat_id": chat_id,
            "sender": sender,
            "text": text,
            "isCrisis": is_crisis,
            "isTerm": is_term,
            "created_at": now
        }

    def delete_chat(self, chat_id: str, user_id: int) -> bool:
        """Удаляет диалог со всеми его сообщениями."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_messages WHERE chat_id = ?", (chat_id,))
            cursor.execute("DELETE FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def rename_chat(self, chat_id: str, user_id: int, new_title: str) -> bool:
        """Переименовывает диалог."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE chats SET title = ? WHERE id = ? AND user_id = ?", (new_title.strip(), chat_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
