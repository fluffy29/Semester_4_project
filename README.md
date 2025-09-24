# GenAI Chat Backend (FastAPI)

A small, fully functional Python backend demonstrating Generative AI integration (OpenAI or local GPT4All), authentication, role management, and privacy by design.

## Quickstart

1. Create `.env` from example:

```bash
cp .env.example .env
```

2. Install dependencies (Python 3.11):

```bash
pip install -e .
```

Or with extras for local model (GPT4All):

```bash
pip install -e .[local]
Then download a compatible GGUF model (e.g., orca-mini) and set `GPT4ALL_MODEL_PATH` to its file path. Toggle provider via `AI_PROVIDER=gpt4all`.
```

3. Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Health:

```bash
curl http://localhost:8000/api/health
```

## Environment variables

- `APP_ENV`: dev|prod
- `APP_PORT`: server port
- `JWT_SECRET`: secret for HS256
- `JWT_EXPIRES_MIN`: token expiry minutes
- `AI_PROVIDER`: openai|gpt4all (toggle without code changes)
- `OPENAI_API_KEY`: OpenAI key
- `OPENAI_MODEL`: model id
- `GPT4ALL_MODEL_PATH`: path to GGUF model
- `MAX_TOKENS`: generation tokens
- `TEMPERATURE`: generation temperature
- `PRIVACY_STORE_MESSAGES`: if false, do not persist content

## Auth & Roles

- Login: `POST /api/auth/login` with `{email, password}` returns JWT.
- Roles: `student` can use chat and access own history; `admin` can list all conversations.
- Demo users: `student@example.com` and `admin@example.com` with password `password`.

## API reference

- `GET /api/health`
- `POST /api/auth/login`
- `POST /api/chat` body `{ message, conversationId? }` -> `{ conversationId, reply, usage, provider }`
- `GET /api/history` (student)
- `GET /api/history/{conversationId}` (student)
- `DELETE /api/history/{conversationId}` (student)
- `GET /api/admin/conversations` (admin)

## Privacy by design

- Controlled by `PRIVACY_STORE_MESSAGES`:
  - false: store only IDs and timestamps; messages content is not persisted and detail view is redacted.
  - true: persist messages per conversation.
- No prompts or replies are logged. Avoid placing secrets in prompts.
- Delete: `DELETE /api/history/{conversationId}` lets users erase a conversation.

## Security notes

- JWT auth (HS256) and simple role checks.
- Basic per-IP rate limit.
- Input validation (max message length).
- Secrets via env vars.
- See `app/security/threats.md` for threat list and countermeasures.

## Tests

Run tests:

```bash
pytest
```

Tests mock the AI client and cover login, chat flow, history, and role restrictions.

## Sample curl

```bash
# login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"student@example.com","password":"password"}' | jq -r .access_token)

# chat
curl -s -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello from student"}'

# history
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/history
```
# Semester_4_project
