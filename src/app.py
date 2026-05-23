"""App Streamlit. Ejecutar desde la raíz del proyecto:
    streamlit run src/app.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd
import streamlit as st
from culinary import AXES, MODES
from engine import PairingEngine

st.set_page_config(page_title="Matriz de pairing", page_icon="🧪", layout="centered")


@st.cache_resource
def load_engine():
    return PairingEngine()


eng = load_engine()

st.title("🧪 Matriz de pairing")
st.caption("Scores calculados sobre datos de moléculas (FlavorDB / dataset semilla). "
           "Química = moléculas compartidas (Jaccard ponderado por IDF) · "
           "Sensorial = coseno de descriptores · Contraste = reglas culinarias.")

col1, col2 = st.columns([3, 2])
with col1:
    ingrediente = st.text_input("Ingrediente", value="berberecho")
with col2:
    modo = st.selectbox("Modo", list(MODES.keys()))

res = eng.pair(ingrediente, mode=modo, top=15) if ingrediente.strip() else None

if res is None and ingrediente.strip():
    st.warning("No encuentro ese ingrediente en los datos. Añádelo a data/synonyms.csv "
               "o prueba con uno de estos:")
    st.write(", ".join(sorted(eng.foods["name_es"].dropna().tolist())))
elif res:
    st.subheader(res["nombre"])
    if res["note"]:
        st.caption("ℹ️ " + res["note"])

    # Huella sensorial
    axes_df = pd.DataFrame({"eje": AXES, "valor": [res["axes"][a] for a in AXES]})
    axes_df = axes_df[axes_df["valor"] > 0].set_index("eje")
    st.markdown("**Huella sensorial** (derivada de los descriptores de sus moléculas)")
    st.bar_chart(axes_df, height=220)

    # Matriz de pairing
    st.markdown("**Maridajes** (ordenados por score total)")
    table = pd.DataFrame([{
        "Ingrediente": r["nombre"],
        "Total": r["total"],
        "Química": r["quimico"],
        "Sensorial": r["sensorial"],
        "Contraste": r["contraste"],
        "Vía (moléculas compartidas)": ", ".join(r["via"]) or "—",
    } for r in res["pairings"]])
    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Total": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=float(table["Total"].max() or 1)),
            "Química": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
            "Sensorial": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
            "Contraste": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
        },
    )

    # Grafo de puentes moleculares (opcional: requiere networkx + matplotlib)
    with st.expander("Ver puentes moleculares (grafo)"):
        try:
            import matplotlib.pyplot as plt
            import networkx as nx

            G = nx.Graph()
            base = res["nombre"]
            G.add_node(base, kind="base")
            for r in res["pairings"][:6]:
                if r["quimico"] < 0.05 or not r["via"]:
                    continue
                G.add_node(r["nombre"], kind="pair")
                for mol in r["via"]:
                    G.add_node(mol, kind="mol")
                    G.add_edge(base, mol)
                    G.add_edge(mol, r["nombre"])
            if G.number_of_edges() == 0:
                st.info("No hay suficientes moléculas compartidas para dibujar el grafo.")
            else:
                pos = nx.spring_layout(G, seed=4, k=0.9)
                kinds = nx.get_node_attributes(G, "kind")
                colors = {"base": "#e3a948", "mol": "#5cb9a7", "pair": "#cccccc"}
                fig, ax = plt.subplots(figsize=(7, 5))
                nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
                for kind, col in colors.items():
                    nodes = [n for n in G if kinds.get(n) == kind]
                    nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=col,
                                           node_size=[700 if kind == "base" else 220 for _ in nodes], ax=ax)
                nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
                ax.axis("off")
                st.pyplot(fig)
        except ImportError:
            st.info("Instala networkx y matplotlib para ver el grafo.")

    # Explicación con LLM (opcional)
    if st.button("Explicar el top 3 (requiere ANTHROPIC_API_KEY)"):
        try:
            from explain import explain_pairings
            st.write(explain_pairings(res))
        except Exception as e:
            st.error(f"No disponible: {e}")
