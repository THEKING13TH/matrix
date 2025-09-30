import pypff
import pandas as pd
from tkinter import Tk, filedialog, messagebox

# Selecciona el archivo PST
root = Tk()
root.withdraw()
pst_path = filedialog.askopenfilename(
    title="Selecciona el archivo PST de Outlook",
    filetypes=[("Archivos PST", "*.pst")]
)
if not pst_path:
    messagebox.showerror("Error", "No se seleccionó archivo PST.")
    exit()

pst_file = pypff.file()
pst_file.open(pst_path)

# Busca la carpeta de contactos
def find_contacts_folder(folder):
    if folder.name and "contact" in folder.name.lower():
        return folder
    for subfolder in folder.sub_folders:
        result = find_contacts_folder(subfolder)
        if result:
            return result
    return None

contacts_folder = find_contacts_folder(pst_file.get_root_folder())
if not contacts_folder:
    messagebox.showerror("Error", "No se encontró la carpeta de contactos.")
    exit()

# Extrae los contactos
contactos = []
for i in range(contacts_folder.number_of_sub_messages):
    msg = contacts_folder.get_sub_message(i)
    nombre = msg.get_value_string(0x3001)  # PR_DISPLAY_NAME
    correo = msg.get_value_string(0x39FE)  # PR_EMAIL_ADDRESS
    telefono = msg.get_value_string(0x3A08)  # PR_BUSINESS_TELEPHONE_NUMBER
    movil = msg.get_value_string(0x3A1C)    # PR_MOBILE_TELEPHONE_NUMBER
    empresa = msg.get_value_string(0x3A16)  # PR_COMPANY_NAME
    puesto = msg.get_value_string(0x3A17)   # PR_TITLE
    direccion = msg.get_value_string(0x3A19) # PR_BUSINESS_ADDRESS
    contactos.append({
        "NOMBRE": nombre,
        "CORREO": correo,
        "TELÉFONO": telefono,
        "MÓVIL": movil,
        "EMPRESA": empresa,
        "PUESTO": puesto,
        "DIRECCIÓN": direccion
    })

# Guarda en Excel
output_path = pst_path.replace('.pst', '_CONTACTOS.xlsx')
pd.DataFrame(contactos).to_excel(output_path, index=False)
messagebox.showinfo("Listo", f"Archivo guardado como:\n{output_path}")
print(f"Archivo guardado como: {output_path}")