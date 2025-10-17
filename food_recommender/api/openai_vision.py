"""OpenAI Vision + Tools: only emit predefined tags for a given food image."""
from typing import Dict, Any
import base64
from pathlib import Path
import os
import mimetypes
import json
from dotenv import load_dotenv

from .openai_tools import build_tools, default_vocab


def _b64_of(path: str) -> str:
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode("utf-8")


def _guess_mime(path: str) -> str:
    mt, _ = mimetypes.guess_type(path)
    return mt or "image/jpeg"


def analyze_image(image_path: str) -> Dict[str, Any]:
    """Analyze the food image and return structured tags using OpenAI vision + tools.

    Returns a dict with keys: category, dishes, taste, nutrition.
    If OpenAI API key is not configured or an error occurs, returns empty tags.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"category": [], "dishes": [], "taste": [], "nutrition": []}

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        image_b64 = _b64_of(image_path)
        mime = _guess_mime(image_path)
        tools = build_tools(default_vocab()) #tools로 정해진 태그 전달 

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "사진 속 음식에 대해, 도구 emit_tags만 호출하여 사전 정의된 태그로만 반환하세요."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{image_b64}", "detail": "low"},
                    },
                ],
            }
        ]

        # Vision + tool calling (Chat Completions API)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0,
        )

        choice = resp.choices[0]
        msg = choice.message
        tool_calls = getattr(msg, "tool_calls", None) 
        if tool_calls:
            for call in tool_calls:
                fn = call.function
                if fn and fn.name == "emit_tags": # function name check
                    # arguments is a JSON string per OpenAI function calling
                    args = json.loads(fn.arguments or "{}")
                    return {
                        "category": args.get("category", []),
                        "dishes": args.get("dishes", []),
                        "taste": args.get("taste", []),
                        "nutrition": args.get("nutrition", []),
                    }
        # No tool call → return empty
        return {"category": [], "dishes": [], "taste": [], "nutrition": []}
    except Exception as e:
        # Optional: log e
        return {"category": [], "dishes": [], "taste": [], "nutrition": []}
