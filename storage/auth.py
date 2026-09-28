import sqlite3
import hashlib
import secrets
import os

class AuthManager:
    def __init__(self, db_path: str = "storage/empasis.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Создает таблицу пользователей с полями для лимитов, ролей, возраста и Google OAuth."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'student',
                    age INTEGER DEFAULT 14,
                    email TEXT DEFAULT '',
                    auth_provider TEXT DEFAULT 'local',
                    google_id TEXT DEFAULT '',
                    requests_used INTEGER DEFAULT 0,
                    max_requests INTEGER DEFAULT 15,
                    is_unlimited INTEGER DEFAULT 0,
                    is_verified INTEGER DEFAULT 1,
                    verification_code TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

            # Автоматическая миграция недостающих колонок
            cursor.execute("PRAGMA table_info(users)")
            existing_cols = [c[1] for c in cursor.fetchall()]
            
            migrations = [
                ("requests_used", "INTEGER DEFAULT 0"),
                ("max_requests", "INTEGER DEFAULT 15"),
                ("is_unlimited", "INTEGER DEFAULT 0"),
                ("age", "INTEGER DEFAULT 14"),
                ("email", "TEXT DEFAULT ''"),
                ("auth_provider", "TEXT DEFAULT 'local'"),
                ("google_id", "TEXT DEFAULT ''"),
                ("is_verified", "INTEGER DEFAULT 1"),
                ("verification_code", "TEXT DEFAULT ''")
            ]
            for col_name, col_def in migrations:
                if col_name not in existing_cols:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
            conn.commit()

            # Создаем мастер-аккаунты Администратора
            self._ensure_admin_exists(cursor, conn)

    def _ensure_admin_exists(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        """Создает защищенные аккаунты администратора (Владельца платформы)."""
        admins = [
            ("eciva", "Qazwsxedciva98971", 25, "eciva@school.uz"),
            ("admin", "admin2026", 30, "admin@school.uz")
        ]
        for uname, pwd, age, email in admins:
            cursor.execute("SELECT id FROM users WHERE username = ?", (uname,))
            if not cursor.fetchone():
                salt = secrets.token_hex(16)
                pwd_hash = self._hash_password(pwd, salt)
                cursor.execute("""
                    INSERT INTO users (username, password_hash, salt, role, age, email, requests_used, max_requests, is_unlimited, is_verified)
                    VALUES (?, ?, ?, 'admin', ?, ?, 0, 999999, 1, 1)
                """, (uname, pwd_hash, salt, age, email))
                conn.commit()

    def _hash_password(self, password: str, salt: str) -> str:
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return pwd_hash.hex()

    def register(self, username: str, password: str, role: str = "student", age: int = 14, email: str = "") -> tuple[bool, str, dict | None]:
        username = username.strip().lower()
        email = email.strip().lower()
        if len(username) < 3:
            return False, "Имя пользователя должно содержать минимум 3 символа", None
        if len(password) < 4:
            return False, "Пароль должен содержать минимум 4 символа", None

        valid_roles = ["student", "parent", "teacher", "psychologist", "admin"]
        if role not in valid_roles:
            role = "student"

        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, salt, role, age, email, requests_used, max_requests, is_unlimited, is_verified)
                    VALUES (?, ?, ?, ?, ?, ?, 0, 15, 0, 1)
                """, (username, password_hash, salt, role, age, email))
                conn.commit()
                user_id = cursor.lastrowid
                
                user_data = {
                    "id": user_id,
                    "username": username,
                    "role": role,
                    "age": age,
                    "email": email,
                    "requests_used": 0,
                    "max_requests": 15,
                    "is_unlimited": False
                }
                return True, "Регистрация успешна", user_data
        except sqlite3.IntegrityError:
            return False, "Пользователь с таким логином уже зарегистрирован", None

    def login(self, username: str, password: str) -> tuple[bool, str, dict | None]:
        username = username.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, password_hash, salt, role, age, email, requests_used, max_requests, is_unlimited 
                FROM users WHERE username = ?
            """, (username,))
            row = cursor.fetchone()

            if not row:
                return False, "Пользователь не найден", None

            stored_hash = row["password_hash"]
            salt = row["salt"]
            input_hash = self._hash_password(password, salt)

            if secrets.compare_digest(stored_hash, input_hash):
                user_data = {
                    "id": row["id"],
                    "username": username,
                    "role": row["role"],
                    "age": row["age"] or 14,
                    "email": row["email"] or "",
                    "requests_used": row["requests_used"],
                    "max_requests": row["max_requests"],
                    "is_unlimited": bool(row["is_unlimited"])
                }
                return True, "Успешный вход", user_data
            else:
                return False, "Неверный пароль", None

    def login_or_register_google(self, email: str, name: str, google_id: str, age: int = 14) -> tuple[bool, str, dict | None]:
        """Авторизация или мгновенная регистрация через аккаунт Google / Gmail."""
        email = email.strip().lower()
        if not email or "@" not in email:
            return False, "Некорректный адрес электронной почты Google", None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Поиск по google_id
            cursor.execute("SELECT id, username, role, age, email, requests_used, max_requests, is_unlimited FROM users WHERE google_id = ?", (google_id,))
            row = cursor.fetchone()

            # 2. Поиск по email, если google_id еще не привязан
            if not row:
                cursor.execute("SELECT id, username, role, age, email, requests_used, max_requests, is_unlimited FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()
                if row:
                    cursor.execute("UPDATE users SET google_id = ?, auth_provider = 'google' WHERE id = ?", (google_id, row["id"]))
                    conn.commit()

            if row:
                user_data = {
                    "id": row["id"],
                    "username": row["username"],
                    "role": row["role"],
                    "age": row["age"] or age,
                    "email": row["email"],
                    "requests_used": row["requests_used"],
                    "max_requests": row["max_requests"],
                    "is_unlimited": bool(row["is_unlimited"])
                }
                return True, "Успешный вход через Google", user_data

            # 3. Регистрация нового пользователя Google
            # Формируем читаемый username из email или имени
            base_username = (name.replace(" ", "_").lower() if name else email.split("@")[0])[:15]
            username = base_username
            idx = 1
            while True:
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if not cursor.fetchone():
                    break
                username = f"{base_username}_{idx}"
                idx += 1

            salt = secrets.token_hex(16)
            dummy_pwd = secrets.token_urlsafe(24)
            pwd_hash = self._hash_password(dummy_pwd, salt)

            cursor.execute("""
                INSERT INTO users (username, password_hash, salt, role, age, email, auth_provider, google_id, requests_used, max_requests, is_unlimited, is_verified)
                VALUES (?, ?, ?, 'student', ?, ?, 'google', ?, 0, 15, 0, 1)
            """, (username, pwd_hash, salt, age, email, google_id))
            conn.commit()
            new_id = cursor.lastrowid

            user_data = {
                "id": new_id,
                "username": username,
                "role": "student",
                "age": age,
                "email": email,
                "requests_used": 0,
                "max_requests": 15,
                "is_unlimited": False
            }
            return True, "Добро пожаловать в Empasis!", user_data

    def get_user_by_username(self, username: str) -> dict | None:
        username = username.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, role, age, email, requests_used, max_requests, is_unlimited 
                FROM users WHERE username = ?
            """, (username,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "username": row["username"],
                "role": row["role"],
                "age": row["age"] or 14,
                "email": row["email"] or "",
                "requests_used": row["requests_used"],
                "max_requests": row["max_requests"],
                "is_unlimited": bool(row["is_unlimited"])
            }

    def get_user_role(self, username: str) -> str | None:
        """Возвращает роль пользователя из базы данных."""
        username = username.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return row["role"] if row else None

    def check_and_use_request(self, username: str) -> tuple[bool, int, int]:
        """
        Проверяет и списывает 1 запрос у пользователя.
        Возвращает: (разрешено_ли, использовано, лимит)
        """
        username = username.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT requests_used, max_requests, is_unlimited FROM users WHERE username = ?
            """, (username,))
            row = cursor.fetchone()

            if not row:
                return False, 0, 0

            requests_used = row["requests_used"]
            max_requests = row["max_requests"]
            is_unlimited = row["is_unlimited"]

            # Для админа или безлимитных аккаунтов (школьная лицензия)
            if is_unlimited:
                cursor.execute("UPDATE users SET requests_used = requests_used + 1 WHERE username = ?", (username,))
                conn.commit()
                return True, requests_used + 1, max_requests

            # Если лимит исчерпан
            if requests_used >= max_requests:
                return False, requests_used, max_requests

            # Списываем 1 запрос
            cursor.execute("UPDATE users SET requests_used = requests_used + 1 WHERE username = ?", (username,))
            conn.commit()
            return True, requests_used + 1, max_requests

    def set_verification_code(self, username_or_email: str, code: str) -> bool:
        val = username_or_email.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET verification_code = ?, is_verified = 0 
                WHERE username = ? OR email = ?
            """, (code, val, val))
            conn.commit()
            return cursor.rowcount > 0

    def verify_code(self, username_or_email: str, code: str) -> tuple[bool, str]:
        val = username_or_email.strip().lower()
        code = code.strip()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, verification_code FROM users WHERE username = ? OR email = ?
            """, (val, val))
            row = cursor.fetchone()
            if not row:
                return False, "Пользователь не найден"
            if row["verification_code"] == code:
                cursor.execute("UPDATE users SET is_verified = 1, verification_code = '' WHERE id = ?", (row["id"],))
                conn.commit()
                return True, "Почта успешно подтверждена!"
            else:
                return False, "Неверный код подтверждения"

    # --- Управление пользователями в панели администратора ---
    def search_users(self, query: str = "") -> list[dict]:
        """Поиск пользователей по логину, роли или email."""
        query = f"%{query.strip().lower()}%"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, role, age, email, auth_provider, requests_used, max_requests, is_unlimited, is_verified, created_at
                FROM users 
                WHERE username LIKE ? OR role LIKE ? OR email LIKE ?
                ORDER BY id DESC LIMIT 50
            """, (query, query, query))
            return [
                {
                    "id": r["id"],
                    "username": r["username"],
                    "role": r["role"],
                    "age": r["age"] or 14,
                    "email": r["email"] or "—",
                    "auth_provider": r["auth_provider"],
                    "requests_used": r["requests_used"],
                    "max_requests": r["max_requests"],
                    "is_unlimited": bool(r["is_unlimited"]),
                    "is_verified": bool(r["is_verified"]),
                    "created_at": str(r["created_at"])[:16]
                }
                for r in cursor.fetchall()
            ]

    def update_user_privileges(self, user_id: int, role: str, max_requests: int, is_unlimited: bool) -> tuple[bool, str]:
        """Изменение роли и лимитов пользователя."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET role = ?, max_requests = ?, is_unlimited = ?
                WHERE id = ?
            """, (role, max_requests, 1 if is_unlimited else 0, user_id))
            conn.commit()
            if cursor.rowcount > 0:
                return True, "Привилегии успешно обновлены"
            return False, "Пользователь не найден"

    def delete_user(self, user_id: int) -> tuple[bool, str]:
        """Удаление пользователя (мастер-аккаунты eciva и admin защищены)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Пользователь не найден"

            username = row["username"].lower()
            if username in ["eciva", "admin"]:
                return False, "Запрещено удалять мастер-аккаунт администратора!"

            # Удаляем связанные чаты и сообщения
            cursor.execute("SELECT id FROM chats WHERE user_id = ?", (user_id,))
            chats = cursor.fetchall()
            for c in chats:
                cursor.execute("DELETE FROM chat_messages WHERE chat_id = ?", (c["id"],))
            cursor.execute("DELETE FROM chats WHERE user_id = ?", (user_id,))

            # Удаляем самого пользователя
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True, f"Пользователь {username} удален"

    def get_admin_dashboard(self) -> dict:
        """Статистика для директора и владельца платформы."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(requests_used) FROM users")
            total_requests = cursor.fetchone()[0] or 0

            return {
                "total_users": total_users,
                "total_requests": total_requests,
                "recent_users": self.search_users("")
            }
