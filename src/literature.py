import requests
from functools import lru_cache

EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

@lru_cache(maxsize=128)
def search_literature(ingredient: str, limit: int = 8):
    query = f'(\"{ingredient}\") AND (flavour OR flavor OR volatile OR aroma OR \"GC-MS\" OR metabolomics)'
    params = {"query": query, "format": "json", "pageSize": limit}
    try:
        r = requests.get(EUROPE_PMC, params=params, timeout=15, headers={"User-Agent": "FlavorPairingLocalApp/0.1"})
        if r.status_code != 200:
            return []
        data = r.json()
        results = data.get("resultList", {}).get("result", [])
        out = []
        for item in results:
            out.append({"title": item.get("title", ""), "journal": item.get("journalTitle", ""), "year": item.get("pubYear", ""), "doi": item.get("doi", ""), "pmid": item.get("pmid", ""), "url": f"https://europepmc.org/article/MED/{item.get('pmid')}" if item.get("pmid") else (f"https://doi.org/{item.get('doi')}" if item.get("doi") else "")})
        return out
    except Exception:
        return []
