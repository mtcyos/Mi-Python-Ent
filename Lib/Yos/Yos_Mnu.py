#!/usr/bin/env python3
# -*- coding: utf-8 -*
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

def Mnu(Fnc_Mnu= YosCfg["Apl_Mnu"]):
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
        print(Fore.BLUE + "═" * ancho_total)

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

        # 5. Captura de datos con NORMALIZACIÓN
        # .strip() elimina espacios accidentales y .zfill(2) asegura el formato "06"
#        MnuOpc = input(Fore.YELLOW + " 💻 Seleccione Opción: " + Fore.WHITE).strip().zfill(2)
        Entrada = input(Fore.YELLOW + " 💻 Seleccione Opción: " + Fore.WHITE).strip()
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

def MnuRec(Fnc_Mnu):
    # Recupero el menu de YosCfg.Mnu
    if not Fnc_Mnu:
        Fnc_Mnu = "Main"

    from Yos.Idd_BdtSvr import Cnx, SelTot, Cie,Sel
    Mem_Cnx_Mnu_Rec = Cnx("YosCfg")
    Mem_Cur_Mnu_Rec = Mem_Cnx_Mnu_Rec.cursor()

    Mem_Sql = "SELECT * FROM Mnu WHERE cMnu='"+Fnc_Mnu+"' and (cEtn='"+YosCfg["Etn"]+"' OR cEtn='' OR cEtn IS NULL) ORDER BY cNum"
    Mem_Dat = SelTot(Mem_Cur_Mnu_Rec, Mem_Sql, pParams=())

    if not Mem_Dat:
        print(f"ERROR: NO EXISTE EL MENU {Fnc_Mnu} DE LA APLICACION {YosCfg["Apl_Apl"]} EN YosCfg")
        if Fnc_Mnu == "Main":
            print("CREANDO MENU Main")
            Mem_Cnx_Mnu_Cre = Cnx("YosCfg", "rw")
            Mem_Cur_Mnu_Cre = Mem_Cnx_Mnu_Rec.cursor()

            # 1. Intentamos verificar si la tabla existe en el catálogo de SQL [cite: 2026-01-29]
            Mem_Sql_Cre = "SELECT name FROM sqlite_master WHERE type='table' AND name='Mnu'"

            Mem_Dat = Sel(Mem_Cur_Mnu_Cre, Mem_Sql_Cre)
            if not Mem_Dat:
                Mem_Sql_Cre = """
                    CREATE TABLE IF NOT EXISTS "Mnu" (
                        "cApl"          TEXT(30),
                        "cMnu"          TEXT(25),
                        "cNum"          TEXT(3),
                        "cEtn"          TEXT(10),
                        "cTxt"          TEXT(50),
                        "cFnc"          TEXT(200),
                        "cModRegNik"    TEXT(20),
                        "cModRegTim"    TEXT(20)
                        );
                    """
                Mem_Dat = Sel(Mem_Cur_Mnu_Cre, Mem_Sql_Cre)
            # Añado Registros Basicos
            from datetime import datetime
            cTimModReg = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            Mem_Sql_Cre = f"""
                INSERT INTO 'Mnu' VALUES
                    ('YosCtr','Main','00',NULL,'ENTORNO'        ,''                                 ,'YosCfg','{cTimModReg}'),
                    ('YosCtr','Main','01',NULL,'RECARGAR MENU'  ,'YosMnuCag'                        ,'YosCfg','{cTimModReg}'),
                    ('YosCtr','Main','02',NULL,'MODIFICAR MENU' ,'YosMnuCag'                        ,'YosCfg','{cTimModReg}'),
                    ('YosCtr','Main','05',NULL,'CONTACTENOS'    ,'Yos.EmlEnv("mtcyos@yahoo.es")'    ,'YosCfg','{cTimModReg}'),
                    ('YosCtr','Main','06',NULL,'LICENCIA'       ,'Yos.Acd_Res()'                    ,'YosCfg','{cTimModReg}'),
                    ('YosCtr','Main','07',NULL,'ENTORNO'        ,'Yos.AcdEtn()'                     ,'YosCfg','{cTimModReg}'),
                    ('YosCtr','Main','08',NULL,'ACERCA DE ...'  ,'Yos.Acd()'                        ,'YosCfg','{cTimModReg}'),
                    ('YosCtr','Main','09',NULL,'SALIR'          ,'Yos.Apl_Fin()'                    ,'YosCfg','{cTimModReg}');
            """
            Mem_Dat = Sel(Mem_Cur_Mnu_Cre, Mem_Sql_Cre)

            Cie(Mem_Cnx_Mnu_Cre)

            # Vuelvo a cargar el menu
            Mem_Sql = "SELECT * FROM Mnu WHERE cApl='" +YosCfg["Apl_Apl"] +"' and cMnu='"+Fnc_Mnu+"' and (cEtn='"+YosCfg["Etn"]+"' OR cEtn='' OR cEtn IS NULL) ORDER BY cNum"
            Mem_Dat = SelTot(Mem_Cur_Mnu_Rec, Mem_Sql, pParams=())

    Mem_Dic_Tmp = {}

    for Mem_Uni in Mem_Dat:
        # Llenamos el temporal
        Mem_Dic_Tmp[Mem_Uni["cNum"]] = {
            "Txt": Mem_Uni["cTxt"],
            "Fnc": Mem_Uni["cFnc"] if Mem_Uni["cFnc"] is not None else ""
        }
#        print(Mem_Uni["cApl"]+" - "+Mem_Uni["cMnu"]+" - "+Mem_Uni["cNum"]+" - "+str(Mem_Uni["cEtn"])+" - "+Mem_Uni["cTxt"]+" - "+str(Mem_Uni["cFnc"]))

    Cie(Mem_Cnx_Mnu_Rec)

    if Fnc_Mnu == "Main":
        YosCfg["Apl_Mnu"] = Mem_Dic_Tmp
        YosCfg.sync()
    else:
        return Mem_Dic_Tmp
