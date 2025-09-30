import os
import shutil
import pandas as pd
from tkinter import Tk, filedialog, messagebox

# Oculta la ventana principal de Tkinter
root = Tk()
root.withdraw()

# Selecciona el archivo Excel con la lista de números
excel_path = filedialog.askopenfilename(
    title="Selecciona el archivo Excel con la lista de números",
    filetypes=[("Archivos Excel", "*.xlsx *.xls")]
)
if not excel_path:
    messagebox.showerror("Error", "No se seleccionó archivo Excel.")
    exit()

# Lee la lista de números
df = pd.read_excel(excel_path, dtype=str)
if "NUMERO" not in df.columns:
    messagebox.showerror("Error", "El archivo Excel debe tener una columna llamada 'NUMERO'.")
    exit()
numeros = df["NUMERO"].astype(str).tolist()

# Selecciona la carpeta donde buscar los PDFs
carpeta_busqueda = filedialog.askdirectory(title="Selecciona la carpeta donde buscar los PDFs")
if not carpeta_busqueda:
    messagebox.showerror("Error", "No se seleccionó carpeta de búsqueda.")
    exit()

# Selecciona la carpeta destino para copiar los PDFs encontrados
carpeta_destino = filedialog.askdirectory(title="Selecciona la carpeta destino para los PDFs encontrados")
if not carpeta_destino:
    messagebox.showerror("Error", "No se seleccionó carpeta destino.")
    exit()

# Busca y copia los PDFs
reporte = []

for numero in numeros:
    patron = f"credencial_{numero}_"
    encontrados_archivos = []
    for carpeta_actual, _, archivos in os.walk(carpeta_busqueda):
        for archivo in archivos:
            if archivo.lower().startswith(patron.lower()) and archivo.lower().endswith('.pdf'):
                ruta_origen = os.path.join(carpeta_actual, archivo)
                ruta_destino = os.path.join(carpeta_destino, archivo)
                # Si ya existe, renombra para no sobrescribir
                contador = 1
                nombre_base, extension = os.path.splitext(archivo)
                while os.path.exists(ruta_destino):
                    ruta_destino = os.path.join(carpeta_destino, f"{nombre_base}_{contador}{extension}")
                    contador += 1
                shutil.copy2(ruta_origen, ruta_destino)
                encontrados_archivos.append(archivo)
    if len(encontrados_archivos) == 0:
        reporte.append({"NUMERO": numero, "ESTATUS": "NO ENCONTRADO", "ARCHIVO": ""})
    elif len(encontrados_archivos) == 1:
        reporte.append({"NUMERO": numero, "ESTATUS": "ENCONTRADO", "ARCHIVO": encontrados_archivos[0]})
    else:
        for archivo in encontrados_archivos:
            reporte.append({"NUMERO": numero, "ESTATUS": "DUPLICADO", "ARCHIVO": archivo})

# Reporte de resultados
reporte_path = os.path.join(carpeta_destino, "reporte_resultados.xlsx")
pd.DataFrame(reporte).to_excel(reporte_path, index=False)
messagebox.showinfo("Reporte", f"Proceso terminado.\nSe generó un reporte en:\n{reporte_path}")

print(f"Total registros procesados: {len(numeros)}")
print(f"Reporte generado en: {reporte_path}")