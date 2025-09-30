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
df = pd.read_excel(file_path, dtype=str).fillna("")

# Columnas requeridas
cols = [
    "1.21 MUNICIPIO",
    "1.1 APELLIDO PATERNO",
    "1.2 APELLIDO MATERNO",
    "1.3 NOMBRE(S)",
    "1.4 CLAVE DE ARTESANO"
]

# Verifica que existan las columnas
for col in cols:
    if col not in df.columns:
        messagebox.showerror("Error", f"Falta la columna: {col}")
        exit()

# Crea columna de nombre completo (nombre, apellido paterno, apellido materno)
df["NOMBRE COMPLETO"] = (
    df["1.3 NOMBRE(S)"].str.strip() + " " +
    df["1.1 APELLIDO PATERNO"].str.strip() + " " +
    df["1.2 APELLIDO MATERNO"].str.strip()
).str.strip()

# Ordena por municipio
df_final = df[["1.21 MUNICIPIO", "1.4 CLAVE DE ARTESANO", "NOMBRE COMPLETO"]].sort_values(by=["1.21 MUNICIPIO"])

# Guarda el nuevo Excel
output_path = file_path.replace('.xlsx', '_NOMBRES_COMPLETOS.xlsx').replace('.xls', '_NOMBRES_COMPLETOS.xls')
df_final.to_excel(output_path, index=False)

messagebox.showinfo("Listo", f"Archivo guardado como:\n{output_path}")
print(f"Archivo guardado como: {output_path}")