"""Simple preferences backed by a JSON file under data/exports/preferences.json."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


PREF_PATH = (Path(__file__).resolve().parents[2] / "food_recommender" / "data" / "exports" / "preferences.json")


DEFAULT_PREFS: Dict[str, Any] = {
    "city": "",  # 예: "서울", "경주"
    "last_foods": [],  # ["비빔밥", "파스타"]
    "mood": "보통",  # "기쁨", "피곤", "스트레스", ...
    "search_radius_m": 2000,
}


def load_prefs() -> Dict[str, Any]:
    try:
        if PREF_PATH.exists():
            data = json.loads(PREF_PATH.read_text(encoding="utf-8"))
            # 최소 마이그레이션: 과거 location(lat/lng)만 저장됐던 경우 city 필드 보정
            if "city" not in data:
                data["city"] = ""
            # 불리한 키 제거는 하지 않고, 필요한 키만 기본값 채움
            for k, v in DEFAULT_PREFS.items():
                data.setdefault(k, v)
            return data
    except Exception:
        pass
    return DEFAULT_PREFS.copy()


def save_prefs(prefs: Dict[str, Any]) -> None:
    PREF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREF_PATH.write_text(json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")


__all__ = ["load_prefs", "save_prefs", "DEFAULT_PREFS", "PREF_PATH"]
