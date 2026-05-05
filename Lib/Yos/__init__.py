#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Bin > Sistema Yos - Inicialización y Verificación de Módulos
# Tim - 20260409 14:15:00

import sys
import importlib
import subprocess

# 1. Definición de Módulos con Mapeo (Nombre PIP : Nombre IMPORT)
# Esto resuelve el problema de pywebview vs webview
Mdl_Map = {
    "pip": "pip",                       # Gestor de paquetes (Instalador oficial)
    "psutil": "psutil",                 # Control de Hardware (Lectura de Discos, CPU y RAM)
    "pytimedinput": "pytimedinput",     # Entradas de teclado con tiempo límite (Timeouts)
    "pyfiglet": "pyfiglet",             # Arte ASCII (Rótulos grandes para Banners)
    "colorama": "colorama",             # Soporte de colores ANSI en la consola de Windows
    "django": "django",                 # Framework para Modelos de Datos y entorno Web
    "pypyodbc": "pypyodbc",             # Conector universal de Base de Datos (ODBC)
    "dbfread": "dbfread",               # Conector para LECTURA de .dbf
    "openpyxl": "openpyxl",             # LECTURA y ESCRITURA de archivos Excel (.xlsx)
    "fpdf": "fpdf",                     # Generador de reportes y documentos en PDF
    "pyperclip": "pyperclip",           # Portapapeles (Copiar y Pegar texto del sistema)

    "prompt_toolkit": "prompt_toolkit", # TUI: Interfaz de Terminal Avanzada (Menús con teclado y F2)
    "FreeSimpleGUI": "FreeSimpleGUI",   # GUI: Ventanas rápidas (Versión Free)

    "nicegui": "nicegui",               # Interfaz Web moderna (Menús azules, tablas y multiusuario)
    "asyncio": "asyncio",               # Manejo de tareas asíncronas para el servidor web
    "pywebview": "webview",             # Ventana nativa para NiceGUI (MODO ESCRITORIO)
}

# pip uninstall pywebview

# 2. Verificación de existencia de los módulos
for pkg_name, import_name in Mdl_Map.items():
    try:
        importlib.import_module(import_name)
    except ImportError:
        print(f"\nEl módulo '{pkg_name}' no está instalado o no se encuentra.")
        if input(f"Instalar {pkg_name} (S=Instalar) : ").upper() == "S":
            print(f"Instalando {pkg_name}...")
            try:
                # Se usa --break-system-packages para entornos Linux modernos
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name, "--break-system-packages"])
                print(f"Módulo {pkg_name} instalado correctamente.")
            except Exception as e:
                print(f"Error al instalar {pkg_name}: {e}")
    except Exception as e:
        print(f"Ocurrió otro error al importar {import_name}: {e}")

# Importaciones de la YosLib
from .YosLib import * # Aqui se guardan todas las Def Yos_xxxx que no tienen salida a pantalla
from .YosIdd import * # Aqui se guardan todas las Def Idd_xxxx que no tienen salida a pantalla
from .YosApl import * # Aqui se guardan todas las Def Apl_xxxx que no tienen salida a pantalla

from .Yos_Ges_Frm import *  # Gestion de todas las Def Yos_xxx_Frm
from .Yos_Ges_Txt import *  # Gestion de todas las Def Yos_xxx_Txt

from .Idd_Ges_Frm import *  # Gestion de todas las Def Idd_xxx_Frm
from .Idd_Ges_Txt import *  # Gestion de todas las Def Idd_xxx_Txt

from .Apl_Ges_Frm import *  # Gestion de todas las Def Apl_xxx_Frm
from .Apl_Ges_Txt import *  # Gestion de todas las Def Apl_xxx_Txt



from .Yos_Cfg import *
# from .Yos_Acd import *
from .Yos_Ini import *
from .Yos_Ent import *


from .Yos_Mnu import *
from .Yos_Mnu_NiceGUI import *


from .Idd_BdtSvr import *
from .Idd_TabMod import *
from .Idd_TabMod_Gui import *
from .Idd_TabMst import *


