import pandas as pd
from tkinter import Tk, filedialog
import os
import unicodedata
import shutil

# Función para quitar acentos
def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )

# Ocultar ventana principal
root = Tk()
root.withdraw()

# Seleccionar carpeta principal
folder_path = filedialog.askdirectory(
    title="Selecciona la carpeta principal con los archivos Excel"
)

if not folder_path:
    print("No se seleccionó ninguna carpeta.")
    exit()

# Carpeta de salida (misma ruta + '_convertido')
output_folder = folder_path + '_convertido'

# Copiar estructura de carpetas (sin archivos)
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
for dirpath, dirnames, filenames in os.walk(folder_path):
    rel_path = os.path.relpath(dirpath, folder_path)
    out_dir = os.path.join(output_folder, rel_path)
    os.makedirs(out_dir, exist_ok=True)

    for filename in filenames:
        if filename.lower().endswith(('.xlsx', '.xls')):
            file_path = os.path.join(dirpath, filename)
            try:
                df = pd.read_excel(file_path, dtype=str)
                df = df.fillna("0.00")
                output_path = os.path.splitext(os.path.join(out_dir, filename))[0] + '.txt'
                with open(output_path, 'w', encoding='cp1252') as f:
                    for _, row in df.iterrows():
                        cells = []
                        for cell in row:
                            cell_str = str(cell).strip()
                            if cell_str == "":
                                cells.append("")  # Celda vacía, no poner nada
                            elif cell_str == "0":
                                cells.append("0")  # Si es 0, poner 0
                            else:
                                cells.append(remove_accents(cell_str))
                        formatted_line = '"|"'.join(cells)
                        f.write(f'"{formatted_line}"\n')
                print(f"Convertido: {output_path}")
            except Exception as e:
                print(f"Error procesando {file_path}: {e}")

print(f"\nTodos los archivos han sido procesados en:\n{output_folder}")
