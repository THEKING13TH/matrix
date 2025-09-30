import pandas as pd
import smtplib
import os
from tkinter import Tk, filedialog, messagebox
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Configuración de colores y estilo para el mensaje (Morena)
COLOR_FONDO = "#800000"
COLOR_TEXTO = "#FFFFFF"
COLOR_BOTON = "#FFD700"

# Configura aquí tu servidor y credenciales
SMTP_SERVER = "smtp.office365.com"  # Outlook/Hotmail
SMTP_PORT = 587
EMAIL_USER = "TU_CORREO@outlook.com"
EMAIL_PASS = "TU_CONTRASEÑA"

# Selecciona el archivo Excel con los datos
root = Tk()
root.withdraw()
excel_path = filedialog.askopenfilename(
    title="Selecciona el archivo Excel con los datos de envío",
    filetypes=[("Archivos Excel", "*.xlsx *.xls")]
)
if not excel_path:
    messagebox.showerror("Error", "No se seleccionó archivo Excel.")
    exit()

df = pd.read_excel(excel_path, dtype=str).fillna("")

# Verifica columnas requeridas
for col in ["NOMBRE", "CORREO", "IMAGEN", "MENSAJE"]:
    if col not in df.columns:
        messagebox.showerror("Error", f"Falta la columna: {col}")
        exit()

estatus_envio = []

try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
except Exception as e:
    messagebox.showerror("Error", f"No se pudo conectar al servidor SMTP: {e}")
    exit()

for idx, row in df.iterrows():
    try:
        msg = MIMEMultipart('related')
        msg['From'] = EMAIL_USER
        msg['To'] = row["CORREO"]
        msg['Subject'] = f"Invitación personalizada para {row['NOMBRE']}"

        mensaje_html = f"""
        <html>
        <body style="background-color:{COLOR_FONDO}; color:{COLOR_TEXTO}; font-family:Arial, sans-serif; padding:20px;">
            <h2 style="color:{COLOR_BOTON};">¡Hola {row['NOMBRE']}!</h2>
            <p style="font-size:16px;">{row['MENSAJE']}</p>
            <img src="cid:invitacionimg" style="width:80%; border:4px solid {COLOR_BOTON}; margin-top:20px;">
            <p style="margin-top:30px; color:{COLOR_BOTON}; font-weight:bold;">¡Esperamos contar con tu presencia!</p>
            <p style="font-size:12px; color:#ccc;">Este mensaje fue enviado por el equipo de Morena</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(mensaje_html, 'html'))

        imagen_path = row["IMAGEN"]
        if not os.path.isfile(imagen_path):
            estatus_envio.append({"NOMBRE": row["NOMBRE"], "CORREO": row["CORREO"], "ESTATUS": "IMAGEN NO ENCONTRADA"})
            continue
        with open(imagen_path, 'rb') as img:
            mime_img = MIMEImage(img.read())
            mime_img.add_header('Content-ID', '<invitacionimg>')
            mime_img.add_header('Content-Disposition', 'inline', filename=os.path.basename(imagen_path))
            msg.attach(mime_img)

        server.sendmail(EMAIL_USER, row["CORREO"], msg.as_string())
        estatus_envio.append({"NOMBRE": row["NOMBRE"], "CORREO": row["CORREO"], "ESTATUS": "ENVIADO"})
    except Exception as e:
        estatus_envio.append({"NOMBRE": row["NOMBRE"], "CORREO": row["CORREO"], "ESTATUS": f"ERROR: {str(e)}"})

server.quit()

# Guarda el reporte de estatus
reporte_path = os.path.join(os.path.dirname(excel_path), "reporte_envio_invitaciones.xlsx")
pd.DataFrame(estatus_envio).to_excel(reporte_path, index=False)
messagebox.showinfo("Reporte", f"Envío terminado. Reporte guardado en:\n{reporte_path}")
print(f"Reporte guardado en: {reporte_path}")