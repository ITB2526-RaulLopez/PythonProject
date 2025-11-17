import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from colorama import Fore, Style

# Carregar XML
tree = ET.parse("incidencies.xml")
root = tree.getroot()

incidencies = []
for inc in root.findall("incidencia"):
    data = {
        "id": inc.get("id"),
        "data": inc.find("data").text,
        "equip": inc.find("equip").text,
        "tipus": inc.find("tipus").text,
        "prioritat": int(inc.find("prioritat").text),
        "descripcio": inc.find("descripcio").text
    }
    # Filtrar dates errònies
    try:
        any = int(data["data"].split("/")[-1])
        if any > 2025:  # descartar futur massa llunyà
            continue
    except:
        continue
    incidencies.append(data)

# Mostrar incidències amb format
print(Fore.CYAN + "=== Llista d'incidències ===" + Style.RESET_ALL)
for inc in incidencies[:5]:  # només les primeres 5 per exemple
    print(f"{Fore.YELLOW}ID:{inc['id']}{Style.RESET_ALL} | "
          f"Equip: {inc['equip']} | "
          f"Tipus: {inc['tipus']} | "
          f"Prioritat: {inc['prioritat']}")

# Estadístiques
equips = Counter([i["equip"] for i in incidencies])
prioritats = Counter([i["prioritat"] for i in incidencies])

print(Fore.GREEN + "\n=== Estadístiques ===" + Style.RESET_ALL)
print("Total incidències:", len(incidencies))
print("Incidències per equip:", dict(equips))
print("Distribució per prioritat:", dict(prioritats))