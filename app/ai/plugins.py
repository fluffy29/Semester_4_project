from typing import Callable, List, Dict, Any

BeforeHook = Callable[[list[dict], Dict[str, Any]], list[dict]]
AfterHook = Callable[[str, Dict[str, Any]], str]


class PluginManager:
    def __init__(self) -> None:
        self._before: List[BeforeHook] = []
        self._after: List[AfterHook] = []
        return None

    def register_before(self, fn: BeforeHook) -> None:
        self._before.append(fn)

    def register_after(self, fn: AfterHook) -> None:
        self._after.append(fn)

    def run_before(self, messages: list[dict], ctx: Dict[str, Any]) -> list[dict]:
        for fn in self._before:
            messages = fn(messages, ctx)
        return messages

    def run_after(self, reply: str, ctx: Dict[str, Any]) -> str:
        for fn in self._after:
            reply = fn(reply, ctx)
        return reply


plugins = PluginManager()
