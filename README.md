# Flavor Pairing Real App

App local para crear una matriz de **food pairing químico + sensorial**.

## Qué hace

- Introduces un ingrediente.
- La app busca su perfil en una base semilla local.
- Calcula pairings por afinidad química, similitud sensorial, contraste culinario y evidencia.
- Genera una matriz radial interactiva.
- Enriquece moléculas en vivo usando PubChem PUG-REST.
- Busca literatura científica en Europe PMC para el ingrediente.
- Permite importar datos propios de FooDB/FlavorDB/VCF si dispones de CSV/licencia.

## Instalación en Windows PowerShell

```powershell
cd C:\Users\TU_USUARIO\Desktop
Expand-Archive .\flavor_pairing_real_app.zip -DestinationPath .
cd .\flavor_pairing_real_app

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python -m streamlit run app.py
```

## Ingredientes incluidos inicialmente

berberechos, tomate, fresa, café, chocolate negro, kombu, dashi, miso blanco, yuzu/lima, limón, vinagre de Jerez, pepino, hinojo, perejil, cebollino/chalota, mantequilla, albariño/vino blanco, aceite de oliva, setas, soja, nori, almendra y vainilla.

## Importar datos propios

Formato mínimo recomendado:

```csv
food_name,compound_name,chemical_family,descriptor,evidence,concentration,unit,source
berberecho,Glutamate,amino acid,umami,0.8,,,seed
```

## Nota importante

PubChem normaliza moléculas, pero no resuelve de forma directa “ingrediente → moléculas de sabor”. Para eso necesitas bases como FooDB/FlavorDB/VCF o datos propios extraídos de literatura.
