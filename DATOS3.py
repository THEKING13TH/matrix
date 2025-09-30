import os
import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# -----------------------------
# Funciones auxiliares
# -----------------------------
def clean_label(label):
    label = re.sub(r'^\(\d+\)\s*\*?', '', label).strip()
    if label.endswith(":"):
        label = label[:-1].strip()
    return label

def extract_header_data(soup, header_text):
    for t in soup.find_all("table", border="1"):
        caption_td = t.find("td", string=lambda x: x and header_text in x)
        if caption_td:
            rows = t.find_all("tr")
            if len(rows) >= 1:
                first_row = rows[0]
                date_parts = [cell.get_text(strip=True) for cell in first_row.find_all("td")]
                return " ".join(part for part in date_parts if part).strip()
    return ""

def extract_clave_artesano(soup):
    span = soup.find("span", class_="Estilo2", string=lambda x: x and "CLAVE DEL ARTESANO" in x)
    if span:
        table = span.find_parent("table")
        if table:
            rows = table.find_all("tr")
            if len(rows) >= 2:
                return rows[1].get_text(strip=True)
    return ""

def extract_general_data(soup):
    general_data = {}
    for t in soup.find_all("table"):
        first_td = t.find("td", class_="Estilo1")
        if first_td and first_td.get_text(strip=True).startswith("(1)"):
            general_table = t
            break
    if general_table:
        rows = general_table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                for i in range(0, len(cells), 2):
                    if i + 1 < len(cells):
                        label_raw = cells[i].get_text(" ", strip=True)
                        value_raw = cells[i+1].get_text(" ", strip=True)
                        if label_raw:
                            label = clean_label(label_raw)
                            general_data[label] = value_raw
    return general_data

# -----------------------------
# Configuración principal
# -----------------------------
descargas_dir = "kardex_descargados"
os.makedirs(descargas_dir, exist_ok=True)

url_base = "https://casart.info/ARTESANO_KARDEX.PHP?swa=a263939b4370afd39f1fd5123aa210f9&ID={}"


inicio_id = 70000
fin_id = 80000

registros = []

def procesar_id(id_kardex):
    try:
        url = url_base.format(id_kardex)
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and "No encontrado" not in response.text:
            print(f"Procesando ID {id_kardex}...")
            soup = BeautifulSoup(response.text, "html.parser")
            
            registro = {"ID": id_kardex}
            registro["Clave Artesano"] = extract_clave_artesano(soup)
            registro["Fecha Credencializacion"] = extract_header_data(soup, "FECHA DE CREDENCIALIZACION")
            registro["Fecha Recredencializacion"] = extract_header_data(soup, "FECHA RECREDENCIALIZACION")
            
            datos_generales = extract_general_data(soup)
            registro.update(datos_generales)
            
            registros.append(registro)
            print(f"ID {id_kardex} procesado.")
        else:
            print(f"ID {id_kardex} no válido o sin datos.")
    except requests.RequestException as e:
        print(f"Error al conectar con el ID {id_kardex}: {e}")

# -----------------------------
# Proceso de descarga y extracción (concurrente)
# -----------------------------
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(procesar_id, range(inicio_id, fin_id + 1))

print("Proceso de descarga y extracción finalizado.")

# -----------------------------
# Exportar a Excel
# -----------------------------
if registros:
    df = pd.DataFrame(registros)
    output_excel = "kardex_datos.xlsx"
    df.to_excel(output_excel, index=False)
    print(f"Datos exportados a {output_excel}")
else:
    print("No se han obtenido registros.")
