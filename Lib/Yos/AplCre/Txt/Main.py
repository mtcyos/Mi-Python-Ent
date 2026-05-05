#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
   YosMnu_Txt.py

   Yos Menú en entrono Txto

   Copyright (c) 2026 Miguel Tortosa

   Licenciado bajo la Licencia MIT.

   Consulte el archivo LICENCIA en la raíz del proyecto para más información.
"""

import platform
import sys
import os
import subprocess

#import importlib
#import importlib.util

# Añado Directorio de YosLib
match platform.system():
    case "Windows":
        sys.path.append(os.path.abspath("..")+"\\Lib\\")
    case "Linux":
        sys.path.append(os.path.abspath("..")+os.path.abspath("/Lib/"))
#   case "Darwin": # macOS
#       sys.path.append(os.path.abspath("..")+os.path.abspath("/Lib/"))
    case _:
        print("YosCtr.36")
        print(f"Sistema Operativo {platform.system()} no implementado.")
        sys.exit(0)

# Nombre de la Aplicacion
import builtins
builtins.Mem_Ini_AplCod = "YosMnu"                # ES el nombre REAL de la Aplicacion, NO LO CAMBIE, use cNom="Apl_Apl" en YosCfg.Dat
builtins.Mem_Ini_AplNom = "MENU DE APLICACIONES"  # ES el nombre REAL de la Aplicacion, NO LO CAMBIE, use cNom="Apl_Nom" en YosCfg.Dat
builtins.Mem_Ini_AplEtn = "Txt"                   # ES el entorno REAL de la Aplicacion, NO LO CAMBIE, Txt = prompt_toolkit

import Yos

from Yos import FrmCls, FrmCab

from Yos import Idd_TabMst

YosCfg["Dbg"]="" # MODO DEPURACION S="Completo" X=Para NiceGUI en local
Yos.AplIni()    # Inicio el Entorno

#Idd_TabMst("YosCfg", "Mnu")

def main():
    # DEFINO EL MENU A USAR
    while True:
#        MnuFnc = Yos.Mnu(YosCfg["Apl_Mnu"])
        MnuFnc = Yos.Mnu_Gui(YosCfg["Apl_Mnu"])
#        input(MnuFnc)
        if MnuFnc == "YosMnuCag":
            Yos.MnuRec("Main")
            continue

        if MnuFnc[:7]=="YosCmd:":   # YosCmd: se pone ANTES del comando que queramos ejecutar
            MnuFnc=MnuFnc.replace("YosCmd:", "")

            if YosCfg["Etn"] == "Windows":
                subprocess.Popen(['cmd', '/c', 'start', '', MnuFnc], shell=True)
            elif YosCfg["Etn"] == "Darwin": # Mac
                subprocess.Popen(['open', MnuFnc])
            else: # Linux y otros
                subprocess.Popen(['xdg-open', MnuFnc])

            continue

        try:
            exec(MnuFnc)
        except Exception as e:
            input(f"Error al ejecutar: {e}")
# FIN - Proceso del menu

if __name__ == '__main__':
    main()

