#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   Yos_Mnu.py
   Genero el Menu de la Aplicacion

   Copyright (c) 2026 Miguel Tortosa

   Licenciado bajo la Licencia MIT.

   Consulte el archivo LICENCIA en la raíz del proyecto para más información.
"""

import Yos
from Yos.Yos_Frm import FrmCls, FrmWit
from Yos.Yos_Ini import AplIni
from Yos.Yos_Acd import Acd
from Yos.Yos_Cfg import Apl_Fin

import os

from colorama import Fore, Style

def MnuTxt(Fnc_Mnu= YosCfg["Apl_Mnu"]):
    """
    Menú dinámico con persistencia.
    Se mantiene ejecutándose hasta que se elige una función externa.
    """

    if not Fnc_Mnu:
        Fnc_Mnu = YosCfg["Apl_Mnu"]

    Salir_Num=""
    while True:
        # Limpiamos pantalla en cada ciclo para que el menú siempre esté arriba
        # FrmCls() debería tener: os.system('clear' if os.name != 'nt' else 'cls')
 #       FrmCls()
        AplIni()
        print(f"{Style.RESET_ALL+Fore.YELLOW+YosCfg['Apl_Nom']:^{YosCfg["Apl_Etn_Lon"]}}")

        ancho_total = YosCfg["Apl_Etn_Lon"]

        # 1. Agrupar por decenas (0, 1, 8, 9)
        grupos = {}
        items = sorted(Fnc_Mnu.items())

        for clave, valor in items:
            ent = valor.get("Ent", "")
            if ent == "" or ent in YosCfg["Ent"]:
                decena = clave[0]
                if decena not in grupos:
                    grupos[decena] = []
                grupos[decena].append({"id": clave, "txt": valor["Txt"], "fnc": valor["Fnc"]})

        # 2. Preparar columnas
        claves_grupos = sorted(grupos.keys())
        columnas = [grupos[k] for k in claves_grupos]
        num_cols = len(columnas)
        if num_cols == 0: return "" # Evitar división por cero

        ancho_col = ancho_total // num_cols

        # 3. Imprimir Títulos de cada columna
        linea_titulos = ""
        for i, col in enumerate(columnas):
            titulo = col[0]["txt"].upper()
            bloque_titulo = f"{titulo[:ancho_col-3]:^{ancho_col-1}}"

            if i < len(columnas) - 1:
                linea_titulos += Fore.MAGENTA + Style.BRIGHT + bloque_titulo + Fore.BLUE + "|"
            else:
                linea_titulos += Fore.MAGENTA + Style.BRIGHT + bloque_titulo

        print(linea_titulos)
        print(Style.RESET_ALL+Fore.BLUE + "═" * ancho_total)

        # 4. Imprimir las opciones (fila por fila)
        # Empezamos en 1 porque la fila 0 es el título del grupo
        max_filas = max(len(col) for col in columnas)

        for i in range(1, max_filas):
            fila_completa = ""
            for j, col in enumerate(columnas):
                ancho_disponible = ancho_col - 1

                if i < len(col):
                    item = col[i]
 #                   texto_celda = f" {item['id']} - {item['txt']}"
                    # Si el testo es "SALIR" Salir_Num
                    id_ver = "S".ljust(len(item['id'])) if item['txt'] == "SALIR" else item['id']
                    if item['txt'] == "SALIR":
                        Salir_Num = item['id']

                    texto_celda = f" {id_ver} - {item['txt']}"
                    contenido = f"{texto_celda[:ancho_disponible]:<{ancho_disponible}}"
                else:
                    contenido = " " * ancho_disponible

                if j < num_cols - 1:
                    fila_completa += Fore.WHITE + contenido + Fore.BLUE + "|"
                else:
                    fila_completa += Fore.WHITE + contenido

            print(fila_completa)

        print(Fore.BLUE + "═" * ancho_total)

        print(f"{Style.RESET_ALL+Fore.YELLOW+YosCfg['Apl_Cpy']:^{YosCfg["Apl_Etn_Lon"]}}")
        # 5. Captura de datos con NORMALIZACIÓN
        # .strip() elimina espacios accidentales y .zfill(2) asegura el formato "06"
       #MnuOpc = input(Fore.YELLOW + " 💻 Seleccione Opción: " + Fore.WHITE).strip().zfill(2)
        Entrada = input(Style.BRIGHT +Fore.YELLOW + " 💻 Seleccione Opción: " + Fore.WHITE).strip()
        # Si es 'S' o 's', la convertimos en '099' para que el sistema la reconozca
        if Entrada.upper() == 'S':
            MnuOpc = Salir_Num
        else:
            MnuOpc = Entrada.zfill(2)

        # 6. Lógica de validación y ejecución
        if MnuOpc in Fnc_Mnu:
            ent_opc = Fnc_Mnu[MnuOpc].get("Ent", "")
            if ent_opc == "" or ent_opc in YosCfg["Ent"]:
                MnuFnc = Fnc_Mnu[MnuOpc]["Fnc"]
            else:
                continue

            # --- SECCIÓN DE ACCIONES INTERNAS ---
            if MnuFnc == "":
                # Es un encabezado o una opción vacía
                #print(Fore.CYAN + " ℹ️  Opción informativa (encabezado).")
                #os.system('sleep 1' if os.name != 'nt' else 'timeout 1 > NUL')
                continue

            # --- SECCIÓN DE RETORNO EXTERNO ---
            else:
                # Si llegamos aquí, es una función real (ej: "Yos.Acd()")
                return MnuFnc

        #else:
            #print(Fore.RED + f" ❌ '{MnuOpc}' no es una opción válida." + Fore.WHITE)
            ## Pequeña pausa para que el usuario lea el error antes de limpiar pantalla
            #os.system('sleep 1.5' if os.name != 'nt' else 'timeout 2 > NUL')
