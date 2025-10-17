"""Simple next-menu recommender.

주요 규칙(맛 전환 테이블):

이전에 먹은 맛 -> 이후에 당기는 맛 (우선순위 순)
 - 짠맛 -> [단맛, 신맛]          # 단짠 조합은 보상 자극↑ / 짠 뒤에 신맛은 상쾌함
 - 단맛 -> [짠맛, 쓴맛, 담백함]  # 단 뒤엔 피로 → 자극적/깔끔한 맛 선호
 - 신맛 -> [단맛, 고소함]        # 산미로 침 분비↑ → 단맛 감도 상승
 - 쓴맛 -> [단맛]                # 쓴맛 거부 후 단맛으로 보상(커피→디저트)
 - 매운맛 -> [단맛, 짠맛, 담백함]# 자극 후 진정/보상(매운→단/짠/담백)
 - 담백함 -> [짠맛, 단맛, 감칠맛]# 자극 약해 강한 맛 그리움
 - 고소함 -> [신맛, 단맛]        # 지방감 중화 위해 산미/단미 전환
 - 감칠맛 -> [신맛, 단맛]        # 입안 무거움 → 산뜻/가벼운 맛 선호

이 모듈은 위 규칙을 반영해 taste를 추천하고, category는 이전과 다른 것으로 순환 추천합니다.
"""
from __future__ import annotations

from typing import Dict, List, Optional


def _pick_next_different(items: List[str], last_item: Optional[str]) -> Optional[str]:
    if not items:
        return None
    if not last_item or last_item not in items:
        return items[0]
    if len(items) == 1:
        return items[0]
    idx = items.index(last_item)
    # pick next in a circular fashion to differ from last
    return items[(idx + 1) % len(items)]


def recommend_next(last_category: Optional[str], last_taste: Optional[str], vocab: Dict[str, List[str]]) -> Dict[str, Optional[str]]:
    """Return a simple recommendation dict with a different category/taste.

    Returns: {"category": str|None, "taste": str|None}
    """
    categories = list(vocab.get("category", []))
    tastes = list(vocab.get("taste", []))
    rec_cat = _pick_next_different(categories, last_category)
    rec_taste = _pick_next_different(tastes, last_taste)
    return {"category": rec_cat, "taste": rec_taste}


# 맛 전환 규칙(우선순위 배열)
TASTE_TRANSITION_RULES: Dict[str, List[str]] = {
    "짠맛": ["단맛", "신맛"],
    "단맛": ["짠맛", "쓴맛", "담백함"],
    "신맛": ["단맛", "고소함"],
    "쓴맛": ["단맛"],
    "매운맛": ["단맛", "짠맛", "담백함"],
    "담백함": ["짠맛", "단맛", "감칠맛"],
    "고소함": ["신맛", "단맛"],
    "감칠맛": ["신맛", "단맛"],
}


def recommend_next_by_rules(
    last_category: Optional[str],
    last_taste: Optional[str],
    vocab: Dict[str, List[str]],
) -> Dict[str, Optional[str]]:
    """Rule-based recommendation using taste transition table.

    - taste: follow TASTE_TRANSITION_RULES if possible; otherwise fallback to cyclic different pick
    - category: pick a different one cyclically vs last_category
    """
    categories = list(vocab.get("category", []))
    tastes = list(vocab.get("taste", []))

    # category: keep it different from last
    rec_cat = _pick_next_different(categories, last_category)

    # taste: prefer rule-based next tastes that exist in vocab
    rec_taste: Optional[str] = None
    if last_taste and last_taste in TASTE_TRANSITION_RULES:
        for cand in TASTE_TRANSITION_RULES[last_taste]:
            if cand in tastes:
                rec_taste = cand
                break
    if rec_taste is None:
        rec_taste = _pick_next_different(tastes, last_taste)

    return {"category": rec_cat, "taste": rec_taste}


__all__ = ["recommend_next", "recommend_next_by_rules", "TASTE_TRANSITION_RULES"]
