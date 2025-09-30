import pandas as pd
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

# Lee el Excel
df = pd.read_excel(file_path, dtype=str)
df = df.fillna("")

# Columnas que NO se convierten a mayúsculas
omit_cols = [
    "1.12.1 SUBIR CURP",
    "1.9 SUBIR DOCUMENTO DE IDENTIFICACIÓN",
    "1.4.1 SUBIR CREDENCIAL DE ARTESANO"
]

# Convierte a mayúsculas solo las columnas que no están en omit_cols
for col in df.columns:
    if col not in omit_cols:
        df[col] = df[col].apply(lambda x: x.upper() if isinstance(x, str) else x)

# Guarda el nuevo archivo Excel
output_path = file_path.replace('.xlsx', '_MAYUS.xlsx').replace('.xls', '_MAYUS.xls')
df.to_excel(output_path, index=False)

messagebox.showinfo("Conversión completada", f"Archivo guardado como:\n{output_path}")
print(f"Archivo guardado como: {output_path}")