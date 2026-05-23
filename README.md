# Matriz de pairing — app real (MVP)

Calcula maridajes a partir de datos de moléculas, no de la intuición de un modelo.
Tres scores: **química** (Jaccard ponderado por IDF sobre moléculas compartidas),
**sensorial** (coseno de descriptores) y **contraste** (reglas culinarias).
El total se combina según el modo, con el contraste pesando más por defecto
(la afinidad química predice peor en cocina mediterránea).

## Estructura
```
data/        foods.csv, compounds.csv, food_compounds.csv, synonyms.csv
src/         engine.py · culinary.py · app.py · fetch_flavordb.py · explain.py
```

## Arrancar ya (con el dataset semilla de ejemplo)
```bash
pip install -r requirements.txt
streamlit run src/app.py
```
Trae ~11 ingredientes reales para que veas el flujo funcionando.

## Probar solo el motor (sin interfaz)
```bash
python src/engine.py
```

## Cargar los datos reales de FlavorDB (sustituye la semilla)
1. **Verifica el endpoint** (imprime el JSON de una entidad):
   ```bash
   python src/fetch_flavordb.py probe 1
   ```
   Si los nombres de campo no coinciden con los de `parse_entity()`, ajústalos ahí.
2. **Descarga** (con pausa para no saturar el servidor académico):
   ```bash
   python src/fetch_flavordb.py crawl --max-id 1000
   ```
   Esto reescribe `data/foods.csv`, `compounds.csv`, `food_compounds.csv`.
3. Completa `data/synonyms.csv` (berberecho -> almeja/clam, etc.) y, si quieres,
   la columna `name_es` de `foods.csv` para tus ingredientes.

## Explicación con LLM (opcional)
El modelo solo redacta; nunca calcula el score.
```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-...
export ANTHROPIC_MODEL=<modelo vigente, ver https://docs.claude.com>
```

## Avisos honestos
- FlavorDB es de **uso no comercial**. Para un producto, revisa licencia.
- Sin datos de concentración no hay **OAV** real; el peso por IDF es un sustituto
  razonable (prioriza moléculas discriminantes), no equivale al OAV de laboratorio.
- El mapeo descriptor->eje sensorial (`culinary.py`) es editable: es donde metes
  tu criterio de cocina.
