"""Motor de food pairing sobre datos (FlavorDB o semilla local).

Tres scores independientes:
  - quimico  : Jaccard ponderado por IDF sobre moléculas compartidas
  - sensorial: similitud coseno entre vectores de descriptores
  - contraste: reglas culinarias sobre los ejes sensoriales dominantes
El total combina los tres según el modo elegido.
"""
import math
import os
import pandas as pd

from culinary import AXES, AXIS_KEYWORDS, CONTRAST_MAP, MODES, descriptors_to_axes

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


class PairingEngine:
    def __init__(self, data_dir=DATA_DIR):
        foods = pd.read_csv(os.path.join(data_dir, "foods.csv"))
        comps = pd.read_csv(os.path.join(data_dir, "compounds.csv"))
        fc = pd.read_csv(os.path.join(data_dir, "food_compounds.csv"))
        syn = pd.read_csv(os.path.join(data_dir, "synonyms.csv"))

        self.foods = foods.set_index("food_id")
        self.desc = {
            r.compound_id: str(r.descriptors).split("@") if pd.notna(r.descriptors) else []
            for r in comps.itertuples()
        }
        self.compound_names = {r.compound_id: r.name for r in comps.itertuples()}
        # food_id -> set(compound_id)
        self.food_compounds = {}
        for r in fc.itertuples():
            self.food_compounds.setdefault(r.food_id, set()).add(r.compound_id)

        self.synonyms = {str(r.input).strip().lower(): r.food_id for r in syn.itertuples()}
        self.notes = {
            str(r.input).strip().lower(): (r.note if pd.notna(r.note) else "")
            for r in syn.itertuples()
        }

        # IDF: moléculas presentes en pocos alimentos pesan más (más discriminantes)
        n = len(self.food_compounds) or 1
        df = {}
        for comps_set in self.food_compounds.values():
            for c in comps_set:
                df[c] = df.get(c, 0) + 1
        self.idf = {c: math.log((n + 1) / (v + 0.5)) for c, v in df.items()}

        # Cache de vectores sensoriales por alimento
        self.axes_cache = {fid: self._axes(fid) for fid in self.food_compounds}

    # ---- resolución de nombre -> food_id ----
    def resolve(self, text):
        key = str(text).strip().lower()
        if key in self.synonyms:
            return self.synonyms[key], self.notes.get(key, "")
        # ¿coincide con un food_id o un name_es?
        for fid in self.food_compounds:
            row = self.foods.loc[fid]
            if key in (fid.lower(), str(row.get("name_es", "")).lower(), str(row.get("name", "")).lower()):
                return fid, ""
        return None, ""

    def _descs(self, fid):
        return [self.desc.get(c, []) for c in self.food_compounds.get(fid, set())]

    def _axes(self, fid):
        return descriptors_to_axes(self._descs(fid))

    # ---- scores ----
    def chemical(self, a, b):
        ca, cb = self.food_compounds.get(a, set()), self.food_compounds.get(b, set())
        inter = ca & cb
        union = ca | cb
        if not union:
            return 0.0, []
        wi = sum(self.idf.get(c, 0) for c in inter)
        wu = sum(self.idf.get(c, 0) for c in union)
        shared = sorted(inter, key=lambda c: -self.idf.get(c, 0))
        return (wi / wu if wu else 0.0), shared

    def sensory(self, a, b):
        va, vb = self.axes_cache[a], self.axes_cache[b]
        dot = sum(va[k] * vb[k] for k in AXES)
        na = math.sqrt(sum(v * v for v in va.values()))
        nb = math.sqrt(sum(v * v for v in vb.values()))
        return dot / (na * nb) if na and nb else 0.0

    def contrast(self, a, b):
        va, vb = self.axes_cache[a], self.axes_cache[b]
        # ejes dominantes del base (valor > 0.4)
        dom = [k for k in AXES if va[k] >= 0.4] or [max(AXES, key=lambda k: va[k])]
        wanted = set()
        for d in dom:
            wanted.update(CONTRAST_MAP.get(d, []))
        if not wanted:
            return 0.0
        return min(1.0, sum(vb[k] for k in wanted) / len(wanted))

    # ---- pairing completo ----
    def pair(self, base_input, mode="Equilibrado", top=12):
        base, note = self.resolve(base_input)
        if base is None:
            return None
        wq, ws, wc = MODES[mode]
        rows = []
        for cand in self.food_compounds:
            if cand == base:
                continue
            q, shared = self.chemical(base, cand)
            s = self.sensory(base, cand)
            c = self.contrast(base, cand)
            total = wq * q + ws * s + wc * c
            rows.append({
                "food_id": cand,
                "nombre": self.foods.loc[cand].get("name_es", cand),
                "quimico": round(q, 3),
                "sensorial": round(s, 3),
                "contraste": round(c, 3),
                "total": round(total, 3),
                "via": [self.compound_name(c2) for c2 in shared[:3]],
            })
        rows.sort(key=lambda r: -r["total"])
        return {
            "base": base,
            "nombre": self.foods.loc[base].get("name_es", base),
            "note": note,
            "axes": self.axes_cache[base],
            "pairings": rows[:top],
        }

    def compound_name(self, cid):
        return self.compound_names.get(cid, cid)


if __name__ == "__main__":
    eng = PairingEngine()

    for modo in ["Equilibrado", "Químico puro"]:
        res = eng.pair("berberecho", mode=modo, top=6)
        print(f"\n=== {res['nombre']}  ·  modo {modo}  {('· ' + res['note']) if res['note'] else ''}")
        print("ejes dominantes:", {k: v for k, v in res["axes"].items() if v >= 0.4})
        for r in res["pairings"]:
            print(f"  {r['nombre']:<14} total {r['total']:.2f}  "
                  f"[Q {r['quimico']:.2f} S {r['sensorial']:.2f} C {r['contraste']:.2f}]  "
                  f"vía: {', '.join(r['via']) or '—'}")
