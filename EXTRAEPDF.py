import os
import shutil
from tkinter import Tk, filedialog, messagebox

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

# Busca y copia los PDF que empiezan con una clave
copiados = 0
for carpeta_actual, _, archivos in os.walk(origen):
    for archivo in archivos:
        if archivo.lower().endswith('.pdf'):
            nombre_base = os.path.splitext(archivo)[0]
            # Extrae el primer "palabra" antes de cualquier espacio o guion
            clave_archivo = nombre_base.split()[0].split('-')[0]
            if clave_archivo in claves:
                ruta_origen = os.path.join(carpeta_actual, archivo)
                ruta_destino = os.path.join(destino, archivo)
                # Si el archivo ya existe en destino, renombra para evitar sobrescribir
                contador = 1
                while os.path.exists(ruta_destino):
                    ruta_destino = os.path.join(destino, f"{nombre_base}_{contador}.pdf")
                    contador += 1
                shutil.copy2(ruta_origen, ruta_destino)
                copiados += 1

messagebox.showinfo("Listo", f"Se copiaron {copiados} archivos PDF a:\n{destino}")
print(f"Se copiaron {copiados} archivos PDF a: {destino}")