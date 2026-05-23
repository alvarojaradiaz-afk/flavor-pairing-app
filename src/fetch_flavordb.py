"""Descarga datos de FlavorDB y los vuelca a data/foods.csv, compounds.csv,
food_compounds.csv (mismo esquema que la semilla, así que la app los usa sin tocar nada).

IMPORTANTE — verifica el endpoint antes de bajar todo:
    python src/fetch_flavordb.py probe 1
Eso te imprime el JSON crudo de una entidad para que confirmes los nombres de los
campos. Si no coinciden con los de abajo, ajusta parse_entity().

Endpoints conocidos (FlavorDB v1, suele seguir activo y devuelve JSON parseable):
    https://cosylab.iiitd.edu.in/flavordb/entities_json?id=N
FlavorDB2 vive en /flavordb2/ y tiene más moléculas; si su JSON difiere, usa probe
para ver el formato y cambia BASE / parse_entity en consecuencia.

Descarga completa (ids 1..1000, con pausa para no saturar el servidor académico):
    python src/fetch_flavordb.py crawl --max-id 1000
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.request

BASE = "https://cosylab.iiitd.edu.in/flavordb/entities_json?id="
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
HEADERS = {"User-Agent": "flavor-pairing-mvp/1.0 (uso académico personal)"}


def fetch(entity_id):
    req = urllib.request.Request(BASE + str(entity_id), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def slug(s):
    return "".join(c if c.isalnum() else "_" for c in str(s).lower()).strip("_")


def parse_entity(j):
    """Devuelve (food_row, [(compound_id, name, descriptors), ...]) o None.
    Ajusta los nombres de campo aquí si tu `probe` muestra otros."""
    name = j.get("entity_alias_readable") or j.get("entity_alias") or j.get("natural_source_name")
    if not name:
        return None
    fid = slug(name)
    category = j.get("category_readable") or j.get("category") or ""
    food = {"food_id": fid, "name": name, "name_es": "", "category": category}

    comps = []
    for m in j.get("molecules", []):
        cid = m.get("pubchem_id") or m.get("pubchem_compound_id")
        cname = m.get("common_name") or m.get("name") or str(cid)
        if cid is None:
            continue
        prof = m.get("flavor_profile") or m.get("fooddb_flavor_profile") or ""
        descriptors = "@".join(d for d in str(prof).replace(",", "@").split("@") if d.strip())
        comps.append((f"cid_{cid}", cname, descriptors))
    return food, comps


def crawl(max_id, delay):
    foods, compounds, links = {}, {}, set()
    ok = 0
    for i in range(1, max_id + 1):
        try:
            j = fetch(i)
            parsed = parse_entity(j)
            if not parsed:
                continue
            food, comps = parsed
            foods[food["food_id"]] = food
            for cid, cname, desc in comps:
                compounds[cid] = (cid, cname, desc)
                links.add((food["food_id"], cid))
            ok += 1
            if ok % 25 == 0:
                print(f"  {ok} ingredientes... (id {i})", file=sys.stderr)
        except Exception as e:
            pass  # ids inexistentes / errores puntuales: se ignoran
        time.sleep(delay)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "foods.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["food_id", "name", "name_es", "category"])
        for r in foods.values():
            w.writerow([r["food_id"], r["name"], r["name_es"], r["category"]])
    with open(os.path.join(DATA_DIR, "compounds.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["compound_id", "name", "descriptors"])
        for cid, cname, desc in compounds.values():
            w.writerow([cid, cname, desc])
    with open(os.path.join(DATA_DIR, "food_compounds.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["food_id", "compound_id"])
        for fid, cid in sorted(links):
            w.writerow([fid, cid])
    print(f"\nListo: {len(foods)} ingredientes, {len(compounds)} moléculas, "
          f"{len(links)} enlaces -> data/*.csv")
    print("Recuerda: añade name_es y completa data/synonyms.csv para tus ingredientes.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe"); p.add_argument("id", type=int)
    c = sub.add_parser("crawl")
    c.add_argument("--max-id", type=int, default=1000)
    c.add_argument("--delay", type=float, default=0.4)
    a = ap.parse_args()

    if a.cmd == "probe":
        j = fetch(a.id)
        print("CLAVES DE LA ENTIDAD:", list(j.keys()))
        mols = j.get("molecules", [])
        print("nº moléculas:", len(mols))
        if mols:
            print("CLAVES DE UNA MOLÉCULA:", list(mols[0].keys()))
            print("EJEMPLO:", json.dumps(mols[0], ensure_ascii=False)[:400])
        print("\n¿parse_entity la entiende? ->", bool(parse_entity(j)))
    elif a.cmd == "crawl":
        crawl(a.max_id, a.delay)
