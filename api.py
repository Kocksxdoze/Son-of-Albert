import sys
import os
import json
import secrets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.safety import SafetyGuard
from storage.knowledge import PsychoKnowledge
from storage.auth import AuthManager
from storage.chat_storage import ChatManager
from core.brain import EmpasisBrain
from core.mailer import Mailer

app = FastAPI(
    title="Empasis AI Backend",
    description="API ассистента школьной психологической службы Узбекистана с B2B-лимитами и мульти-чатами",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

safety = SafetyGuard()
knowledge = PsychoKnowledge()
auth = AuthManager()
chat_mgr = ChatManager()
brain = EmpasisBrain()
mailer = Mailer()

# --- Схемы данных ---
class ChatRequest(BaseModel):
    message: str
    username: str = "guest"
    chat_id: str | None = None
    lang: str = "ru"

class ChatResponse(BaseModel):
    reply: str
    is_crisis: bool
    is_term: bool
    is_limit_reached: bool = False
    requests_used: int = 0
    max_requests: int = 15
    chat_id: str | None = None

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "student"
    age: int = 14
    email: str = ""

class LoginRequest(BaseModel):
    username: str
    password: str

class GoogleAuthRequest(BaseModel):
    email: str
    name: str = ""
    google_id: str = ""
    age: int = 14

class SendCodeRequest(BaseModel):
    email: str
    username: str = ""

class VerifyCodeRequest(BaseModel):
    username_or_email: str
    code: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: dict | None = None

class CreateChatRequest(BaseModel):
    username: str
    title: str = "Новый диалог"

class UpdatePrivilegesRequest(BaseModel):
    role: str
    max_requests: int
    is_unlimited: bool

# --- Аутентификация ---
@app.post("/api/auth/register", response_model=AuthResponse)
def register_endpoint(req: RegisterRequest):
    success, message, user_data = auth.register(
        username=req.username,
        password=req.password,
        role=req.role,
        age=req.age,
        email=req.email
    )
    if not success:
        return AuthResponse(success=False, message=message, user=None)
    return AuthResponse(success=True, message=message, user=user_data)

@app.post("/api/auth/login", response_model=AuthResponse)
def login_endpoint(req: LoginRequest):
    success, message, user_data = auth.login(req.username, req.password)
    if not success:
        return AuthResponse(success=False, message=message, user=None)
    return AuthResponse(success=True, message=message, user=user_data)

@app.post("/api/auth/google", response_model=AuthResponse)
def google_auth_endpoint(req: GoogleAuthRequest):
    """Мгновенный вход или регистрация через Google / Gmail."""
    google_id = req.google_id or f"g_{hash(req.email) % 10000000}"
    success, message, user_data = auth.login_or_register_google(
        email=req.email,
        name=req.name,
        google_id=google_id,
        age=req.age
    )
    return AuthResponse(success=success, message=message, user=user_data)

@app.post("/api/auth/send-code")
def send_code_endpoint(req: SendCodeRequest):
    """Генерация и отправка проверочного кода на почту."""
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Укажите корректный адрес email")

    code = str(secrets.randbelow(900000) + 100000)
    auth.set_verification_code(email, code)
    success, msg = mailer.send_verification_code(email, req.username or email.split("@")[0], code)
    return {"success": success, "message": msg, "dev_code": code}

@app.post("/api/auth/verify-code")
def verify_code_endpoint(req: VerifyCodeRequest):
    """Подтверждение кода из почты."""
    success, msg = auth.verify_code(req.username_or_email, req.code)
    if not success:
        return {"success": False, "message": msg}
    return {"success": True, "message": msg}

# --- Мульти-диалоги (Чаты) ---
@app.get("/api/chats")
def get_chats_endpoint(username: str):
    """Возвращает все диалоги пользователя. Если чатов нет — создает первый."""
    user = auth.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    chats = chat_mgr.get_user_chats(user["id"])
    if not chats:
        # Создаем приветственный диалог
        initial_chat = chat_mgr.create_chat(user["id"], "Новый диалог")
        chats = [initial_chat]

    return {"chats": chats}

@app.post("/api/chats")
def create_chat_endpoint(req: CreateChatRequest):
    """Создает новый диалог."""
    user = auth.get_user_by_username(req.username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    new_chat = chat_mgr.create_chat(user["id"], req.title)
    return {"success": True, "chat": new_chat}

@app.get("/api/chats/{chat_id}/messages")
def get_chat_messages_endpoint(chat_id: str):
    """Возвращает историю сообщений выбранного диалога."""
    messages = chat_mgr.get_chat_messages(chat_id)
    return {"chat_id": chat_id, "messages": messages}

@app.delete("/api/chats/{chat_id}")
def delete_chat_endpoint(chat_id: str, username: str):
    """Удаляет выбранный диалог со всеми репликами."""
    user = auth.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    success = chat_mgr.delete_chat(chat_id, user["id"])
    return {"success": success}

# --- Чат с контролем лимитов, памятью и персонализацией ---
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    text = req.message.strip()
    if not text:
        return ChatResponse(reply="Сообщение пустое", is_crisis=False, is_term=False)

    user = auth.get_user_by_username(req.username)
    if not user:
        # Демо-пользователь
        user = {"id": 0, "username": req.username, "role": "student", "age": 14, "requests_used": 0, "max_requests": 15, "is_unlimited": False}

    # Обеспечиваем наличие chat_id
    active_chat_id = req.chat_id
    if not active_chat_id:
        user_chats = chat_mgr.get_user_chats(user["id"]) if user["id"] else []
        if user_chats:
            active_chat_id = user_chats[0]["id"]
        elif user["id"]:
            new_c = chat_mgr.create_chat(user["id"], "Новый диалог")
            active_chat_id = new_c["id"]
        else:
            active_chat_id = "guest_chat"

    # 1. Проверка на кризис РУз (всегда доступна даже при исчерпанном лимите!)
    is_crisis, crisis_msg = safety.check_crisis(text, lang=req.lang)
    if is_crisis:
        if user["id"] and active_chat_id != "guest_chat":
            chat_mgr.add_message(active_chat_id, "user", text, is_crisis=True)
            chat_mgr.add_message(active_chat_id, "bot", crisis_msg, is_crisis=True)
        return ChatResponse(reply=crisis_msg, is_crisis=True, is_term=False, chat_id=active_chat_id)

    # 2. Проверка лимита запросов (B2B лицензирование для школ)
    allowed, used, max_req = auth.check_and_use_request(req.username)
    if not allowed:
        limit_msg = {
            "ru": (
                "⚠️ **Лимит бесплатных запросов исчерпан (15 из 15).**\n\n"
                "Ваша школа еще не активировала безлимитную лицензию **Empasis School Care**.\n"
                "Пожалуйста, обратитесь к администрации школы или школьному психологу для продления доступа всего класса."
            ),
            "uz": (
                "⚠️ **Bepul so'rovlar limiti tugadi (15 tadan 15 ta).**\n\n"
                "Maktabingiz hali **Empasis School Care** cheksiz litsenziyasini faollashtirmagan.\n"
                "Iltimos, barcha o'quvchilar uchun to'liq kirishni ochish maqsadida maktab ma'muriyatiga murojaat qiling."
            ),
            "en": (
                "⚠️ **Free request limit reached (15/15).**\n\n"
                "Your school has not yet activated the **Empasis School Care** unlimited license.\n"
                "Please contact your school administration or psychologist to extend access for your school."
            )
        }.get(req.lang, "Лимит запросов исчерпан.")

        return ChatResponse(
            reply=limit_msg,
            is_crisis=False,
            is_term=False,
            is_limit_reached=True,
            requests_used=used,
            max_requests=max_req,
            chat_id=active_chat_id
        )

    # 3. Сохраняем реплику пользователя в историю диалога
    if user["id"] and active_chat_id != "guest_chat":
        chat_mgr.add_message(active_chat_id, "user", text)

    # 4. Получаем историю предыдущих сообщений для передачи в контекст нейросети
    history = chat_mgr.get_chat_messages(active_chat_id) if (user["id"] and active_chat_id != "guest_chat") else []

    # 5. Поиск в базе знаний SQLite
    kb_info = knowledge.find_term(text)

    # 6. Генерация эмпатичного ответа с учетом возраста и роли ученика
    reply = brain.generate_response(
        user_text=text,
        lang=req.lang,
        kb_info=kb_info,
        user_profile=user,
        chat_history=history
    )

    # 7. Сохраняем ответ ассистента в историю диалога
    if user["id"] and active_chat_id != "guest_chat":
        chat_mgr.add_message(active_chat_id, "bot", reply, is_term=bool(kb_info))

    return ChatResponse(
        reply=reply,
        is_crisis=False,
        is_term=bool(kb_info),
        is_limit_reached=False,
        requests_used=used,
        max_requests=max_req,
        chat_id=active_chat_id
    )

@app.post("/api/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    """Потоковый эндпоинт (Server-Sent Events) с мгновенным выводом ответа."""
    text = req.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Текст сообщения не может быть пустым")

    # 1. Детерминированный кризисный щит
    is_crisis, crisis_reply = safety.check_crisis(text, req.lang)

    # 2. Проверка пользователя и B2B-лимитов
    user = auth.get_user_by_username(req.username)
    if not user:
        user = {"id": 0, "username": req.username, "role": "student", "age": 14, "requests_used": 0, "max_requests": 15, "is_unlimited": False}

    allowed, used, max_req = auth.check_and_use_request(req.username)

    # 3. Активный чат
    active_chat_id = req.chat_id
    if user["id"] and (not active_chat_id or active_chat_id == "guest_chat"):
        chat_title = (text[:35] + "...") if len(text) > 35 else text
        active_chat = chat_mgr.create_chat(user["id"], chat_title)
        active_chat_id = active_chat["id"] if active_chat else "guest_chat"
    elif not active_chat_id:
        active_chat_id = "guest_chat"

    # Сохраняем входящее сообщение пользователя
    if user["id"] and active_chat_id != "guest_chat":
        chat_mgr.add_message(active_chat_id, "user", text)

    history = chat_mgr.get_chat_messages(active_chat_id) if (user["id"] and active_chat_id != "guest_chat") else []
    kb_info = knowledge.find_term(text)

    def event_generator():
        # Мета-данные чата первым пакетом
        meta = {
            "type": "meta",
            "chat_id": active_chat_id,
            "requests_used": used,
            "max_requests": max_req,
            "is_crisis": is_crisis,
            "is_term": bool(kb_info)
        }
        yield f"data: {json.dumps(meta, ensure_ascii=False)}\n\n"

        # Если сработал кризисный щит
        if is_crisis:
            yield f"data: {json.dumps({'type': 'token', 'token': crisis_reply, 'is_crisis': True}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'token': ''}, ensure_ascii=False)}\n\n"
            if user["id"] and active_chat_id != "guest_chat":
                chat_mgr.add_message(active_chat_id, "bot", crisis_reply, is_crisis=True)
            return

        # Если исчерпан лимит бесплатных запросов
        if not allowed:
            limit_msg = {
                "ru": "⚠️ **Бесплатный лимит запросов (15/15) исчерпан.**\n\nОбратитесь к администрации школы для активации безлимитной лицензии Empasis School Care.",
                "uz": "⚠️ **Bepul so'rovlar limiti (15/15) tugadi.**\n\nEmpasis School Care litsenziyasini faollashtirish uchun maktab ma'muriyatiga murojaat qiling.",
                "en": "⚠️ **Free request limit reached (15/15).**\n\nPlease contact your school administration to extend access."
            }.get(req.lang, "Лимит запросов исчерпан.")
            yield f"data: {json.dumps({'type': 'token', 'token': limit_msg, 'is_limit': True}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'token': ''}, ensure_ascii=False)}\n\n"
            return

        # Потоковая генерация через brain.generate_stream
        accumulated_text = ""
        for chunk in brain.generate_stream(
            user_text=text,
            lang=req.lang,
            kb_info=kb_info,
            user_profile=user,
            chat_history=history
        ):
            token = chunk.get("token", "")
            done = chunk.get("done", False)
            is_term = chunk.get("is_term", False)
            if token:
                accumulated_text += token
                yield f"data: {json.dumps({'type': 'token', 'token': token, 'is_term': is_term}, ensure_ascii=False)}\n\n"
            if done:
                yield f"data: {json.dumps({'type': 'done', 'token': ''}, ensure_ascii=False)}\n\n"
                break

        # Сохранение полного ответа в базу
        if user["id"] and active_chat_id != "guest_chat" and accumulated_text:
            chat_mgr.add_message(active_chat_id, "bot", accumulated_text, is_term=bool(kb_info))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# --- Панель Администратора ---
@app.get("/api/admin/dashboard")
def admin_dashboard(username: str):
    """Сводная аналитика для владельца платформы."""
    role = auth.get_user_role(username)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен. Только для администратора школы.")
    return auth.get_admin_dashboard()

@app.get("/api/admin/users")
def admin_search_users(username: str, query: str = ""):
    """Живой поиск пользователей по имени, почте или роли."""
    role = auth.get_user_role(username)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен. Только для администратора школы.")
    return {"users": auth.search_users(query)}

@app.patch("/api/admin/users/{user_id}")
def admin_update_user(user_id: int, req: UpdatePrivilegesRequest, username: str):
    """Изменение роли и лимитов пользователя."""
    role = auth.get_user_role(username)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен. Только для администратора школы.")

    success, msg = auth.update_user_privileges(user_id, req.role, req.max_requests, req.is_unlimited)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

@app.delete("/api/admin/users/{user_id}")
def admin_delete_user(user_id: int, username: str):
    """Удаление аккаунта пользователя (защита eciva и admin)."""
    role = auth.get_user_role(username)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен. Только для администратора школы.")

    success, msg = auth.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

@app.get("/api/terms")
def get_popular_terms():
    return {
        "ru": ["Что такое СДВГ?", "Что такое буллинг?", "Паническая атака", "Мне тревожно"],
        "uz": ["Diqqat yetishmasligi nima?", "Bulling nima?", "Qattiq hayajonlanyapman"],
        "en": ["What is ADHD?", "What is bullying?", "Panic attack coping"]
    }