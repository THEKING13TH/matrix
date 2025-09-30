import os
import shutil
from tkinter import Tk, filedialog, messagebox
import re

# Oculta la ventana principal de Tkinter
root = Tk()
root.withdraw()

# Selecciona el archivo TXT con las claves
txt_path = filedialog.askopenfilename(
    title="Selecciona el archivo TXT con las claves",
    filetypes=[("Archivos de texto", "*.txt")]
)
if not txt_path:
    messagebox.showerror("Error", "No se seleccionó archivo TXT.")
    exit()

# Lee las claves del TXT (una por renglón, sin espacios)
with open(txt_path, "r", encoding="utf-8") as f:
    claves = set(line.strip() for line in f if line.strip())

if not claves:
    messagebox.showerror("Error", "No se encontraron claves en el TXT.")
    exit()

# Selecciona la carpeta origen
origen = filedialog.askdirectory(title="Selecciona la carpeta de origen")
if not origen:
    messagebox.showerror("Error", "No se seleccionó carpeta de origen.")
    exit()

# Selecciona la carpeta destino
destino = filedialog.askdirectory(title="Selecciona la carpeta de destino")
if not destino:
    messagebox.showerror("Error", "No se seleccionó carpeta de destino.")
    exit()

# Busca y copia los PDF que tienen el número después de 'credencial_'
copiados = 0
patron = re.compile(r'^credencial_(\d+)_', re.IGNORECASE)
for carpeta_actual, _, archivos in os.walk(origen):
    for archivo in archivos:
        if archivo.lower().endswith('.pdf'):
            match = patron.match(archivo)
            if match:
                numero = match.group(1)
                if numero in claves:
                    ruta_origen = os.path.join(carpeta_actual, archivo)
                    ruta_destino = os.path.join(destino, archivo)
                    # Si el archivo ya existe en destino, renombra para evitar sobrescribir
                    contador = 1
                    nombre_base, extension = os.path.splitext(archivo)
                    while os.path.exists(ruta_destino):
                        ruta_destino = os.path.join(destino, f"{nombre_base}_{contador}{extension}")
                        contador += 1
                    shutil.copy2(ruta_origen, ruta_destino)
                    copiados += 1

messagebox.showinfo("Listo", f"Se copiaron {copiados} archivos PDF a:\n{destino}")
print(f"Se copiaron {copiados} archivos PDF a: {destino}")