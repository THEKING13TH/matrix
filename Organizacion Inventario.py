import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from bs4 import BeautifulSoup

def cargar_archivo():
    """Abre un cuadro de diálogo para seleccionar un archivo HTML y lo muestra en una tabla ordenada con filtros."""
    archivo = filedialog.askopenfilename(filetypes=[("Archivos HTML", "*.html")])
    
    if not archivo:
        messagebox.showwarning("Aviso", "No se seleccionó ningún archivo.")
        return
    
    try:
        # Cargar el archivo HTML
        with open(archivo, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Parsear el contenido HTML con BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Encontrar la fila de encabezados
        header_row = soup.find('tr', class_='caption')
        headers = [header.text.strip() for header in header_row.find_all('td')]

        # Asegurarse de que el encabezado tiene 13 columnas
        if len(headers) != 13:
            headers.append('VENTA')  # Aseguramos que el encabezado tenga 13 columnas

        # Crear una lista para almacenar los datos
        data = []

        # Buscar las filas con la clase 'controls' que contienen los datos
        rows = soup.find_all('tr', class_='controls')

        # Iterar sobre las filas de datos
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip().replace('&nbsp;', '') for ele in cols]  # Extraer texto y limpiar espacios

            # Ajustar el formato de la columna de la venta (con el signo de dólar)
            venta = row.find('th')  # La venta está en una etiqueta <th>
            if venta:
                cols.append(venta.text.strip().replace('&nbsp;', '').replace('$', '').replace(',', ''))
            else:
                cols.append('')  # Si no existe la venta, agregar una columna vacía

            print(f"Fila: {cols}, Longitud: {len(cols)}")  # Imprime la longitud y los datos de cada fila

            # Verificar si la fila es la de 'TOTALES' y evitarla o agregar valores vacíos
            if 'TOTALES' in cols:
                print(f"Fila 'TOTALES' detectada, ignorando o agregando valores vacíos.")
                continue  # Ignorar esta fila completamente
            elif len(cols) == len(headers):  # Si tiene el número correcto de columnas
                data.append(cols)
            elif len(cols) == len(headers) - 1:  # En caso de que falte la columna 'VENTA'
                cols.append('')  # Añadir una columna vacía
                data.append(cols)
            else:
                print(f"Fila con datos inconsistentes: {cols}")

        # Convertir los datos a un DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Ordenar por "No. ART" si existe
        if "No. ART" in df.columns:
            df = df.sort_values(by="No. ART")

        # Guardar el archivo ordenado en Excel
        archivo_salida = archivo.replace(".html", "_ordenado.xlsx")
        df.to_excel(archivo_salida, index=False)

        messagebox.showinfo("Éxito", f"Datos guardados como:\n{archivo_salida}")

        # Mostrar la tabla con filtros
        mostrar_tabla(df)

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema: {e}")

def aplicar_filtro():
    """Filtra los datos según los valores ingresados en las cajas de búsqueda."""
    global df_original
    df_filtrado = df_original.copy()

    for col, entry in filtros.items():
        filtro_valor = entry.get().strip().lower()
        if filtro_valor:
            df_filtrado = df_filtrado[df_filtrado[col].astype(str).str.lower().str.contains(filtro_valor, na=False)]

    actualizar_tabla(df_filtrado)

def guardar_excel():
    """Guarda los datos filtrados en un archivo Excel."""
    global df_original
    df_filtrado = df_original.copy()

    for col, entry in filtros.items():
        filtro_valor = entry.get().strip().lower()
        if filtro_valor:
            df_filtrado = df_filtrado[df_filtrado[col].astype(str).str.lower().str.contains(filtro_valor, na=False)]

    archivo_excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos Excel", "*.xlsx")])

    if archivo_excel:
        try:
            with pd.ExcelWriter(archivo_excel, engine="xlsxwriter") as writer:
                df_filtrado.to_excel(writer, sheet_name="Datos Filtrados", index=False)

                # Ajustar el ancho de las columnas automáticamente
                workbook = writer.book
                worksheet = writer.sheets["Datos Filtrados"]
                for i, col in enumerate(df_filtrado.columns):
                    max_len = max(df_filtrado[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)

            messagebox.showinfo("Éxito", f"Datos guardados en:\n{archivo_excel}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

def mostrar_tabla(df):
    """Crea una ventana para mostrar los datos en una tabla con filtros y botón de exportar a Excel."""
    global df_original, tree, filtros

    df_original = df  # Guardar los datos originales
    ventana = tk.Toplevel()
    ventana.title("Datos con Filtros")
    ventana.geometry("900x600")

    # Crear el marco para los filtros
    filtro_frame = tk.Frame(ventana)
    filtro_frame.pack(fill="x", padx=5, pady=5)

    filtros = {}  # Diccionario para almacenar las entradas de filtro

    for idx, col in enumerate(df.columns):
        lbl = tk.Label(filtro_frame, text=col, font=("Arial", 10, "bold"))
        lbl.grid(row=0, column=idx, padx=5, pady=5)

        entry = tk.Entry(filtro_frame)
        entry.grid(row=1, column=idx, padx=5, pady=5)
        filtros[col] = entry

    # Botón de filtro
    btn_filtrar = tk.Button(filtro_frame, text="Aplicar Filtro", command=aplicar_filtro)
    btn_filtrar.grid(row=1, column=len(df.columns), padx=10, pady=5)

    # Frame para la tabla
    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(fill="both", expand=True)

    # Crear la tabla
    tree = ttk.Treeview(frame_tabla, columns=list(df.columns), show="headings")
    
    # Configurar encabezados
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")  # Ajustar ancho

    # Agregar datos a la tabla
    actualizar_tabla(df)

    tree.pack(fill="both", expand=True)

    # Agregar barra de desplazamiento
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Botón para exportar a Excel
    btn_excel = tk.Button(ventana, text="Guardar en Excel", command=guardar_excel, font=("Arial", 12), bg="#4CAF50", fg="white")
    btn_excel.pack(pady=10)

def actualizar_tabla(df):
    """Actualiza la tabla con los datos filtrados."""
    tree.delete(*tree.get_children())  # Limpiar la tabla
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

# Crear la ventana principal
root = tk.Tk()
root.title("Cargar HTML")
root.geometry("300x150")

# Botón para cargar archivo
btn_cargar = tk.Button(root, text="Cargar Archivo HTML", command=cargar_archivo, font=("Arial", 12), padx=10, pady=5)
btn_cargar.pack(pady=20)

root.mainloop()
