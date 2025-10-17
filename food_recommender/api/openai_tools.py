"""OpenAI Tools / Function definitions for controlled vocabulary tagging."""
from typing import Dict, Any, List, Optional


DEFAULT_VOCAB: Dict[str, List[str]] = {
    "category": [
        "한식", "중식", "일식", "양식", "분식", "디저트", "카페/베이커리",
        "패스트푸드", "아시안", "인도", "지중해", "멕시칸", "치킨", "피자",
    ],
    "dishes": [
        # 한식
        "김치찌개", "된장찌개", "비빔밥", "불고기", "삼겹살", "삼계탕", "냉면", "갈비탕",
        # 중식/일식/양식 등
        "짜장면", "짬뽕", "마라탕", "탕수육", "초밥", "라멘", "우동", "돈카츠",
        "파스타", "피자", "스테이크", "버거", "샐러드", "샌드위치",
        # 분식/디저트
        "떡볶이", "순대", "김밥", "치킨", "도넛", "케이크", "아이스크림",
    ],
    "taste": [
        "매운맛", "단맛", "짠맛", "신맛", "쓴맛", "담백함", "고소함", "감칠맛",
    ],
    "nutrition": [
        "고단백", "저지방", "고지방", "저칼로리", "고칼로리", "저탄수", "고탄수", "고섬유",
    ],
}


def build_tools(vocab: Optional[Dict[str, List[str]]] = None) -> List[Dict[str, Any]]:
    """Return OpenAI tool schema that forces the model to emit only allowed tags.

    The tool function name is 'emit_tags' and parameters are arrays constrained by enums.
    """
    v = vocab or DEFAULT_VOCAB
    def arr_enum(enum_list: List[str]) -> Dict[str, Any]:
        return {
            "type": "array",
            "items": {"type": "string", "enum": enum_list},
            "uniqueItems": True,
            "default": [],
        }

    return [
        {
            "type": "function",
            "function": {
                "name": "emit_tags",
                "description": "이미지에서 추출된 태그를 사전에 정의된 목록으로만 반환합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": arr_enum(v.get("category", [])),
                        "dishes": arr_enum(v.get("dishes", [])),
                        "taste": arr_enum(v.get("taste", [])),
                        "nutrition": arr_enum(v.get("nutrition", [])),
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
        }
    ]


def default_vocab() -> Dict[str, List[str]]:
    return DEFAULT_VOCAB
