import requests
import time
from functools import lru_cache

BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IsomericSMILES,InChIKey/JSON"

@lru_cache(maxsize=512)
def lookup_compound(name: str) -> dict:
    clean = (name or "").strip()
    if not clean:
        return {"query": name, "found": False, "error": "empty query"}
    url = BASE.format(name=requests.utils.quote(clean))
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "FlavorPairingLocalApp/0.1"})
        if r.status_code != 200:
            return {"query": name, "found": False, "status_code": r.status_code}
        data = r.json()
        props = data.get("PropertyTable", {}).get("Properties", [])
        if not props:
            return {"query": name, "found": False}
        p = props[0]
        time.sleep(0.15)
        return {"query": name, "found": True, "cid": p.get("CID"), "formula": p.get("MolecularFormula"), "mw": p.get("MolecularWeight"), "canonical_smiles": p.get("CanonicalSMILES"), "isomeric_smiles": p.get("IsomericSMILES"), "inchikey": p.get("InChIKey")}
    except Exception as e:
        return {"query": name, "found": False, "error": str(e)}

def enrich_molecules(molecules):
    rows = []
    seen = set()
    for m in molecules:
        name = m.get("name", str(m))
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        info = lookup_compound(name)
        rows.append({**m, **info})
    return rows
