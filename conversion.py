from tkinter import filedialog, Tk
import os

# Ocultar ventana principal
root = Tk()
root.withdraw()

# Seleccionar archivo(s) .txt codificados en UTF-8
file_paths = filedialog.askopenfilenames(
    title="Selecciona archivo(s) TXT en UTF-8",
    filetypes=[("Text files", "*.txt")]
)

if not file_paths:
    print("No se seleccionó ningún archivo.")
    exit()

for file_path in file_paths:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Crear archivo de salida con el mismo nombre + "_ansi"
    base, ext = os.path.splitext(file_path)
    output_path = base + "_ansi" + ext

    with open(output_path, 'w', encoding='cp1252', errors='replace') as f:
        f.write(content)

    print(f"Convertido a ANSI: {output_path}")
