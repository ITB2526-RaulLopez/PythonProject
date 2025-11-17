import xml.etree.ElementTree as ET

# Carregar el fitxer XML
tree = ET.parse("incidencies.xml")
root = tree.getroot()

# Llista per guardar les incidències
incidencies = []

# Recorrem cada incidència
for inc in root.findall("incidencia"):
    id_incidencia = inc.get("id")
    equip = inc.find("equip").text if inc.find("equip") is not None else "Desconegut"
    tipus = inc.find("tipus").text if inc.find("tipus") is not None else "Desconegut"
    prioritat = inc.find("prioritat").text if inc.find("prioritat") is not None else "0"

    incidencies.append((id_incidencia, equip, tipus, prioritat))

# Mostrar les primeres incidències
print("=== Llista d'incidències ===")
for i in incidencies[:5]:
    print(f"ID: {i[0]} | Equip: {i[1]} | Tipus: {i[2]} | Prioritat: {i[3]}")

# Estadístiques senzilles
print("\nTotal incidències:", len(incidencies))