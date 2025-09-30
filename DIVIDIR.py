import pandas as pd
from tkinter import Tk, filedialog, messagebox
import os
from fpdf import FPDF

# Mapeo de municipios a sedes (puedes cargarlo desde un archivo si lo prefieres)
municipio_sede = {
    "VILLA DE ALLENDE": "VILLA DE ALLENDE",
    "VALLE DE BRAVO": "VILLA DE ALLENDE",
    "DONATO GUERRA": "VILLA DE ALLENDE",
    "VILLA VICTORIA": "VILLA DE ALLENDE",
    "IXTAPAN DEL ORO": "VILLA DE ALLENDE",
    "TEMASCALTEPEC": "VILLA DE ALLENDE",
    "TEJUPILCO": "VILLA DE ALLENDE",
    "AMANALCO": "VILLA DE ALLENDE",
    "VILLA GUERRERO": "VILLA DE ALLENDE",
    "SAN FELIPE DEL PROGRESO": "SAN FELIPE DEL PROGRESO",
    "TEMASCALCINGO": "SAN FELIPE DEL PROGRESO",
    "IXTLAHUACA": "SAN FELIPE DEL PROGRESO",
    "EL ORO": "SAN FELIPE DEL PROGRESO",
    "ATLACOMULCO": "SAN FELIPE DEL PROGRESO",
    "SAN JOSÉ DEL RINCÓN": "SAN FELIPE DEL PROGRESO",
    "JIQUIPILCO": "SAN FELIPE DEL PROGRESO",
    "ACULCO": "SAN FELIPE DEL PROGRESO",
    "JOCOTITLAN": "SAN FELIPE DEL PROGRESO",
    "ACAMBAY": "SAN FELIPE DEL PROGRESO",
    "TENANCINGO": "TENANCINGO",
    "IXTAPAN DE LA SAL": "TENANCINGO",
    "ZUMPAHUACAN": "TENANCINGO",
    "COATEPEC HARINAS": "TENANCINGO",
    "TONATICO": "TENANCINGO",
    "TLATLAYA": "TENANCINGO",
    "ZACUALPAN": "TENANCINGO",
    "MALINALCO": "TENANCINGO",
    "ALMOLOYA DE ALQUISIRAS": "TENANCINGO",
    "METEPEC": "TOLUCA",
    "TIANGUISTENCO": "TOLUCA",
    "TOLUCA": "TOLUCA",
    "SAN MATEO ATENCO": "TOLUCA",
    "SAN ANTONIO LA ISLA": "TOLUCA",
    "TEMOAYA": "TOLUCA",
    "RAYÓN": "TOLUCA",
    "LERMA": "TOLUCA",
    "VILLA DEL CARBÓN": "TOLUCA",
    "ALMOLOYA DE JUAREZ": "TOLUCA",
    "ZINACANTEPEC": "TOLUCA",
    "MORELOS": "TOLUCA",
    "OTZOLOTEPEC": "TOLUCA",
    "OCOYOACAC": "TOLUCA",
    "CALIMAYA": "TOLUCA",
    "JILOTEPEC": "TOLUCA",
    "CHAPA DE MOTA": "TOLUCA",
    "NAUCALPAN DE JUÁREZ": "TOLUCA",
    "TIMILPAN": "TOLUCA",
    "MEXICALTZINGO": "TOLUCA",
    "ISIDRO FABELA": "TOLUCA",
    "XONACATLÁN": "TOLUCA",
    "HUIXQUILUCAN": "TOLUCA",
    "OCUILAN": "TOLUCA",
    "XALATLACO": "TOLUCA",
    "CAPULHUAC": "TOLUCA",
    "TENANGO DEL VALLE": "TOLUCA",
    "TEXCALYACAC": "TOLUCA",
    "ATIZAPÁN": "TOLUCA",
    "JOQUICINGO": "TOLUCA",
    "TEOTIHUACÁN": "TEXCOCO",
    "SAN MARTÍN DE LAS PIRÁMIDES": "TEXCOCO",
    "CHIMALHUACÁN": "TEXCOCO",
    "TEXCOCO": "TEXCOCO",
    "ATLAUTLA": "TEXCOCO",
    "CHICOLOAPAN": "TEXCOCO",
    "ATIZAPAN DE ZARAGOZA": "TEXCOCO",
    "IXTAPALUCA": "TEXCOCO",
    "OTUMBA": "TEXCOCO",
    "AMECAMECA": "TEXCOCO",
    "CHICONCUAC": "TEXCOCO",
    "NEZALHUALCOYOTL": "TEXCOCO",
    "ATENCO": "TEXCOCO",
    "ACOLMAN": "TEXCOCO",
    "CHALCO": "TEXCOCO",
    "NOPALTEPEC": "TEXCOCO",
    "TEPOTZOTLÁN": "TEXCOCO",
    "CUAUTITLÁN IZCALLI": "TEXCOCO",
    "LA PAZ": "TEXCOCO",
    "NICOLÁS ROMERO": "TEXCOCO",
    "VALLE DE CHALCO": "TEXCOCO",
    "ECATEPEC DE MORELOS": "TEXCOCO",
    "TEMASCALAPA": "TEXCOCO",
    "TLALNEPANTLA DE BAZ": "TEXCOCO",
    "CUAUTITLÁN": "TEXCOCO",
    "COCOTITLÁN": "TEXCOCO",
    "TEZOYUCA": "TEXCOCO",
    "TLALMANALCO": "TEXCOCO",
    "TULTITLÁN": "TEXCOCO",
    "TEPETLAOXTOC": "TEXCOCO",
    "ZUMPANGO": "TEXCOCO",
    "APAXCO": "TEXCOCO",
    "AYAPANGO": "TEXCOCO",
    "OZUMBA": "TEXCOCO",
    "AXAPUSCO": "TEXCOCO",
    "HUEHUETOCA": "TEXCOCO"
}

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

