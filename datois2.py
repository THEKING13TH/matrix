import os
import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

# -----------------------------
# Funciones auxiliares
# -----------------------------
def clean_label(label):
    """
    Limpia la cadena quitando el número entre paréntesis, asteriscos y dos puntos finales.
    Ejemplo: "(1) *APELLIDO PATERNO :" -> "APELLIDO PATERNO"A
    """
    label = re.sub(r'^\(\d+\)\s*\*?', '', label).strip()
    if label.endswith(":"):
        label = label[:-1].strip()
    return label

def extract_header_data(soup, header_text):
    """
    Busca en todas las tablas con border=1 aquella que tenga en alguno de sus td el texto header_text.
    Se asume que la primera fila contiene las partes de la fecha.
    Retorna la cadena con la fecha (concatenando los textos de los td de la primera fila).
    """
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
    """
    Busca la tabla que contiene el <span> con "CLAVE DEL ARTESANO" y extrae el valor (se
    asume que se halla en la segunda fila de esa tabla).
    """
    span = soup.find("span", class_="Estilo2", string=lambda x: x and "CLAVE DEL ARTESANO" in x)
    if span:
        table = span.find_parent("table")
        if table:
            rows = table.find_all("tr")
            if len(rows) >= 2:
                return rows[1].get_text(strip=True)
    return ""

def extract_general_data(soup):
    """
    Busca la tabla que contiene los datos generales (se asume que el primer td de la tabla inicia con "(1)")
    y extrae las parejas (etiqueta, valor) de cada campo.
    """
    general_data = {}
    general_table = None
    # Buscamos la tabla cuyo primer td tenga texto que comience con "(1)"
    for t in soup.find_all("table"):
        first_td = t.find("td", class_="Estilo1")
        if first_td and first_td.get_text(strip=True).startswith("(1)"):
            general_table = t
            break

    if general_table:
        rows = general_table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            # Se procesan de a pares: [etiqueta, valor] (si hay 4 celdas se obtienen dos pares)
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
# Carpeta para guardar los HTML (opcional)
descargas_dir = "kardex_descargados"
os.makedirs(descargas_dir, exist_ok=True)

# URL base con parámetro ID
url_base = "https://casart.info/CARDEXPRODUCTO2.PHP?swa=ae529c47959b655ee1d5290e7f0f2927&amp;pagina={}&amp;orden=&amp;sucursal=001&amp;CVEPROD=&amp;CVEART=&amp;DIA1=12&amp;MES1=02&amp;ANIO1=2000&amp;DIA2=12&amp;MES2=02&amp;ANIO2=2025&amp;inicia=2"

# Rango de IDs a descargar (ajusta según sea necesario)
inicio_id = 1
fin_id = 100
#70086

# Lista donde se almacenan los registros extraídos
registros = []

# -----------------------------
# Proceso de descarga y extracción
# -----------------------------
for id_kardex in range(inicio_id, fin_id + 1):
    try:
        url = url_base.format(id_kardex)
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and "No encontrado" not in response.text:
            print(f"Procesando ID {id_kardex}...")
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Diccionario para el registro actual
            registro = {"ID": id_kardex}
            
            # Extraer "Clave del Artesano"
            registro["Clave Artesano"] = extract_clave_artesano(soup)
            
            # Extraer fechas de Credencialización y Recredencialización
            registro["Fecha Credencializacion"] = extract_header_data(soup, "FECHA DE CREDENCIALIZACION")
            registro["Fecha Recredencializacion"] = extract_header_data(soup, "FECHA RECREDENCIALIZACION")
            
            # Extraer datos generales (por ejemplo: APELLIDO PATERNO, NOMBRE(S), etc.)
            datos_generales = extract_general_data(soup)
            registro.update(datos_generales)
            
            registros.append(registro)
            
            # (Opcional) Guardar la página HTML descargada
            archivo_nombre = os.path.join(descargas_dir, f"kardex_{id_kardex}.html")
            with open(archivo_nombre, "w", encoding="utf-8") as archivo:
                archivo.write(response.text)
            print(f"Guardado HTML: {archivo_nombre}")
        else:
            print(f"ID {id_kardex} no válido o sin datos.")
    except requests.RequestException as e:
        print(f"Error al conectar con el ID {id_kardex}: {e}")
    
    # Espera breve para no sobrecargar el servidor (opcional)
    time.sleep(1)

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
