#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Yos
from Yos.Yos_Frm import FrmCls, FrmWit
from Yos.Yos_Ini import AplIni
from Yos.Yos_Acd import Acd
from Yos.Yos_Cfg import Apl_Fin

import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Inicializamos el motor visual de Yos
console = Console()

def Mnu(Fnc_Mnu=None):
    """
    Menú dinámico con persistencia usando Rich para estética SpansTools.
    """
    if not Fnc_Mnu:
        Fnc_Mnu = YosCfg["Apl_Mnu"]

    Salir_Num = ""
    
    while True:
        # 1. Inicialización y Limpieza
        AplIni() 

        # 2. Agrupar por decenas (Tu lógica original de Clipper/Fox)
        grupos = {}
        items = sorted(Fnc_Mnu.items())

        for clave, valor in items:
            ent = valor.get("Ent", "")
            if ent == "" or ent in YosCfg["Ent"]:
                decena = clave[0]
                if decena not in grupos:
                    grupos[decena] = []
                grupos[decena].append({"id": clave, "txt": valor["Txt"], "fnc": valor["Fnc"]})

        claves_grupos = sorted(grupos.keys())
        columnas = [grupos[k] for k in claves_grupos]
        num_cols = len(columnas)
        
        if num_cols == 0: return "" 

        # 3. Construcción del Menú con Rich (Win/Linux/Mac compatible)
        # Creamos la tabla que organiza las columnas automáticamente
        tabla_mnu = Table(show_header=True, 
                          header_style="bold magenta", 
                          box=None, 
                          expand=True, 
                          padding=(0, 2))

        # Añadimos los encabezados de columna
        for col in columnas:
            titulo = col[0]["txt"].upper()
            tabla_mnu.add_column(titulo)

        # Calculamos la profundidad de las filas (saltando el título)
        max_filas = max(len(col) for col in columnas)

        for i in range(1, max_filas):
            fila_completa = []
            for col in columnas:
                if i < len(col):
                    item = col[i]
                    # Lógica para la tecla rápida 'S'
                    id_ver = "S" if item['txt'] == "SALIR" else item['id']
                    if item['txt'] == "SALIR":
                        Salir_Num = item['id']
                    
                    # Formateamos con colores Rich
                    fila_completa.append(f"[bold white]{id_ver}[/] - [cyan]{item['txt']}[/]")
                else:
                    fila_completa.append("")
            tabla_mnu.add_row(*fila_completa)

        # 4. Impresión de Pantalla estilo SpansTools
        # El Panel crea el marco de doble línea (box.DOUBLE) automáticamente
        console.print(Panel(tabla_mnu, 
                            title=f"[bold yellow] {YosCfg.get('Apl_Nom', 'Yos_Menu')} [/]", 
                            subtitle=f"[bold yellow] {YosCfg.get('Apl_Cpy', 'Yos_Menu')} [/]",# "[italic blue] mtcyos 2026 [/]",
                            border_style="bright_blue",
                            box=box.DOUBLE))

        # 5. Captura de datos con NORMALIZACIÓN
        try:
            entrada = console.input("[bold yellow] 💻 Seleccione Opción: [/]").strip()
        except EOFError:
            break

        if entrada.upper() == 'S':
            MnuOpc = Salir_Num
        else:
            MnuOpc = entrada.zfill(2)

        # 6. Lógica de ejecución
        if MnuOpc in Fnc_Mnu:
            ent_opc = Fnc_Mnu[MnuOpc].get("Ent", "")
            if ent_opc == "" or ent_opc in YosCfg["Ent"]:
                MnuFnc = Fnc_Mnu[MnuOpc]["Fnc"]
                
                if MnuFnc == "":
                    continue
                else:
                    # Retornamos la función para que el cerebro la ejecute
                    return MnuFnc

def MnuRec(Fnc_Mnu):
    """
    Recupero el menu de la base de datos SQLite YosCfg
    """
    if not Fnc_Mnu:
        Fnc_Mnu = "Main"

    from Yos.Idd_BdtSvr import Cnx, SelTot, Cie, Sel
    Mem_Cnx_Mnu_Rec = Cnx("YosCfg")
    Mem_Cur_Mnu_Rec = Mem_Cnx_Mnu_Rec.cursor()

    Mem_Sql = "SELECT * FROM Mnu WHERE cMnu='"+Fnc_Mnu+"' and (cEtn='"+YosCfg["Etn"]+"' OR cEtn='' OR cEtn IS NULL) ORDER BY cNum"
    Mem_Dat = SelTot(Mem_Cur_Mnu_Rec, Mem_Sql, pParams=())

    if not Mem_Dat:
        # --- BLOQUE DE CREACIÓN DE MENÚ SI NO EXISTE ---
        if Fnc_Mnu == "Main":
            Mem_Cnx_Mnu_Cre = Cnx("YosCfg", "rw")
            Mem_Cur_Mnu_Cre = Mem_Cnx_Mnu_Cre.cursor()

            # Verificamos tabla
            Mem_Sql_Cre = "SELECT name FROM sqlite_master WHERE type='table' AND name='Mnu'"
            if not Sel(Mem_Cur_Mnu_Cre, Mem_Sql_Cre):
                Mem_Cur_Mnu_Cre.execute("""
                    CREATE TABLE IF NOT EXISTS "Mnu" (
                        "cApl" TEXT(30), "cMnu" TEXT(25), "cNum" TEXT(3),
                        "cEtn" TEXT(10), "cTxt" TEXT(50), "cFnc" TEXT(200),
                        "cModRegNik" TEXT(20), "cModRegTim" TEXT(20)
                    );
                """)
            
            # Registros básicos (Honor a quien honor merece)
            from datetime import datetime
            cTimModReg = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            Mem_Sql_Ins = f"""
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
            Mem_Cur_Mnu_Cre.execute(Mem_Sql_Ins)
            Mem_Cnx_Mnu_Cre.commit()
            Cie(Mem_Cnx_Mnu_Cre)

            # Recargamos tras crear
            Mem_Dat = SelTot(Mem_Cur_Mnu_Rec, Mem_Sql, pParams=())

    # Generamos el diccionario para YosCfg
    Mem_Dic_Tmp = {}
    for Mem_Uni in Mem_Dat:
        Mem_Dic_Tmp[Mem_Uni["cNum"]] = {
            "Txt": Mem_Uni["cTxt"],
            "Fnc": Mem_Uni["cFnc"] if Mem_Uni["cFnc"] is not None else ""
        }

    Cie(Mem_Cnx_Mnu_Rec)

    if Fnc_Mnu == "Main":
        YosCfg["Apl_Mnu"] = Mem_Dic_Tmp
        YosCfg.sync()
    else:
        return Mem_Dic_Tmp