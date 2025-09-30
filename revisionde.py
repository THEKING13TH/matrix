import pandas as pd
import re
from tkinter import Tk, filedialog, messagebox

# Oculta la ventana principal de Tkinter
root = Tk()
root.withdraw()

# Selecciona el archivo Excel
file_path = filedialog.askopenfilename(
    title="Selecciona el archivo Excel",
    filetypes=[("Archivos Excel", "*.xlsx *.xls")]
)
if not file_path:
    messagebox.showerror("Error", "No se seleccionó archivo.")
    exit()

# Expresión regular para caracteres válidos (letras, acentos, ñ, ü, espacios y puntos)
regex_validos = re.compile(r'[A-Za-zÁÉÍÓÚáéíóúÑñÜü.\s]')
# Expresión regular para detectar caracteres NO válidos (números o caracteres raros)
regex_no_validos = re.compile(r'[^A-Za-zÁÉÍÓÚáéíóúÑñÜü.\s]')

# Columnas a limpiar
cols = ["1.1 APELLIDO PATERNO", "1.2 APELLIDO MATERNO", "1.3 NOMBRE(S)"]

# Carga el archivo Excel
df = pd.read_excel(file_path)

# Función para limpiar los nombres
def limpiar_nombre(nombre):
    if pd.isnull(nombre):
        return ""
    return ''.join(regex_validos.findall(str(nombre)))

# Función para detectar si hay caracteres no válidos
def tiene_caracteres_raros(nombre):
    if pd.isnull(nombre):
        return False
    return bool(regex_no_validos.search(str(nombre)))

# Lista para el reporte de nombres corregidos
reporte_lista = []
for col in cols:
    if col in df.columns:
        for i, valor in df[col].items():
            if tiene_caracteres_raros(valor):
                corregido = limpiar_nombre(valor)
                reporte_lista.append({
                    "COLUMNA": col,
                    "ANTES": valor,
                    "DESPUES": corregido
                })
        # Limpia la columna en el DataFrame original
        df[col] = df[col].apply(limpiar_nombre)

# Crea el DataFrame del reporte
reporte = pd.DataFrame(reporte_lista, columns=["COLUMNA", "ANTES", "DESPUES"])

# Guarda el resultado limpio
output_path = file_path.replace('.xlsx', '_LIMPIO.xlsx').replace('.xls', '_LIMPIO.xls')
df.to_excel(output_path, index=False)

# Guarda el reporte de cambios
reporte_path = file_path.replace('.xlsx', '_REPORTE_CORRECCIONES.xlsx').replace('.xls', '_REPORTE_CORRECCIONES.xls')
reporte.to_excel(reporte_path, index=False)

messagebox.showinfo(
    "Limpieza completada",
    f"Archivo limpio guardado como:\n{output_path}\n\nReporte de correcciones guardado como:\n{reporte_path}"
)
print(f"Archivo limpio guardado como: {output_path}")
print(f"Reporte de correcciones guardado como: {reporte_path}")