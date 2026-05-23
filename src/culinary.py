"""Traducción de descriptores químicos a ejes sensoriales y reglas de contraste."""

# Cada eje sensorial se activa si el descriptor de una molécula contiene
# alguna de estas palabras clave (en inglés, como vienen en FlavorDB).
AXIS_KEYWORDS = {
    "Marino":    ["marine", "sea", "sulfur", "cabbage", "fishy", "oyster", "iodine"],
    "Umami":     ["umami", "savory", "brothy", "meaty", "broth"],
    "Dulce":     ["sweet", "honey", "caramel", "vanilla"],
    "Ácido":     ["sour", "acid", "acidic", "tart"],
    "Cítrico":   ["citrus", "lemon", "orange", "lime", "grapefruit"],
    "Vegetal":   ["green", "grassy", "cucumber", "herbal", "fresh", "leafy", "vegetable"],
    "Graso":     ["fatty", "buttery", "creamy", "milky", "oily", "cheesy"],
    "Floral":    ["floral", "violet", "rose", "jasmine"],
    "Frutal":    ["fruity", "peach", "berry", "strawberry", "apple", "tropical"],
    "Tostado":   ["smoky", "roasted", "toasted", "burnt", "coffee"],
    "Picante":   ["pungent", "spicy", "hot", "sharp"],
    "Amargo":    ["bitter"],
}

# Para un perfil dominante en X, ¿qué ejes en la pareja crean buen contraste?
CONTRAST_MAP = {
    "Marino":  ["Ácido", "Cítrico", "Graso", "Vegetal"],
    "Umami":   ["Ácido", "Cítrico", "Vegetal"],
    "Graso":   ["Ácido", "Cítrico", "Picante", "Amargo"],
    "Dulce":   ["Ácido", "Amargo", "Cítrico"],
    "Ácido":   ["Graso", "Dulce", "Umami"],
    "Cítrico": ["Graso", "Dulce", "Umami"],
    "Amargo":  ["Graso", "Dulce"],
    "Vegetal": ["Graso", "Umami"],
    "Frutal":  ["Ácido", "Graso"],
    "Tostado": ["Ácido", "Graso", "Vegetal"],
    "Picante": ["Graso", "Dulce"],
    "Floral":  ["Ácido", "Graso"],
}

AXES = list(AXIS_KEYWORDS.keys())

# Pesos por modo: (química, sensorial, contraste)
MODES = {
    "Equilibrado":  (0.30, 0.25, 0.45),
    "Químico puro": (0.70, 0.20, 0.10),
    "Sensorial":    (0.20, 0.55, 0.25),
    "Creativo":     (0.20, 0.20, 0.60),
}


def descriptors_to_axes(descriptor_lists):
    """descriptor_lists: lista de listas de descriptores (una por molécula).
    Devuelve un vector {eje: recuento normalizado 0-1}."""
    counts = {a: 0.0 for a in AXES}
    for descs in descriptor_lists:
        for d in descs:
            dl = d.lower()
            for axis, keys in AXIS_KEYWORDS.items():
                if any(k in dl for k in keys):
                    counts[axis] += 1
    m = max(counts.values()) or 1.0
    return {a: round(counts[a] / m, 3) for a in AXES}
