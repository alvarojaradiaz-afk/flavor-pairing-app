import math
from typing import Dict, List, Set

def cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a.keys()) | set(b.keys())
    d = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = sum(a.get(k, 0.0) ** 2 for k in keys)
    nb = sum(b.get(k, 0.0) ** 2 for k in keys)
    if na == 0 or nb == 0:
        return 0.0
    return d / (math.sqrt(na) * math.sqrt(nb))

def molecule_names(food: dict) -> Set[str]:
    return {m["name"].strip().lower() for m in food.get("molecules", [])}

def molecule_families(food: dict) -> Set[str]:
    return {m.get("family", "").strip().lower() for m in food.get("molecules", []) if m.get("family")}

def evidence_mean(food: dict) -> float:
    vals = [float(m.get("evidence", 0.5)) for m in food.get("molecules", [])]
    return sum(vals) / len(vals) if vals else 0.4

def molecular_score(a: dict, b: dict) -> float:
    ma, mb = molecule_names(a), molecule_names(b)
    fa, fb = molecule_families(a), molecule_families(b)
    if not ma or not mb:
        return 0.0
    jaccard = len(ma & mb) / len(ma | mb)
    family_overlap = len(fa & fb) / len(fa | fb) if fa and fb else 0.0
    bonus = 0.0
    if any("sulfur" in f or "sulfurado" in f or "organosulfur" in f for f in fa) and any("sulfur" in f or "sulfurado" in f or "organosulfur" in f for f in fb):
        bonus += 0.10
    if any("amino acid" in f for f in fa) and any("amino acid" in f for f in fb):
        bonus += 0.08
    if any("aldehyde" in f for f in fa) and any("aldehyde" in f for f in fb):
        bonus += 0.05
    return min(1.0, 0.70 * jaccard + 0.30 * family_overlap + bonus)

def contrast_score(base: Dict[str, float], cand: Dict[str, float]) -> float:
    s = 0.0
    if base.get("marino", 0) > 0.4 or base.get("salino", 0) > 0.4:
        s += 0.32 * max(cand.get("acido", 0), cand.get("citrico", 0))
        s += 0.20 * max(cand.get("fresco", 0), cand.get("vegetal", 0))
    if base.get("graso", 0) < 0.2:
        s += 0.18 * cand.get("graso", 0)
    if base.get("umami", 0) > 0.35:
        s += 0.18 * max(cand.get("acido", 0), cand.get("herbal", 0), cand.get("fresco", 0))
    if base.get("dulce", 0) > 0.5:
        s += 0.22 * max(cand.get("acido", 0), cand.get("amargo", 0), cand.get("tostado", 0))
    if base.get("amargo", 0) > 0.4:
        s += 0.20 * max(cand.get("dulce", 0), cand.get("graso", 0), cand.get("acido", 0))
    return min(1.0, s)

def score_pairing(base: dict, candidate: dict, mode: str = "equilibrado") -> dict:
    weights = {
        "equilibrado": (0.38, 0.27, 0.25, 0.10),
        "quimico": (0.65, 0.22, 0.08, 0.05),
        "sensorial": (0.20, 0.58, 0.14, 0.08),
        "creativo": (0.22, 0.23, 0.45, 0.10),
    }.get(mode, (0.38, 0.27, 0.25, 0.10))
    q = molecular_score(base, candidate)
    sensory = cosine(base.get("profile", {}), candidate.get("profile", {}))
    contrast = contrast_score(base.get("profile", {}), candidate.get("profile", {}))
    evidence = min(1.0, (evidence_mean(base) + evidence_mean(candidate)) / 2)
    total = weights[0] * q + weights[1] * sensory + weights[2] * contrast + weights[3] * evidence
    shared_molecules = sorted(list(molecule_names(base) & molecule_names(candidate)))
    shared_families = sorted(list(molecule_families(base) & molecule_families(candidate)))
    return {"id": candidate["id"], "name": candidate["name"], "emoji": candidate.get("emoji", ""), "category": candidate.get("category", ""), "role": candidate.get("role", ""), "molecular": q, "sensory": sensory, "contrast": contrast, "evidence": evidence, "total": total, "shared_molecules": shared_molecules, "shared_families": shared_families, "molecules": candidate.get("molecules", []), "profile": candidate.get("profile", {})}

def rank_pairings(base: dict, candidates: List[dict], mode: str = "equilibrado") -> List[dict]:
    out = []
    for c in candidates:
        if c["id"] == base["id"]:
            continue
        out.append(score_pairing(base, c, mode))
    return sorted(out, key=lambda x: x["total"], reverse=True)
