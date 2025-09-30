import os
import platform
import time
import random
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Colores estilo terminal azul
BG_COLOR = "#0a2342"
FG_COLOR = "#00ffea"
FONT = ("Consolas", 11)

def obtener_info_pc():
    info = []
    info.append(f"Sistema: {platform.system()}")
    info.append(f"Nombre de la PC: {platform.node()}")
    info.append(f"Versión: {platform.version()}")
    info.append(f"Release: {platform.release()}")
    info.append(f"Procesador: {platform.processor()}")
    info.append(f"Arquitectura: {platform.machine()}")
    try:
        import psutil
        ram = round(psutil.virtual_memory().total / (1024**3), 2)
        info.append(f"RAM instalada: {ram} GB")
    except:
        info.append("RAM instalada: (psutil no instalado)")
    return "\n".join(info)

def simular_analisis(text_widget, diagnostico):
    text_widget.delete(1.0, tk.END)
    procesos = [
        "Analizando integridad del kernel...",
        "Verificando módulos de compatibilidad...",
        "Escaneando drivers de hardware...",
        "Comprobando TPM 2.0...",
        "Analizando Secure Boot...",
        "Revisando espacio en disco...",
        "Verificando DirectX...",
        "Escaneando CPU y RAM...",
        "Comprobando actualizaciones de BIOS...",
        "Analizando compatibilidad de GPU...",
        "Revisando lista de procesos activos...",
        "Verificando configuración de red...",
        "Analizando registros del sistema...",
        "Comprobando cifrado BitLocker...",
        "Escaneando dispositivos conectados...",
        "Verificando estado de servicios críticos...",
        "Analizando logs de eventos recientes...",
        "Comprobando integridad de archivos del sistema...",
        "Verificando compatibilidad de software instalado...",
        "Analizando tabla de particiones...",
    ]
    for i in range(30):
        linea = random.choice(procesos)
        codigo = f"{linea} [{random.randint(1000,9999)}] ... OK\n"
        text_widget.insert(tk.END, codigo)
        text_widget.see(tk.END)
        text_widget.update()
        time.sleep(random.uniform(0.05, 0.15))
        # Simula líneas de "código raro"
        if random.random() > 0.7:
            text_widget.insert(tk.END, f"0x{random.randint(100000,999999):x} -> {os.urandom(4).hex()} ...\n")
            text_widget.see(tk.END)
            text_widget.update()
            time.sleep(0.05)
    text_widget.insert(tk.END, "\n--- DIAGNÓSTICO FINAL ---\n", "bold")
    text_widget.insert(tk.END, diagnostico + "\n\n", "bold")
    text_widget.insert(tk.END, obtener_info_pc())
    text_widget.see(tk.END)
    text_widget.update()

def analizar_pc():
    diagnostico = (
        "La PC NO es apta para actualizar a Windows 11.\n"
        "Todos los controladores y el sistema se encuentran lo más actualizado posible."
    )
    simular_analisis(terminal, diagnostico)

def info_sistema():
    diagnostico = (
        "La PC ES apta para actualizar a Windows 11.\n"
        "Todos los controladores y el sistema se encuentran lo más actualizado posible."
    )
    simular_analisis(terminal, diagnostico)

def salir():
    root.destroy()

# Interfaz
root = tk.Tk()
root.title("Diagnóstico de PC")
root.configure(bg=BG_COLOR)
root.geometry("700x500")
root.resizable(False, False)

# Terminal simulada
terminal = scrolledtext.ScrolledText(root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)
terminal.place(x=20, y=80, width=660, height=390)
terminal.tag_configure("bold", font=(FONT[0], FONT[1], "bold"))

# Menú de opciones
frame_menu = tk.Frame(root, bg=BG_COLOR)
frame_menu.place(x=20, y=20, width=660, height=50)

btn_analizar = tk.Button(frame_menu, text="Analizar PC", font=FONT, bg="#1a4e8a", fg=FG_COLOR, command=analizar_pc)
btn_analizar.pack(side=tk.LEFT, padx=10, pady=10)

btn_info = tk.Button(frame_menu, text="Información del sistema", font=FONT, bg="#1a4e8a", fg=FG_COLOR, command=info_sistema)
btn_info.pack(side=tk.LEFT, padx=10, pady=10)

btn_salir = tk.Button(frame_menu, text="Salir", font=FONT, bg="#1a4e8a", fg=FG_COLOR, command=salir)
btn_salir.pack(side=tk.RIGHT, padx=10, pady=10)

# Mensaje inicial
terminal.insert(tk.END, "Bienvenido al Diagnóstico de PC\nSeleccione una opción del menú para comenzar...\n\n")

root.mainloop()