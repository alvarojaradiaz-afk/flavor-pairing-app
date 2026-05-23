import json
from pathlib import Path
from typing import Dict, List, Tuple

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "seed_foods.json"

def load_foods() -> List[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def index_foods(foods: List[dict]) -> Tuple[Dict[str, dict], Dict[str, str]]:
    by_id = {f["id"]: f for f in foods}
    alias_to_id = {}
    for f in foods:
        alias_to_id[f["name"].lower()] = f["id"]
        for alias in f.get("aliases", []):
            alias_to_id[alias.lower()] = f["id"]
    return by_id, alias_to_id

def normalize_food(query: str, foods: List[dict]) -> dict:
    by_id, alias_to_id = index_foods(foods)
    q = (query or "").strip().lower()
    if not q:
        return by_id["cockles"]
    if q in alias_to_id:
        return by_id[alias_to_id[q]]
    for alias, fid in alias_to_id.items():
        if q in alias or alias in q:
            return by_id[fid]
    return by_id["cockles"]
