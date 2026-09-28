# Son of Albert (Empasis AI)

Asynchronous backend service and school educational assistant built with FastAPI, Pydantic, and local LLM integration (Ollama).

Empasis AI is designed as a domain-specific digital assistant for educational environments, supporting multi-language conversational sessions (Uzbek, Russian, English) with strict role segregation and content safety validation.

---

## Architecture Overview

```
backend/
├── api.py               # FastAPI application entry point, middleware, routes
├── main.py              # Standalone CLI interface
├── requirements.txt     # Python dependencies
├── core/
│   ├── brain.py         # EmpasisBrain: LLM orchestration and context management
│   ├── safety.py        # SafetyGuard: content filters and crisis classification
│   └── mailer.py        # System alert and notification service
└── storage/
    ├── auth.py          # User management and authentication
    ├── chat_storage.py  # Session persistence and conversation history
    └── knowledge.py     # Domain pedagogical knowledge base
```

---

## Key Features

- **FastAPI Core:** Asynchronous REST API utilizing Pydantic v2 schemas for strict request/response data validation.
- **Local Model Execution:** Direct integration with Ollama runtime (Qwen models) without external API dependencies.
- **Multi-language Support:** Native dialogue handling in Uzbek, Russian, and English.
- **SafetyGuard Layer:** Automated detection of distress markers with rule-based safety intervention.
- **Role Differentiation:** Distinct prompting logic separating personal student venting from 3rd-person teacher/parent pedagogical inquiries.
- **Session Management:** Multi-chat tracking with configurable request limits and token controls.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Ollama installed and running locally

### Installation

1. Clone repository:
```bash
git clone https://github.com/Kocksxdoze/Son-of-Albert.git
cd Son-of-Albert/backend
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Pull local model:
```bash
ollama run qwen2.5:1.5b
```

5. Start the API server:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Interactive API documentation available at `http://localhost:8000/docs`.

---

## API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/chat` | Send message and receive response from EmpasisBrain |
| `POST` | `/api/chat/stream` | Stream LLM response chunks via SSE |
| `POST` | `/api/auth/register` | Register new user account |
| `POST` | `/api/auth/login` | Authenticate user and return session token |
| `GET` | `/api/chats` | Retrieve conversation history for active session |

---

## Author

- **Albert Xalikov** — [GitHub](https://github.com/Kocksxdoze) | [Telegram](https://t.me/eciva3)
