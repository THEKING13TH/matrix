import os
import shutil
from tkinter import Tk, filedialog

def obtener_tipo_archivo(extension):
    tipos = {
        'Documentos': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'Imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        'Audio': ['.mp3', '.wav', '.aac', '.flac'],
        'Video': ['.mp4', '.avi', '.mov', '.wmv', '.mkv'],
        'Comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Ejecutables': ['.exe', '.msi', '.bat', '.sh'],
        'Otros': []
    }
    for tipo, extensiones in tipos.items():
        if extension.lower() in extensiones:
            return tipo
    return 'Otros'

def organizar_por_tipo_y_indole(ruta_base):
    for carpeta_actual, subcarpetas, archivos in os.walk(ruta_base):
        for archivo in archivos:
            ruta_archivo = os.path.join(carpeta_actual, archivo)
            extension = os.path.splitext(archivo)[1]
            tipo = obtener_tipo_archivo(extension)
            indole = os.path.basename(carpeta_actual)
            carpeta_destino = os.path.join(ruta_base, tipo, indole)
            os.makedirs(carpeta_destino, exist_ok=True)
            nuevo_path = os.path.join(carpeta_destino, archivo)
            if os.path.abspath(ruta_archivo) != os.path.abspath(nuevo_path):
                shutil.move(ruta_archivo, nuevo_path)

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    ruta = filedialog.askdirectory(title="Selecciona la carpeta a organizar")
    if ruta:
        organizar_por_tipo_y_indole(ruta)
        print("Organización completada.")
    else:
        print("No se seleccionó ninguna carpeta.")