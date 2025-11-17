import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime

XML_PATH = "/home/sjo/PycharmProjects/PythonProject/incidencies.xml"

# Camps esperats en ordre (si l'origen era CSV/ODS)
EXPECTED_FIELDS = [
    "marcaTemps", "nom", "correu", "sala", "data", "hora",
    "equip", "tipus", "descripcio", "prioritat", "comentaris"
]

NS = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
}

def safe_text(elem):
    return elem.text.strip() if elem is not None and elem.text else ""

def valid_any(any_str):
    # Acceptem anys raonables; filtrem barbaritats
    try:
        y = int(any_str)
        return 2000 <= y <= 2025
    except:
        return False

def parse_any_from_data(data_str):
    # Admet "dd/mm/yyyy" o "yyyy-mm-dd"
    if not data_str:
        return None
    data_str = data_str.strip()
    try:
        if "/" in data_str:
            return int(data_str.split("/")[-1])
        elif "-" in data_str:
            return int(data_str.split("-")[0])
    except:
        return None
    return None

def read_clean_xml(root):
    """Forma neta: <incidencies><incidencia id=...> ... </incidencia></incidencies>"""
    incidencies = []
    for inc in root.findall(".//incidencia"):
        rec = {}
        rec["id"] = inc.get("id") or ""
        for f in EXPECTED_FIELDS:
            rec[f] = safe_text(inc.find(f))
        # Filtre de dates
        any_ = parse_any_from_data(rec["data"])
        if any_ is None or not valid_any(str(any_)):
            continue
        incidencies.append(rec)
    return incidencies

def read_ods_xml(root):
    """Forma ODS: <table:table-row><table:table-cell> amb <text:p> a dins."""
    incidencies = []
    rows = root.findall(".//table:table-row", NS)
    if not rows:
        return incidencies

    # Intentem detectar si hi ha capçalera; si el primer row té textos “Marca de temps”, etc.
    header = None
    for row in rows:
        cells = row.findall("table:table-cell", NS)
        values = [safe_text(c.find("text:p", NS)) for c in cells]
        # considerem header si conté paraules clau
        if any("Marca" in v or "Nom" in v or "Correu" in v for v in values):
            header = values
            continue
        # Si no tenim header, assumim l'ordre EXPECTED_FIELDS
        rec = {}
        for i, field in enumerate(EXPECTED_FIELDS):
            rec[field] = values[i] if i < len(values) else ""
        rec["id"] = ""  # no hi ha ID en ODS; es podria generar si cal
        # Filtre de dates
        any_ = parse_any_from_data(rec["data"])
        if any_ is None or not valid_any(str(any_)):
            continue
        incidencies.append(rec)

    return incidencies

def load_incidencies(xml_path):
    # iterparse evita carregar tot el fitxer (millor per fitxers grans)
    context = ET.iterparse(xml_path, events=("start", "end"))
    _, root = next(context)  # primer element
    # intentem detectar forma
    if root.tag.endswith("incidencies") or root.find(".//incidencia") is not None:
        return read_clean_xml(root)
    else:
        return read_ods_xml(root)

def print_sample(incidencies, limit=10):
    print("=== Mostra d'incidències (fins a 10) ===")
    for i, inc in enumerate(incidencies[:limit], 1):
        print(f"{i}. {inc.get('marcaTemps','')} | {inc.get('nom','')} | {inc.get('sala','')}")
        print(f"   Data {inc.get('data','')} {inc.get('hora','')} | Equip: {inc.get('equip','')} | Tipus: {inc.get('tipus','')}")
        print(f"   Prioritat: {inc.get('prioritat','')} | Descripció: {inc.get('descripcio','')}")
        if inc.get("comentaris", ""):
            print(f"   Comentaris: {inc['comentaris']}")
        print("-" * 60)

def print_stats(incidencies):
    print("\n=== Estadístiques ===")
    total = len(incidencies)
    print(f"Total incidències: {total}")

    def count_by(field):
        c = Counter(inc.get(field, "") for inc in incidencies if inc.get(field, ""))
        return c.most_common()

    for field, label in [("equip", "per equip"), ("tipus", "per tipus"), ("prioritat", "per prioritat"), ("sala", "per sala")]:
        items = count_by(field)
        if not items:
            continue
        print(f"\nIncidències {label}:")
        for k, v in items[:10]:
            print(f"  {k}: {v}")

if __name__ == "__main__":
    try:
        incidencies = load_incidencies(XML_PATH)
        if not incidencies:
            print("No s'han trobat incidències vàlides (potser totes tenen dates fora de rang).")
        else:
            print_sample(incidencies, limit=10)
            print_stats(incidencies)
    except ET.ParseError as e:
        print(f"Error de parseig XML: {e}")
    except FileNotFoundError:
        print(f"No s'ha trobat el fitxer: {XML_PATH}")
    except Exception as e:
        print(f"S'ha produït un error: {e}")