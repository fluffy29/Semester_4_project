import os
import sys
import json
import readline  # noqa: F401
from pathlib import Path
import urllib.request
from urllib.error import HTTPError, URLError

API_URL = os.environ.get("CHAT_API_URL", "http://127.0.0.1:8000/api")
TOKEN_FILE = Path("/tmp/chat_token.txt")


def load_token() -> str:
    if not TOKEN_FILE.exists():
        print("Token file not found. Run 'make login' first.")
        sys.exit(1)
    return TOKEN_FILE.read_text().strip()


def send_message(token: str, message: str, conversation_id: str | None) -> dict:
    payload = {
        "message": message,
        "conversationId": conversation_id,
        "maxTokens": 256,
        "temperature": 0.4,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{API_URL}/chat",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        try:
            body = e.read().decode()
        except Exception:
            body = ""
        print(f"HTTP {e.code}: {body}")
        return {}
    except (URLError, Exception) as e:  # noqa: BLE001
        print(f"Error: {e}")
        return {}


def main():
    token = load_token()
    conversation_id = None
    print("Simple Chat REPL. Type /exit to quit, /new to start new conversation.")
    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in {"/exit", "/quit"}:
            break
        if user_input.lower() in {"/new", "/reset"}:
            conversation_id = None
            print("(started new conversation)")
            continue
        result = send_message(token, user_input, conversation_id)
        if not result:
            continue
        conversation_id = result.get("conversationId", conversation_id)
        print(f"AI> {result.get('reply','(no reply)')}")


if __name__ == "__main__":
    main()
