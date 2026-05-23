import pandas as pd

EXPECTED_COLUMNS = ["food_name", "compound_name", "chemical_family", "descriptor", "evidence", "concentration", "unit", "source"]

def load_user_csv(path_or_buffer):
    df = pd.read_csv(path_or_buffer)
    missing = [c for c in ["food_name", "compound_name"] if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas obligatorias: {missing}")
    for c in EXPECTED_COLUMNS:
        if c not in df.columns:
            df[c] = None
    return df[EXPECTED_COLUMNS]

def _safe_float(x, default=0.5):
    try:
        return float(x)
    except Exception:
        return default

def merge_imported_compounds(foods, imported_df):
    foods = [dict(f) for f in foods]
    for _, row in imported_df.iterrows():
        fname = str(row["food_name"]).strip().lower()
        comp = {"name": str(row["compound_name"]).strip(), "spanish": str(row["compound_name"]).strip(), "family": str(row.get("chemical_family") or ""), "descriptor": str(row.get("descriptor") or ""), "evidence": _safe_float(row.get("evidence"), 0.5), "source": str(row.get("source") or "imported")}
        for f in foods:
            aliases = [a.lower() for a in f.get("aliases", [])] + [f.get("name", "").lower()]
            if fname in aliases:
                existing = {m["name"].lower() for m in f.get("molecules", [])}
                if comp["name"].lower() not in existing:
                    f.setdefault("molecules", []).append(comp)
    return foods
