import requests
from bs4 import BeautifulSoup
import os

# URL base de la página
base_url = "https://casart.info/CARDEXPRODUCTO2.PHP?swa=ae529c47959b655ee1d5290e7f0f2927&pagina="

# Carpeta donde se guardarán los archivos
output_folder = "cardex_respaldo"

# Crear la carpeta si no existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Cookies extraídas del navegador (puedes copiar las cookies de tu navegador usando las herramientas de desarrollo)
cookies = {
    'nombre_cookie': 'valor_cookie',  # Reemplazar con las cookies reales de tu sesión
}

# Cabeceras HTTP para emular un navegador normal (reemplazar con las cabeceras de tu navegador)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://casart.info/',  # Aquí deberías poner la URL de referencia
}

# Función para obtener y guardar el contenido de una página
def guardar_cardex(pagina):
    url = base_url + str(pagina)
    
    # Realizar la solicitud con cookies y cabeceras
    response = requests.get(url, cookies=cookies, headers=headers)

    if response.status_code == 200:
        print(f"Página {pagina} descargada exitosamente.")
        
        # Guardar el HTML completo para depuración
        with open(os.path.join(output_folder, f"cardex_completo_{pagina}.html"), 'w', encoding='utf-8') as file:
            file.write(response.text)
        
        # Procesar el contenido HTML de la página
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Depuración: Mostrar todo el HTML de la página
        print(f"Mostrando contenido completo de la página {pagina}:")
        print(soup.prettify())  # Esto imprime todo el HTML formateado

        # Ajusta esto según la estructura HTML
        contenido = soup.find('div', {'id': 'contenido'})  # Asegúrate de que esta etiqueta sea correcta
        
        if contenido:
            with open(os.path.join(output_folder, f"cardex_{pagina}.html"), 'w', encoding='utf-8') as file:
                file.write(str(contenido))
            print(f"Guardado cardex de la página {pagina}")
        else:
            print(f"No se encontró contenido específico en la página {pagina}")
    else:
        print(f"Error al acceder a la página {pagina} (Código de estado: {response.status_code})")

# Función principal para recorrer varias páginas
def respaldar_cardex(total_paginas):
    for pagina in range(1, total_paginas + 1):
        guardar_cardex(pagina)

# Número total de páginas a recorrer (ajustar según el número máximo de páginas que deseas respaldar)
total_paginas = 100  # Ajusta este número según el número total de páginas que crees que existen

# Iniciar el proceso de respaldo
respaldar_cardex(total_paginas)



creo que opuede ser por las credenciales, aqui esta la informacion por si te sirve , estas es la pagina del login

https://casart.info/INDEX2.PHP


y esto es el contenido de el cuadro del login 


<tbody><tr><td colspan="4" height="238">&nbsp;</td></tr>
  <tr>
    <th width="110">&nbsp;</th>
    <td height="36" valign="top" width="110"><span class="Estilo3">Usuario</span></td>
    <td valign="top" width="100"><label><input type="text" name="txtuser"></label></td>
    <th>&nbsp;</th>
    </tr>
  <tr>
  	<th>&nbsp;</th>
    <td height="36" valign="top"><span class="Estilo3">Contraseña</span></td>
    <td valign="top"><label><input type="password" name="txtpass"></label></td>
    <th>&nbsp;</th>
  </tr>
  
    
  <tr>
  	<th>&nbsp;</th>
    <td height="64" colspan="2"><div align="center"><font color="White"></font><br><input type="button" value="Continuar" class="botoncito" onclick="enviar(this.form)" name="envia"></div></td>
    <th>&nbsp;</th>    
    </tr>
 	<tr><td colspan="4">&nbsp;</td></tr>   
</tbody>