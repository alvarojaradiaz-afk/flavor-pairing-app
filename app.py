import streamlit as st
import pandas as pd
from src.data_loader import load_foods, normalize_food
from src.scoring import rank_pairings
from src.pubchem_client import enrich_molecules
from src.literature import search_literature
from src.visualization import radial_matrix
from src.importers import load_user_csv, merge_imported_compounds

st.set_page_config(page_title="Matriz química de sabores", page_icon="🧪", layout="wide")

CUSTOM_CSS = """
<style>
.main { background: #f4e6ba; }
.block-container { padding-top: 2rem; }
.big-title { font-size: 3.2rem; font-weight: 900; letter-spacing: -0.04em; line-height: 0.95; }
.subtle { color: #64748b; }
.card { background: rgba(255,255,255,0.78); border: 1px solid rgba(255,255,255,0.75); border-radius: 28px; padding: 22px; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08); }
.metric-card { background: #020617; color: white; border-radius: 22px; padding: 18px; text-align: center; }
.pill { display:inline-block; padding: 5px 11px; margin: 3px; border-radius: 999px; border: 1px solid #e2e8f0; background: white; font-size: 0.82rem; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

@st.cache_data
def get_foods():
    return load_foods()

foods = get_foods()

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div style="font-weight:800; letter-spacing:0.22em; color:#64748b;">🧪 CHEMICAL FOOD PAIRING LAB</div>', unsafe_allow_html=True)
st.markdown('<div class="big-title">Matriz química de sabores</div>', unsafe_allow_html=True)
st.markdown('<p class="subtle">App local para combinar moléculas compartidas, descriptores sensoriales, contraste culinario y evidencia. Incluye enriquecimiento en vivo con PubChem y búsqueda bibliográfica en Europe PMC.</p>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([2.2, 1.0, 1.0])
with c1:
    query = st.text_input("Ingrediente", value="berberechos", placeholder="Ej: berberechos, tomate, fresa, café, chocolate, kombu...")
with c2:
    mode = st.selectbox("Modo de scoring", ["equilibrado", "quimico", "sensorial", "creativo"])
with c3:
    top_n = st.slider("Nº de pairings", 5, 15, 10)
st.markdown('</div>', unsafe_allow_html=True)

with st.expander("Importar CSV propio de compuestos alimentarios"):
    st.write("Formato mínimo: `food_name, compound_name, chemical_family, descriptor, evidence, concentration, unit, source`.")
    uploaded = st.file_uploader("Sube un CSV de FooDB/FlavorDB/VCF/papers ya transformado", type=["csv"])
    if uploaded:
        try:
            df_imported = load_user_csv(uploaded)
            foods = merge_imported_compounds(foods, df_imported)
            st.success(f"Importadas {len(df_imported)} filas. Se recalcularán los scores.")
            st.dataframe(df_imported.head(20), use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo importar el CSV: {e}")

base = normalize_food(query, foods)
ranked = rank_pairings(base, foods, mode=mode)
top = ranked[:top_n]

left, center, right = st.columns([0.9, 1.5, 0.9])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.caption("INGREDIENTE BASE")
    st.header(f"{base.get('emoji','')} {base['name']}")
    st.write(f"*{base.get('scientific','')}*")
    st.write(base.get("role", ""))
    st.subheader("Huella sensorial")
    prof = pd.DataFrame([{"descriptor": k, "intensidad": v} for k, v in base.get("profile", {}).items()]).sort_values("intensidad", ascending=False)
    st.bar_chart(prof.set_index("descriptor"))
    st.subheader("Moléculas / familias clave")
    mols = pd.DataFrame(base.get("molecules", []))
    if not mols.empty:
        cols = [c for c in ["spanish", "name", "family", "descriptor", "evidence"] if c in mols.columns]
        st.dataframe(mols[cols], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with center:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.caption("VISUALIZACIÓN RADIAL")
    st.subheader("Matriz de pairing")
    fig = radial_matrix(base, top, n=min(8, len(top)))
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Ranking")
    ranking_df = pd.DataFrame([{
        "pairing": f"{r.get('emoji','')} {r['name']}",
        "score_total": round(r["total"] * 100, 1),
        "quimica": round(r["molecular"] * 100, 1),
        "sensorial": round(r["sensory"] * 100, 1),
        "contraste": round(r["contrast"] * 100, 1),
        "evidencia": round(r["evidence"] * 100, 1),
        "categoria": r["category"]
    } for r in top])
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.caption("DETALLE DEL PAIRING")
    options = [r["name"] for r in top]
    selected_name = st.selectbox("Selecciona un pairing", options)
    selected = next(r for r in top if r["name"] == selected_name)
    st.header(f"{base['name']} + {selected['name']}")
    st.write(selected.get("role", ""))
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Score total", f"{round(selected['total']*100)}")
        st.metric("Química", f"{round(selected['molecular']*100)}")
    with m2:
        st.metric("Sensorial", f"{round(selected['sensory']*100)}")
        st.metric("Contraste", f"{round(selected['contrast']*100)}")
    if selected.get("shared_molecules"):
        st.write("**Moléculas compartidas:**")
        st.write(", ".join(selected["shared_molecules"]))
    if selected.get("shared_families"):
        st.write("**Familias compartidas:**")
        st.write(", ".join(selected["shared_families"]))
    st.write("**Moléculas del pairing seleccionado:**")
    st.dataframe(pd.DataFrame(selected.get("molecules", [])), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

t1, t2 = st.tabs(["🔎 PubChem en vivo", "📚 Literatura científica"])
with t1:
    st.subheader("Enriquecimiento químico con PubChem")
    st.write("Busca CID, fórmula, peso molecular, SMILES e InChIKey para las moléculas del ingrediente base y del pairing seleccionado.")
    molecules_to_enrich = base.get("molecules", []) + selected.get("molecules", [])
    if st.button("Enriquecer moléculas con PubChem"):
        with st.spinner("Consultando PubChem..."):
            enriched = enrich_molecules(molecules_to_enrich)
        st.dataframe(pd.DataFrame(enriched), use_container_width=True, hide_index=True)

with t2:
    st.subheader("Búsqueda bibliográfica en Europe PMC")
    st.write("Busca artículos sobre volátiles, aroma, flavor, GC-MS o metabolómica del ingrediente.")
    if st.button("Buscar literatura"):
        with st.spinner("Buscando en Europe PMC..."):
            lit = search_literature(base["name"], limit=10)
        if lit:
            for item in lit:
                title = item.get("title", "Sin título")
                year = item.get("year", "")
                journal = item.get("journal", "")
                url = item.get("url", "")
                st.markdown(f"**{title}**  \n{journal} · {year}  \n{url}")
                st.markdown("---")
        else:
            st.warning("No se encontraron resultados o no hubo conexión.")

st.markdown("---")
st.info("Limitación metodológica: PubChem normaliza moléculas, pero no resuelve por sí solo ingrediente → moléculas de sabor. Para esa capa necesitas FooDB, FlavorDB, VCF Online, datos propios o extracción de literatura.")
