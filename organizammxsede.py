import pandas as pd
from tkinter import Tk, filedialog, messagebox

# Diccionario de municipios a sedes (puedes copiar y pegar el listado aquí)
municipio_a_sede = {
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

# Selecciona el archivo Excel original
root = Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    title="Selecciona el archivo Excel original",
    filetypes=[("Archivos Excel", "*.xlsx *.xls")]
)
if not file_path:
    messagebox.showerror("Error", "No se seleccionó archivo.")
    exit()

df = pd.read_excel(file_path, dtype=str)

# Agrega la columna SEDE al inicio
df.insert(0, "SEDE", df["1.21 MUNICIPIO"].map(municipio_a_sede).fillna("SIN SEDE"))

# Guarda el nuevo archivo
output_path = file_path.replace('.xlsx', '_CON_SEDE.xlsx').replace('.xls', '_CON_SEDE.xls')
df.to_excel(output_path, index=False)

messagebox.showinfo("Listo", f"Archivo guardado como:\n{output_path}")
print(f"Archivo guardado como: {output_path}")