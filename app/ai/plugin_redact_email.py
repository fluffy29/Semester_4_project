import re
from .plugins import plugins

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def redact_before(messages, ctx):
    redacted = []
    for m in messages:
        content = m.get("content")
        if content:
            content = EMAIL_RE.sub("[redacted-email]", content)
        redacted.append({**m, "content": content})
    return redacted


plugins.register_before(redact_before)
