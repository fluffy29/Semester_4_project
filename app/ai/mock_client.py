from typing import Any
from .base import AIClient
import re
import random
import math
import ast
 


class MockAIClient(AIClient):
    def __init__(self):
        self.responses = {
            # Greetings
            r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b": [
                "Hello! How can I help you today?",
                "Hi there! What would you like to know?",
                "Hey! I'm here to assist you with any questions.",
                "Hello! What can I do for you?"
            ],
            
            # How are you / status
            r"\b(how are you|how's it going|what's up)\b": [
                "I'm doing well, thank you for asking! How can I help you?",
                "I'm here and ready to help! What's on your mind?",
                "All good on my end! What would you like to discuss?"
            ],
            
            # Programming questions
            r"\b(python|javascript|react|code|programming|developer?|software)\b": [
                "I'd be happy to help with programming! What specific topic or problem are you working on?",
                "Programming is fascinating! Are you looking for help with a particular language or concept?",
                "I can assist with coding questions. What are you trying to build or debug?",
                "Great! I love discussing programming. What's your current project about?"
            ],
            
            # Math/calculations
            r"\b(math|calculate|equation|number|solve)\b": [
                "I can help with math problems! What calculation do you need assistance with?",
                "Math is one of my strengths. What equation or concept would you like to explore?",
                "I'd be happy to help with mathematical problems. What are you working on?"
            ],
            
            # Creative requests
            r"\b(write|create|story|poem|creative|imagine)\b": [
                "I love creative tasks! What kind of content would you like me to help create?",
                "Creative writing is fun! What theme or style are you interested in?",
                "I'd be excited to help with creative projects. What's your vision?"
            ],
            
            # Questions about AI/chatbots
            r"\b(what are you|who are you|ai|chatbot|assistant)\b": [
                "I'm an AI assistant designed to help answer questions and have conversations on a wide variety of topics.",
                "I'm a helpful AI chatbot! I can assist with information, problem-solving, creative tasks, and more.",
                "I'm an artificial intelligence assistant. I'm here to help with whatever you need!"
            ],
            
            # Help/assistance requests
            r"\b(help|assist|support|need)\b": [
                "Of course! I'm here to help. What do you need assistance with?",
                "I'd be glad to help! Can you tell me more about what you're looking for?",
                "Absolutely! What kind of support do you need?"
            ],
            
            # Thanks
            r"\b(thank|thanks|appreciate)\b": [
                "You're very welcome! Is there anything else I can help you with?",
                "Happy to help! Let me know if you have any other questions.",
                "My pleasure! Feel free to ask if you need anything else."
            ],
            
            # Weather (mock since we don't have real data)
            r"\b(weather|temperature|rain|sunny|cloudy)\b": [
                "I don't have access to real-time weather data, but I can help you think about weather-related questions!",
                "For current weather, I'd recommend checking a weather app or website. Is there something else I can help with?"
            ],
            
            # Goodbyes
            r"\b(bye|goodbye|see you|farewell)\b": [
                "Goodbye! It was great chatting with you. Come back anytime!",
                "See you later! Feel free to return if you have more questions.",
                "Farewell! Have a wonderful day!"
            ]
    }

    async def chat(self, messages: list[dict[str, str]], max_tokens: int, temperature: float) -> dict[str, Any]:
        last_user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "Hello")
        user_input = last_user.strip().lower()

        # Intent: math direct expression (very small safe evaluator)
        math_answer = self._maybe_do_math(user_input)
        if math_answer is not None:
            reply = math_answer
        else:
            # Essay intent
            if re.search(r"\b(write|make|create) (me )?(an? )?essay\b", user_input) or re.search(r"\bessay on|essay about\b", user_input):
                topic = self._extract_topic_for_essay(user_input)
                reply = self._generate_essay(topic, max_tokens)
            # How-to intent
            elif re.search(r"\bhow to (dance|cook|study|learn)\b", user_input):
                activity = re.findall(r"how to (\w+)", user_input)[0]
                reply = self._generate_howto(activity, max_tokens)
            # Specific domain topic (WW2)
            elif re.search(r"world war ?2|ww2", user_input):
                reply = self._ww2_summary(max_tokens)
            else:
                # Pattern-based quick responses
                reply = None
                for pattern, responses in self.responses.items():
                    if re.search(pattern, user_input, re.IGNORECASE):
                        reply = random.choice(responses)
                        break
                if not reply:
                    if "?" in last_user:
                        reply = (
                            "That's an interesting question. I don't have a knowledge base behind me, "
                            "but I can help you reason it out. Could you add a bit more detail?"
                        )
                    else:
                        reply = (
                            f"You mentioned: '{last_user[:80]}'. Could you clarify what aspect you want to dive into (summary, steps, examples, etc.)?"
                        )

        if len(reply) > max_tokens:
            reply = reply[: max_tokens - 3] + "..."

        # Approximate 'tokens' (very rough heuristic) by splitting on whitespace
        total_prompt_tokens = sum(len(m.get("content", "").split()) for m in messages)
        completion_tokens = len(reply.split())
        usage = {
            "promptTokens": total_prompt_tokens,
            "completionTokens": completion_tokens,
            "totalTokens": total_prompt_tokens + completion_tokens,
    }
        return {"reply": reply, "usage": usage}

    # --- helper methods ---
    def _maybe_do_math(self, text: str) -> str | None:
        if not re.fullmatch(r"[0-9xX*+\-\/() ^.]+", text.replace(" ", "")):
            return None
        # Replace common symbols
        expr = text.replace("x", "*").replace("X", "*")
        try:
            tree = ast.parse(expr, mode="eval")
            if not self._safe_ast(tree):
                return None
            result = eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, {})  # noqa: S307
            if isinstance(result, (int, float)):
                if isinstance(result, float):
                    if math.isclose(result, round(result)):
                        result = int(round(result))
                return f"Result: {result}"
        except Exception:
            return None
        return None

    def _safe_ast(self, node):
        allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.USub, ast.UAdd, ast.Load, ast.FloorDiv, ast.Constant, ast.LShift, ast.RShift, ast.BitXor, ast.BitOr, ast.BitAnd, ast.MatMult)
        if not isinstance(node, allowed):
            if isinstance(node, ast.Module):
                return all(self._safe_ast(n) for n in node.body)
            if isinstance(node, ast.BinOp):
                return self._safe_ast(node.left) and self._safe_ast(node.right) and self._safe_ast(node.op)
            if isinstance(node, ast.UnaryOp):
                return self._safe_ast(node.operand) and self._safe_ast(node.op)
            if isinstance(node, ast.Expression):
                return self._safe_ast(node.body)
            return False
        for child in ast.iter_child_nodes(node):
            if not self._safe_ast(child):
                return False
        return True

    def _extract_topic_for_essay(self, text: str) -> str:
        m = re.search(r"essay (on|about) (.+)", text)
        if m:
            return m.group(2).strip()
        after = re.split(r"essay", text, 1)
        if len(after) > 1:
            return after[1].strip(" :.,") or "a general topic"
        return "a general topic"

    def _generate_essay(self, topic: str, max_tokens: int) -> str:
        paragraphs = [
            f"Introduction: This short essay provides an overview of {topic}. While this mock system isn't a factual knowledge engine, it can structure ideas clearly.",
            f"Core Perspective: When thinking about {topic}, it helps to outline definitions, historical or contextual significance, key challenges, and typical approaches people take to understand or solve related problems.",
            f"Implications: Considering {topic} invites reflection on impact, trade‑offs, and future directions. A balanced view weighs benefits against limitations.",
            f"Conclusion: Summarizing {topic} involves restating the central idea, synthesizing main points, and suggesting a direction for deeper exploration." ,
        ]
        essay = "\n\n".join(paragraphs)
        if len(essay) > max_tokens:
            return essay[: max_tokens - 3] + "..."
        return essay

    def _generate_howto(self, activity: str, max_tokens: int) -> str:
        steps = [
            f"Goal: Learn how to {activity} effectively.",
            f"1. Basics: Break {activity} into fundamental components and practice them slowly.",
            f"2. Technique: Focus on form/posture/mechanics before speed or complexity.",
            f"3. Iteration: Practice in short, regular intervals; reflect after each session.",
            f"4. Feedback: Use recordings or an experienced observer to adjust.",
            f"5. Progression: Gradually layer difficulty once fundamentals feel natural.",
            f"6. Consistency: Small daily effort usually beats rare intense sessions.",
            f"Summary: Mastery of {activity} comes from structured repetition and mindful refinement.",
        ]
        text = "\n".join(steps)
        if len(text) > max_tokens:
            return text[: max_tokens - 3] + "..."
        return text

    def _ww2_summary(self, max_tokens: int) -> str:
        summary = (
            "World War II (1939–1945) was a global conflict involving most major powers, "
            "driven by territorial expansion, ideological clashes, and economic instability. "
            "Key theaters included Europe, the Pacific, North Africa, and the Atlantic. "
            "Consequences included unprecedented destruction, the Holocaust, the emergence of the US and USSR as superpowers, the founding of the UN, and accelerated decolonization. "
            "(Note: This is a concise synthesized summary from a mock model, not a sourced encyclopedia.)"
        )
        if len(summary) > max_tokens:
            return summary[: max_tokens - 3] + "..."
        return summary
