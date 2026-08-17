import re

EMPRESAS = [
    "Camanchaca",
    "AquaChile",
    "Mowi",
    "Cermaq",
    "Multiexport",
    "Abick",
    "Aquagen",
    "Salmones de Chile",
    "Blumar",
    "Ventisqueros",
    "Salmones Saysen",
    "Marine Farm",
    "Yadran",
    "Invermar",
    "Cooke",
    "Nova Austral",
    "Salmones Caleta Bay",
    "St-Andrews",
    "Salmones Magallanes",
    "Australis",
    "Aquasan",
    "Blu River",
    "Friosur",
    "Los Fiordos",
    "Salmones Austral",
    "Otro..."
]

MAPA_ABREVIATURAS_EMPRESAS = {
    "st": {"abbrev": "St", "empresa": "St-Andrews"},
    "mw": {"abbrev": "MW", "empresa": "Mowi"},
    "sm": {"abbrev": "SM", "empresa": "Salmones Magallanes"},
    "au": {"abbrev": "Au", "empresa": "Australis"},
    "ca": {"abbrev": "Ca", "empresa": "Camanchaca"},
    "ce": {"abbrev": "Ce", "empresa": "Cermaq"},
    "mef": {"abbrev": "Mef", "empresa": "Multiexport"},
    "ab": {"abbrev": "Ab", "empresa": "Abick"},
    "ac": {"abbrev": "AC", "empresa": "AquaChile"},
    "as": {"abbrev": "AS", "empresa": "Aquasan"},
    "sc": {"abbrev": "SC", "empresa": "Salmones de Chile"},
    "bl": {"abbrev": "Bl", "empresa": "Blumar"},
    "ve": {"abbrev": "VE", "empresa": "Ventisqueros"},
    "br": {"abbrev": "Br", "empresa": "Blu River"},
    "sa": {"abbrev": "SA", "empresa": "Salmones Saysen"},
    "mf": {"abbrev": "MF", "empresa": "Marine Farm"},
    "fs": {"abbrev": "FS", "empresa": "Friosur"},
    "ya": {"abbrev": "Ya", "empresa": "Yadran"},
    "in": {"abbrev": "In", "empresa": "Invermar"},
    "ck": {"abbrev": "Ck", "empresa": "Cooke"},
    "na": {"abbrev": "NA", "empresa": "Nova Austral"},
    "lf": {"abbrev": "LF", "empresa": "Los Fiordos"},
    "sal": {"abbrev": "SAL", "empresa": "Salmones Austral"},
    "cb": {"abbrev": "Cb", "empresa": "Salmones Caleta Bay"}
}


def parse_location_info(location: str):
    """
    Dada una cadena location (ej: 'ca-ahoni' o 'ce-tranqui1'),
    retorna (empresa_detectada, nombre_centro_formateado).
    Ejemplos:
      'ca-ahoni' -> ('Camanchaca', 'Ahoni')
      'ce-tranqui1' -> ('Cermaq', 'Tranqui 1')
    """
    if not location:
        return None, ""
    
    loc_clean = location.strip().lower()
    if not loc_clean:
        return None, ""
    
    parts = loc_clean.split("-", 1)
    prefix = parts[0]
    
    if len(parts) > 1:
        rest = parts[1]
        rest_formatted = re.sub(r'([a-zA-Z]+)(\d+)', r'\1 \2', rest)
        nombre_centro = rest_formatted.replace("-", " ").title()
    else:
        rest_formatted = re.sub(r'([a-zA-Z]+)(\d+)', r'\1 \2', loc_clean)
        nombre_centro = rest_formatted.replace("-", " ").title()

    if prefix in MAPA_ABREVIATURAS_EMPRESAS:
        empresa = MAPA_ABREVIATURAS_EMPRESAS[prefix]["empresa"]
        return empresa, nombre_centro
    
    return None, nombre_centro