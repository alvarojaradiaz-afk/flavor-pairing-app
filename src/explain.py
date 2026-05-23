"""Capa de explicación opcional. El LLM SOLO redacta; los números vienen del motor.
Requiere:  pip install anthropic   y   export ANTHROPIC_API_KEY=...
El modelo se lee de ANTHROPIC_MODEL (consulta los modelos vigentes en
https://docs.claude.com). No se inventa ningún score aquí.
"""
import os


def explain_pairings(res, n=3):
    import anthropic

    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    client = anthropic.Anthropic()
    top = res["pairings"][:n]
    datos = "\n".join(
        f"- {r['nombre']}: total {r['total']}, química {r['quimico']}, "
        f"sensorial {r['sensorial']}, contraste {r['contraste']}, "
        f"moléculas compartidas: {', '.join(r['via']) or 'ninguna relevante'}"
        for r in top
    )
    prompt = (
        f"Ingrediente base: {res['nombre']}.\n"
        f"Maridajes calculados (NO los cambies, solo explícalos en lenguaje de cocina):\n{datos}\n\n"
        "Para cada uno, una frase breve explicando por qué funciona, distinguiendo si es "
        "por afinidad química (comparten moléculas) o por contraste. Español, conciso."
    )
    msg = client.messages.create(
        model=model, max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if b.type == "text")