# Columnas requeridas (agregando la clave de artesano)
cols = [
    "1.21 MUNICIPIO",
    "1.1 APELLIDO PATERNO",
    "1.2 APELLIDO MATERNO",
    "1.3 NOMBRE(S)",
    "1.4 CLAVE DE ARTESANO",
    "1.23 TELÉFONO CELULAR",
    "1.24 TELÉFONO DE CONTACTO"
]

# Verifica que existan las columnas
for col in cols:
    if col not in df.columns:
        messagebox.showerror("Error", f"Falta la columna: {col}")
        exit()

# Crea columna de nombre completo
df["NOMBRE COMPLETO"] = (
    df["1.1 APELLIDO PATERNO"].str.strip() + " " +
    df["1.2 APELLIDO MATERNO"].str.strip() + " " +
    df["1.3 NOMBRE(S)"].str.strip()
).str.strip()

# Selecciona solo las columnas requeridas
df_final = df[["NOMBRE COMPLETO", "1.4 CLAVE DE ARTESANO", "1.23 TELÉFONO CELULAR", "1.24 TELÉFONO DE CONTACTO", "1.21 MUNICIPIO"]]

# Carpeta base para PDFs
pdf_folder_base = os.path.join(os.path.dirname(file_path), "PDFS_SEDES")
os.makedirs(pdf_folder_base, exist_ok=True)

# Divide por sede y municipio
resumen = {}

for municipio in sorted(df_final["1.21 MUNICIPIO"].unique()):
    sede = municipio_sede.get(municipio, "SIN_SEDE")
    pdf_folder_sede = os.path.join(pdf_folder_base, sede)
    os.makedirs(pdf_folder_sede, exist_ok=True)
    pdf_folder_muni = os.path.join(pdf_folder_sede, municipio)
    os.makedirs(pdf_folder_muni, exist_ok=True)

    df_muni = df_final[df_final["1.21 MUNICIPIO"] == municipio].copy()
    resumen[municipio] = len(df_muni)
    df_muni = df_muni.drop(columns=["1.21 MUNICIPIO"])
    df_muni.index = df_muni.index + 1  # Índice desde 1

    # Genera PDF para el municipio
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"MUNICIPIO: {municipio}", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Total de registros: {len(df_muni)}", ln=True)
    pdf.ln(5)
    # Encabezados
    pdf.set_font("Arial", "B", 10)
    pdf.cell(10, 8, "#", 1)
    pdf.cell(90, 8, "NOMBRE COMPLETO", 1)
    pdf.cell(35, 8, "CLAVE ARTESANO", 1)
    pdf.cell(25, 8, "CELULAR", 1)
    pdf.cell(25, 8, "CONTACTO", 1)
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    # Filas
    for idx, row in df_muni.iterrows():
        nombre_mayus = row["NOMBRE COMPLETO"].upper()[:30]
        pdf.cell(10, 8, str(idx), 1)
        pdf.cell(90, 8, nombre_mayus, 1)
        pdf.cell(35, 8, row["1.4 CLAVE DE ARTESANO"], 1)
        pdf.cell(25, 8, row["1.23 TELÉFONO CELULAR"], 1)
        pdf.cell(25, 8, row["1.24 TELÉFONO DE CONTACTO"], 1)
        pdf.ln()
    pdf.output(os.path.join(pdf_folder_muni, f"{municipio}_{len(df_muni)}.pdf"))

# Total de registros
total_registros = len(df_final)

# Mostrar resumen
resumen_str = "\n".join([f"{muni}: {count} registros" for muni, count in resumen.items()])
resumen_str += f"\n\nTotal de registros: {total_registros}"

messagebox.showinfo("Resumen por municipio", resumen_str + f"\n\nPDFs guardados en:\n{pdf_folder_base}")
print("Resumen por municipio:")
print(resumen_str)
print(f"PDFs guardados en: {pdf_folder_base}")