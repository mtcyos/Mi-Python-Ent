#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import os
import re
import sys
import ctypes
import locale
import msvcrt
import sqlite3

from Yos import Yos_FrmCls, FrmWit, FrmLin, AplIni, Yos_TimeStamp

try:
    locale.setlocale(locale.LC_TIME, "")
except:
    pass

# =============================================================================
# FUNCIONES DE APOYO (SIN CAMBIOS)
# =============================================================================
def maximizar_consola():
    if os.name == 'nt':
        try:
            kernel32 = ctypes.WinDLL('kernel32')
            user32 = ctypes.WinDLL('user32')
            hWnd = kernel32.GetConsoleWindow()
            if hWnd:
                user32.ShowWindow(hWnd, 3)
                hOut = kernel32.GetStdHandle(-11)
                kernel32.SetConsoleDisplayMode(hOut, 1, ctypes.byref(ctypes.c_long()))
        except: pass

def obtener_anchos_reales():
    try:
        Mem_Ancho = os.get_terminal_size().columns - (len(Mem_Tab_Brw) * 3) - 12
    except:
        Mem_Ancho = 118
    anchos_finales = [0] * len(Mem_Tab_Brw)
    espacio_restante = Mem_Ancho
    indices_con_porcentaje = []
    for i, col in enumerate(Mem_Tab_Brw):
        ancho_config = str(col[1])
        if "%" not in ancho_config:
            valor_fijo = int(ancho_config)
            anchos_finales[i] = valor_fijo
            espacio_restante -= valor_fijo
        else:
            indices_con_porcentaje.append(i)
    if indices_con_porcentaje:
        total_slots = len(indices_con_porcentaje)
        for i, idx in enumerate(indices_con_porcentaje):
            if i == total_slots - 1:
                anchos_finales[idx] = max(0, espacio_restante)
            else:
                porcentaje_valor = int(str(Mem_Tab_Brw[idx][1]).replace("%", ""))
                ancho_calculado = int((porcentaje_valor / 100) * espacio_restante)
                anchos_finales[idx] = ancho_calculado
                espacio_restante -= ancho_calculado
    return anchos_finales

# =============================================================================
# BUSCAR (REEMPLAZADO CON FreeSimpleGUI)
# =============================================================================
def busqueda_incremental_dinamica(conn, db_col_names, anchos):
    global offset, fila_resaltada, nLin, order_by_col, Mem_Ftr
    bus = ""
    pad = " " * MARGEN
    where_ftr = f"WHERE {order_by_col} LIKE ?" if Mem_Ftr else ""

    try:
        import FreeSimpleGUI as sg
    except ImportError:
        print("FreeSimpleGUI no está instalado. Instalando...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "FreeSimpleGUI"])
        import FreeSimpleGUI as sg

    layout = [
        [sg.Text(f"Buscar en {order_by_col}:", font=('CourierPS', 10, 'bold'))],
        [sg.Input(key='busqueda', size=(30, 1), enable_events=True, focus=True, font=('CourierPS', 10))],
        [sg.Text("[Letras]: Buscar | [Enter]: Aceptar | [Esc]: Cancelar", text_color='green', font=('CourierPS', 9))],
        [sg.HorizontalSeparator()],
        [sg.Table(
            values=[],
            headings=[c[0] for c in Mem_Tab_Brw],
            auto_size_columns=False,
            col_widths=[max(4, a//8) for a in anchos],
            display_row_numbers=False,
            justification='left',
            num_rows=nLin,
            key='tabla_busqueda',
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            text_color='black',
            background_color='white',
            alternating_row_color='#f0f0f0',
            font=('CourierPS', 9)
        )],
        [sg.Button("Aceptar", key='aceptar', bind_return_key=True), sg.Button("Cancelar", key='cancelar')]
    ]

    window = sg.Window(
        f"Buscar - {Mem_Tab_Nom}",
        layout,
        finalize=True,
        return_keyboard_events=True,
        modal=True,
        font=('CourierPS', 10)
    )

    window['busqueda'].set_focus()

    def actualizar_tabla(bus_texto):
        cur = conn.cursor()
        op_and = "AND" if where_ftr else "WHERE"
        params_bus = (f"%{Mem_Ftr}%", f"{bus_texto}%") if Mem_Ftr else (f"{bus_texto}%",)

        cur.execute(f"SELECT COUNT(*) FROM {Mem_Tab_Nom} {where_ftr} {op_and} {order_by_col} < ? COLLATE NOCASE", params_bus)
        posicion_real = cur.fetchone()[0]
        mitad = nLin // 2
        offset_temp = max(0, posicion_real - mitad)

        cur.execute(f"SELECT {order_by_col} FROM {Mem_Tab_Nom} {where_ftr} {op_and} {order_by_col} >= ? COLLATE NOCASE ORDER BY {order_by_col} COLLATE NOCASE LIMIT 1", params_bus)
        res = cur.fetchone()
        fila_res = res[0] if res else None

        params_sel = (f"%{Mem_Ftr}%",) if Mem_Ftr else ()
        cur.execute(f"SELECT rowid, *, ({order_by_col}) as ord_val FROM {Mem_Tab_Nom} {where_ftr} ORDER BY {order_by_col} COLLATE NOCASE LIMIT {nLin} OFFSET {offset_temp}", params_sel)
        regs = cur.fetchall()

        datos = []
        fila_idx = -1
        for idx, r in enumerate(regs):
            fila = []
            val_comparar = str(r[-1])
            es_esta = (fila_res is not None and val_comparar.upper() == str(fila_res).upper())
            if es_esta:
                fila_idx = idx

            for i in range(len(Mem_Tab_Brw)):
                if i == 0:
                    n_fila = str(idx + 1).zfill(2)
                    fila.append(n_fila)
                else:
                    idx_bd = db_col_names.index(Mem_Tab_Brw[i][2]) + 1 if Mem_Tab_Brw[i][2] else 0
                    valor = str(r[idx_bd] if idx_bd > 0 and r[idx_bd] is not None else "")
                    fila.append(valor[:anchos[i] if i < len(anchos) else 20])

            datos.append(fila)

        window['tabla_busqueda'].update(values=datos)
        if fila_idx >= 0:
            window['tabla_busqueda'].update(select_rows=[fila_idx])

        return regs, fila_res, offset_temp

    registros, fila_resaltada_temp, offset_temp = actualizar_tabla("")
    offset_result = offset

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'cancelar', 'Escape:27'):
            fila_resaltada = None
            break

        if event in ('aceptar', 'Return:36'):
            offset_result = offset_temp
            fila_resaltada = fila_resaltada_temp
            break

        if event == 'busqueda':
            bus = values['busqueda']
            registros, fila_resaltada_temp, offset_temp = actualizar_tabla(bus)

    window.close()
    offset = offset_result

# =============================================================================
# FORMULARIO YOS (REEMPLAZADO CON FreeSimpleGUI)
# =============================================================================
def formulario_yos(db_col_names, registro=None, AccReg="Cre"):
#    import FreeSimpleGUI as sg
    import FreeSimpleGUI as sg

    campos_dinamicos = []
    inputs_dic = {}

    match AccReg:
        case "Cre":
            solo_lectura=False
            eliminar=False
        case "Ver":
            solo_lectura=True
            eliminar=False
        case "Mod":
            solo_lectura=False
            eliminar=False
        case "Eli":
            solo_lectura=True
            eliminar=True
        case _:
            print("Opción inexistente")
            return None

    layout = []

    titulos = {"Cre": "CREAR", "Ver": "VER", "Mod": "MODIFICAR", "Eli": "ELIMINAR"}
    txt_titulo = titulos.get(AccReg, "GESTIÓN")

    color_titulo = 'red' if AccReg == "Eli" else 'green' if AccReg == "Cre" else 'blue'
    layout.append([sg.Text(f" **** {txt_titulo} **** ", size=(40, 1), justification='center',
                          background_color=color_titulo, text_color='white', font=('CourierPS', 12, 'bold'))])
    layout.append([sg.HorizontalSeparator()])

    for i, f in enumerate(Mem_Tab_ClmMod):
        nom_col = f[0]
        etiqueta = f[1]
        Mem_Mod = f[2]
        Mem_Mod_Style = "text-area"
        ancho_sql = Mem_Tab_ClmMod_Def[i][1]
        ancho_Clm = Mem_Tab_ClmMod_Def[i][1]

#        print(f"224 ----------------------------------------")
#        print(f"nom_col {nom_col} 241")
#        print(f"Mem_Mod {Mem_Mod} 241")
#        print(f"solo_lectura {solo_lectura} 241")
        match AccReg:
            case "Cre":
                es_obligatorio = "*" if (len(f) > 3 and f[3] == "N") else " "
            case "Ver":
                es_obligatorio = ""
            case "Mod":
                es_obligatorio = "*" if (len(f) > 3 and f[3] == "N") else " "
                solo_lectura=False
                if Mem_Mod == "Cre":
                    solo_lectura=True
                    Mem_Mod_Style = "readonly"

            case "Eli":
                es_obligatorio = ""
#        print(f"nom_col {nom_col} 241")
#        print(f"Mem_Mod {Mem_Mod} 241")
#        print(f"solo_lectura {solo_lectura} 241")

        texto_label = f" {es_obligatorio}{etiqueta}"

        if ancho_Clm > YosCfg["Apl_Etn_Lon"]:
            ancho_Clm = YosCfg["Apl_Etn_Lon"] - 21

        if registro:
            if isinstance(registro, sqlite3.Row):
                valor_campo = str(registro[nom_col] if nom_col in registro.keys() else "")
            else:
                valor_campo = str(registro[i+1] if registro and i+1 < len(registro) else "")
        else:
            valor_campo = ""


        input_elem = sg.Input(
            default_text=valor_campo,
            size=(min(ancho_Clm, 60), 1),
            readonly=solo_lectura,
            disabled=solo_lectura,
            key=f"input_{nom_col}",
            font=('CourierPS', 10),
#            background_color='#dddddd' if solo_lectura else 'white'
            background_color='white',
            disabled_readonly_background_color='#bbbbbb',
            text_color='black'
        )
#        print(f"input_{nom_col} 268")
#        print(f"solo_lectura {solo_lectura}")

        inputs_dic[nom_col] = input_elem

        label_elem = sg.Text(texto_label.ljust(15), size=(16, 1), font=('CourierPS', 10))

        layout.append([label_elem, input_elem])

    layout.append([sg.HorizontalSeparator()])

    campos_auditoria = [
        ('cModRegNik', 'USUARIO', 20),
        ('cModRegTim', 'MODIFICADO', 20)
    ]

    for nom_col, etiqueta, ancho_fijo in campos_auditoria:
        if registro and isinstance(registro, sqlite3.Row):
            valor_auditoria = str(registro[nom_col] if nom_col in registro.keys() else "")
        else:
            valor_auditoria = ""

        input_auditoria = sg.Input(
            default_text=valor_auditoria,
            size=(ancho_fijo, 1),
            readonly=True,
            disabled=True,
            key=f"audit_{nom_col}",
            font=('CourierPS', 10),
            disabled_readonly_background_color='#bbbbbb'
        )

        inputs_dic[nom_col] = input_auditoria

        layout.append([
            sg.Text(f"  {etiqueta}".ljust(15), size=(16, 1), font=('CourierPS', 10), text_color='white'),
            input_auditoria
        ])

    layout.append([sg.HorizontalSeparator()])
    Msg_Err = sg.Text("", size=(80, 1), text_color='red', key='msg_error', font=('CourierPS', 9, 'bold'))
    layout.append([Msg_Err])

    layout.append([sg.HorizontalSeparator()])

    botones = []
    if AccReg == "Cre":
        botones.append(sg.Button(" [Ctrl+G] CREAR ", key='guardar', button_color=('white', '#0000aa')))
    elif AccReg == "Mod":
        botones.append(sg.Button(" [Ctrl+G] MODIFICAR ", key='guardar', button_color=('white', '#0000aa')))
    elif AccReg == "Eli":
        botones.append(sg.Button(" [Ctrl+E] ELIMINAR ", key='eliminar', button_color=('white', '#aa0000')))
    elif AccReg == "Ver":
        botones.append(sg.Button(" [Ctrl+C] COPIAR ", key='copiar', button_color=('white', '#0000aa')))
        botones.append(sg.Button(" [Ctrl+M] EMAIL ", key='email', button_color=('white', '#0000aa')))

    botones.extend([sg.Button(" [Ctrl+S] SALIR ", key='salir')])

    layout.append(botones)

    window = sg.Window(
        f"{Mem_Tab_Nom} - {txt_titulo}",
        layout,
        finalize=True,
        return_keyboard_events=True,
        modal=True,
        font=('CourierPS', 10),
        keep_on_top=True
    )

    window.bind('<Control-g>', 'guardar')
    window.bind('<Control-G>', 'guardar')
    window.bind('<Control-e>', 'eliminar')
    window.bind('<Control-E>', 'eliminar')
    window.bind('<Control-s>', 'salir')
    window.bind('<Control-S>', 'salir')
    window.bind('<Control-c>', 'copiar')
    window.bind('<Control-C>', 'copiar')
    window.bind('<Control-m>', 'email')
    window.bind('<Control-M>', 'email')
    window.bind('<Escape>', 'salir')

    res = {"save": False}
    verificaciones_dic = {}
    for f in Mem_Tab_ClmMod:
        opc_raw = str(f[4]).strip() if (len(f) > 4 and f[4]) else ""
        lista_opc = [o.strip() for o in opc_raw.split(',')] if opc_raw else []

        verificaciones_dic[f[0]] = {
            "req": (len(f) > 3 and f[3] == "N"),
            "lab": f[1],
            "opc": lista_opc
        }

    eliminar_confirmado = False

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'salir', 'Escape:27'):
            res["save"] = False
            break

        window['msg_error'].update("")

        if event in ('guardar', 'Guardar:71'):
            error_encontrado = False

            for nom_col, txt_obj in inputs_dic.items():
                if nom_col.startswith('audit_'):
                    continue

                info = verificaciones_dic.get(nom_col)
                if not info:
                    continue

                valor = values.get(f"input_{nom_col}", "").strip()

                if info["req"] and not valor:
                    window['msg_error'].update(f" ERROR: El campo [{info['lab']}] es OBLIGATORIO. ")
                    window[f"input_{nom_col}"].set_focus()
                    error_encontrado = True
                    break

                if info["opc"] and valor:
                    if valor not in info["opc"]:
                        validas = ", ".join(info["opc"])
                        window['msg_error'].update(f" ERROR en [{info['lab']}]: Use solo ({validas}) ")
                        window[f"input_{nom_col}"].set_focus()
                        error_encontrado = True
                        break

            if error_encontrado:
                continue

            Mem_FncNom = f"{Mem_Tab}_VfyDat"
            Mem_FncNomVfy = None

            import builtins
            for Mem_NomAtr in dir(builtins):
                contenedor = getattr(builtins, Mem_NomAtr, None)
                if contenedor and hasattr(contenedor, '__dict__'):
                    if hasattr(contenedor, Mem_FncNom):
                        Mem_FncNomVfy = getattr(contenedor, Mem_FncNom)
                        break

            if not Mem_FncNomVfy:
                for Mem_FemInf in inspect.stack():
                    if Mem_FncNom in Mem_FemInf.frame.f_globals:
                        Mem_FncNomVfy = Mem_FemInf.frame.f_globals[Mem_FncNom]
                        break

            if Mem_FncNomVfy and callable(Mem_FncNomVfy):
                class FakeInput:
                    def __init__(self, text):
                        self.text = text

                Mem_DatVfy = {k: FakeInput(values.get(f"input_{k}", "")) for k in inputs_dic.keys() if not k.startswith('audit_')}
                Mem_Err, Mem_Err_Clm = Mem_FncNomVfy(Mem_DatVfy, verificaciones_dic, AccReg)

                if Mem_Err != "":
                    window['msg_error'].update(f" ERROR : {Mem_Err}")
                    if Mem_Err_Clm in inputs_dic:
                        window[f"input_{Mem_Err_Clm}"].set_focus()
                    continue

            res["save"] = True
            break

        elif event in ('eliminar', 'Eliminar:69'):
            if not eliminar_confirmado:
                window['eliminar'].update(" [Ctrl+E] ¿ SEGURO ? ")
                window['eliminar'].update(button_color=('white', '#ff0000'))
                eliminar_confirmado = True
            else:
                res["save"] = "Borrar"
                break

        elif event in ('copiar', 'Copiar:67'):
            from Yos.YosLib import Yos_ClipCopy
            lineas = []
            for nom_col, info in verificaciones_dic.items():
                valor = values.get(f"input_{nom_col}", "")
                lineas.append(f"{info['lab']} : {valor}")
            txt_ficha = "\n".join(lineas)
            Yos_ClipCopy(txt_ficha)
            window['msg_error'].update(" [ INFO ] Registro copiado al portapapeles. ", text_color='green')

        elif event in ('email', 'Email:77'):
            lineas = []
            asunto_id = "Registro"
            for nom_col, info in verificaciones_dic.items():
                valor = values.get(f"input_{nom_col}", "")
                lineas.append(f"{info['lab']} : {valor}")
                if nom_col in ('cNom', 'cTxt'):
                    asunto_id = valor
            txt_ficha = "\n".join(lineas)
            res["save"] = ("Email", asunto_id, txt_ficha)
            break

    window.close()

    if res["save"] == "Borrar":
        return "Borrar"
    elif isinstance(res["save"], tuple) and res_save[0] == "Email":
        return res["save"]
    elif res["save"]:
        return {n: values.get(f"input_{n}", "") for n in inputs_dic.keys() if not n.startswith('audit_')}

    return None

# =============================================================================
# FUNCION PRINCIPAL RENOMBRADA A Idd_TabMod_Gui
# =============================================================================
def Idd_TabMod_Gui(Fnc_Svr, Fnc_Tab, Fnc_Ord=None, Fnc_Brw=None, Fnc_ClmMod=None):
    import FreeSimpleGUI as sg

    global usuario_actual, nLin, offset, fila_resaltada, MARGEN
    global Mem_Dbt_Svr, Mem_Tab_Nom, Mem_Tab_Brw, Mem_Tab_Ord, Mem_Tab_ClmMod, Mem_Tab_ClmMod_Def, order_by_col, Mem_Ftr
    global Mem_Svr, Mem_Tab, Mem_Cnx_YosCfg, Mem_Cur_YosCfg

    Mem_Svr = Fnc_Svr
    Mem_Tab = Fnc_Tab

    Err_CalFra = inspect.stack()[1]
    Err_Ach = os.path.basename(Err_CalFra.filename)
    Err_Lin = Err_CalFra.lineno
    Err_Fnc = Err_CalFra.function
    if Err_Fnc == '<module>':
        Err_Fnc = "Nivel Principal (Main)"

    if not Fnc_Svr:
        sg.popup_error(f"Idd_TabMod_Gui(Fnc_Svr, Fnc_Tab) Fnc_Svr=Servidor es Obligatorio ({Err_Fnc} {Err_Ach} - {Err_Lin})")
        return None

    if not Fnc_Tab:
        sg.popup_error(f"Idd_TabMod_Gui(Fnc_Svr, Fnc_Tab) Fnc_Tab=Tabla es Obligatoria ({Err_Fnc} {Err_Ach} - {Err_Lin})")
        return None

    Mem_Tab_Nom = Fnc_Tab

    if not Fnc_Ord:
        Fnc_Ord = "Main"

    if not Fnc_Brw:
        Fnc_Brw = "Main"

    if not Fnc_ClmMod:
        Fnc_ClmMod = "Main"

    usuario_actual = YosCfg["Usr_Nik"]

    if YosCfg["Apl_Etn_Alt"]:
        nLin = YosCfg["Apl_Etn_Alt"] - 10
    else:
        nLin = 30
    offset = 0
    fila_resaltada = None
    MARGEN = 1
    Mem_Ftr = ""

    maximizar_consola()
    Mem_Dbt_Svr = Fnc_Svr
    Mem_Tab_Nom = Fnc_Tab

    from Yos.Idd_BdtSvr import Cnx, Sel, SelTot, Cie
    Mem_Cnx_YosCfg = Cnx(Fnc_Svr)
    Mem_Cur_YosCfg = Mem_Cnx_YosCfg.cursor()

    if isinstance(Fnc_Ord, list):
        Mem_Tab_Ord = Fnc_Ord
    else:
        Mem_Cur_YosCfg.execute("SELECT cTxt, cCmd FROM Ord WHERE cTab = ? ORDER BY cNum", (Mem_Tab_Nom,))
        Mem_Tab_Ord = [(r['cTxt'], r['cCmd']) for r in Mem_Cur_YosCfg.fetchall()]

    if isinstance(Fnc_Brw, list):
        Mem_Tab_Brw = Fnc_Brw
    else:
        Mem_Cur_YosCfg.execute("SELECT cCab, cLon, cClm FROM Brw WHERE cTab = ? AND cCod = ? ORDER BY cNum", (Mem_Tab_Nom, Fnc_Brw))
        Mem_Tab_Brw = [(r['cCab'], r['cLon'], r['cClm']) for r in Mem_Cur_YosCfg.fetchall()]

    if isinstance(Fnc_ClmMod, list):
        Mem_Tab_ClmMod = Fnc_ClmMod
    else:
        Mem_Cur_YosCfg.execute("SELECT cClm, cCab, cMod, cNul, cOpc FROM ClmMod WHERE cTab = ? AND cCod = ? ORDER BY cNum", (Mem_Tab_Nom, Fnc_ClmMod))
        Mem_Tab_ClmMod = [(r['cClm'], r['cCab'], r['cMod'], r['cNul'], r['cOpc']) for r in Mem_Cur_YosCfg.fetchall()]

    Mem_Cur_YosCfg.execute(f"PRAGMA table_info({Mem_Tab_Nom})")
    estruc_sql = {r[1]: r for r in Mem_Cur_YosCfg.fetchall()}

    Mem_Tab_ClmMod_Def = []
    for col_local in Mem_Tab_ClmMod:
        nom_col = col_local[0]

        if nom_col in estruc_sql:
            info = estruc_sql[nom_col]
            tipo_raw = str(info[2]).upper()

            if any(x in tipo_raw for x in ["CHAR", "TEXT", "CLOB", "STR"]):
                tipo_yos = "C"
            elif any(x in tipo_raw for x in ["INT", "SERIAL", "BIT"]):
                tipo_yos = "N"
            elif any(x in tipo_raw for x in ["DATE", "TIME"]):
                tipo_yos = "D"
            elif any(x in tipo_raw for x in ["DECIMAL", "NUMERIC", "DOUBLE", "FLOAT", "REAL", "MONEY"]):
                tipo_yos = "M"
            else:
                tipo_yos = "C"

            m = re.search(r'\((\d+)\)', tipo_raw)
            if m:
                lon = int(m.group(1))
            else:
                if tipo_yos == "C": lon = 255
                elif tipo_yos == "N": lon = 10
                elif tipo_yos == "D": lon = 10
                elif tipo_yos == "M": lon = 15
                else: lon = 20

            Mem_Tab_ClmMod_Def.append((tipo_yos, lon))
        else:
            Mem_Tab_ClmMod_Def.append(("C", 20))

    idx_ord = 0
    order_by_col = Mem_Tab_Ord[idx_ord][1]
    pad = " " * MARGEN

    info_layout = [
        [sg.Text(f"TABLA : {Fnc_Svr} -> {Mem_Tab_Nom}", font=('CourierPS', 9), text_color='black'),
         sg.Text("", key='info_orden', font=('CourierPS', 9), text_color='black'),
         sg.Text("", key='info_filtro', font=('CourierPS', 9), text_color='black')],
        [sg.Text("", key='info_registros', font=('CourierPS', 9), text_color='black'),
         sg.Text("", key='info_pagina', font=('CourierPS', 9), text_color='black'),
         sg.Text(f"Lineas Browse : {nLin}", key='info_lineas', font=('CourierPS', 9), text_color='black')]
    ]

    comandos_layout = [
        [sg.Button("Salir (S)", key='S', font=('CourierPS', 9), button_color=('white', 'red')),
         sg.Button("Orden (O)", key='ORD', font=('CourierPS', 9)),
         sg.Button("Buscar (B)", key='B', font=('CourierPS', 9)),
         sg.Button("Filtro (F)", key='FTR', font=('CourierPS', 9)),
         sg.Button("Lineas (L)", key='LB', font=('CourierPS', 9)),
         sg.Button("Ayuda (F2)", key='F2', font=('CourierPS', 9)),
        ],
        [sg.Button("Crear (C)", key='C', font=('CourierPS', 9), button_color=('white', 'green')),
         sg.Button("Ver (V)", key='V', font=('CourierPS', 9)),
         sg.Button("Modificar (M)", key='M', font=('CourierPS', 9)),
         sg.Button("Eliminar (E)", key='E', font=('CourierPS', 9), button_color=('white', '#aa0000')),
         sg.Button("|< Primero (P)", key='P', font=('CourierPS', 9)),
         sg.Button("<< Retroceder (R)", key='R', font=('CourierPS', 9)),
         sg.Button(">> Avanzar (A)", key='A', font=('CourierPS', 9)),
         sg.Button(">| Ultimo (U)", key='U', font=('CourierPS', 9))
        ]
    ]

    headings = [c[0] for c in Mem_Tab_Brw]
    col_widths = []
    for c in Mem_Tab_Brw:
        ancho_str = str(c[1])
        if "%" in ancho_str:
            col_widths.append(20)
        else:
            try:
                col_widths.append(max(4, int(ancho_str)))
            except:
                col_widths.append(15)

    tabla_elem = sg.Table(
        values=[],
        headings=headings,
        auto_size_columns=False,
        col_widths=col_widths,
        display_row_numbers=False,
        justification='left',
        num_rows=nLin,
        key='tabla_principal',
        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
        enable_events=True,
        text_color='black',
        background_color='white',
        alternating_row_color='#f0f0f0',
        header_background_color='#0000aa',
        header_text_color='white',
        font=('CourierPS', 9),
        row_height=18,
        expand_x=True,
        expand_y=True,
        bind_return_key=False  # <-- CAMBIO: Desactivado el enter en tabla
    )

    layout = [
        [sg.Frame("Información", info_layout, font=('CourierPS', 9))],
        [sg.Frame("Comandos", comandos_layout, font=('CourierPS', 9))],
#        [sg.HorizontalSeparator()],
        [tabla_elem],
#        [sg.HorizontalSeparator()],
        [sg.Text("Seleccione acción o use atajos de teclado", text_color='yellow', font=('CourierPS', 9))]
    ]

    window = sg.Window(
        f"Idd_TabMod_Gui - {Mem_Tab_Nom}",
        layout,
        finalize=True,
        resizable=True,
        return_keyboard_events=True,
        font=('CourierPS', 10),
        location=(0, 0),   # Esquina superior izquierda
        size=(sg.Window.get_screen_size())  # Tamaño de pantalla completa
    )

    # Maximizar la ventana
    window.maximize()

    window.bind('<F2>', 'F2')
    window.bind('<Prior>', 'PAGEUP')
    window.bind('<Next>', 'PAGEDOWN')

    def cargar_datos():
        nonlocal db_col_names

        where_ftr = f"WHERE {order_by_col} LIKE ?" if Mem_Ftr else ""
        params_filtro = (f"%{Mem_Ftr}%",) if Mem_Ftr else ()

        try:
            Mem_Cur_YosCfg.execute(f"SELECT COUNT(*) FROM {Mem_Tab_Nom} {where_ftr}", params_filtro)
            total_regs = Mem_Cur_YosCfg.fetchone()[0]
        except Exception as e:
            sg.popup_error(f"Error al contar registros: {e}")
            total_regs = 0

        try:
            query = f"SELECT rowid, *, ({order_by_col}) as ord_val FROM {Mem_Tab_Nom} {where_ftr} ORDER BY {order_by_col} COLLATE NOCASE LIMIT {nLin} OFFSET {offset}"
            Mem_Cur_YosCfg.execute(query, params_filtro)
            registros = Mem_Cur_YosCfg.fetchall()
        except Exception as e:
            sg.popup_error(f"Error al cargar datos: {e}\nQuery: {query}")
            registros = []

        pag_actual = (offset // nLin) + 1 if nLin > 0 else 1
        total_paginas = (total_regs + nLin - 1) // nLin if total_regs > 0 else 1

        etiqueta_orden = next((o[0] for o in Mem_Tab_Ord if o[1] == order_by_col), order_by_col)

        window['info_orden'].update(f"Orden : {etiqueta_orden}")
        window['info_filtro'].update(f"Filtro : {Mem_Ftr}" if Mem_Ftr else "")
        window['info_registros'].update(f"Reg : {offset+1}/{total_regs}")
        window['info_pagina'].update(f"Pag : {pag_actual}/{total_paginas}")
        window['info_lineas'].update(f"Lineas Browse : {nLin}")

        # Preparar datos para tabla - SIN COLUMNA ID
        datos_tabla = []
        for r in registros:
            fila = []
            # r[0] es rowid, r[1:] son los datos de las columnas
            for i, col in enumerate(Mem_Tab_Brw):
                col_name = col[2] if len(col) > 2 and col[2] else col[0]
                try:
                    # Buscar índice en db_col_names (0-based), sumar 1 porque r[0] es rowid
                    idx_bd = db_col_names.index(col_name) + 1 if col_name in db_col_names else 0
                except ValueError:
                    idx_bd = 0

                valor = r[idx_bd] if idx_bd < len(r) else None
                str_valor = str(valor) if valor is not None else ""

                max_ancho = col_widths[i] * 2 if i < len(col_widths) else 40
                fila.append(str_valor[:max_ancho])

            datos_tabla.append(fila)

        window['tabla_principal'].update(values=datos_tabla)

        if fila_resaltada:
            for idx, r in enumerate(registros):
                if str(r[-1]) == str(fila_resaltada):
                    window['tabla_principal'].update(select_rows=[idx])
                    break

        return registros

    Mem_Cur_YosCfg.execute(f"PRAGMA table_info({Mem_Tab_Nom})")
    db_col_names = [col[1] for col in Mem_Cur_YosCfg.fetchall()]

    registros_actuales = cargar_datos()
    registro_seleccionado = None

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        seleccion = values['tabla_principal']
        if seleccion:
            idx_sel = seleccion[0]
            if 0 <= idx_sel < len(registros_actuales):
                registro_seleccionado = registros_actuales[idx_sel]
        else:
            registro_seleccionado = None

        cmd = None
        reg_sel = None

        if event in ('S', 's'):
            break
        elif event == 'PAGEUP':
            cmd = 'PAGEUP'
        elif event == 'PAGEDOWN':
            cmd = 'PAGEDOWN'
        elif event in ('P', 'p', 'P'):
            cmd = 'P'
        elif event in ('R', 'r', 'R'):
            cmd = 'R'
        elif event in ('A', 'a', 'A'):
            cmd = 'A'
        elif event in ('U', 'u', 'U'):
            cmd = 'U'
        elif event in ('LB', 'l', 'L'):
            cmd = 'LB'
        elif event in ('P',):
            cmd = 'P'
        elif event in ('R',):
            cmd = 'R'
        elif event in ('A',):
            cmd = 'A'
        elif event in ('U',):
            cmd = 'U'
        elif event in ('ORD', 'o', 'O'):
            cmd = 'ORD'
        elif event in ('B', 'b', 'B'):
            cmd = 'B'
        elif event in ('FTR', 'f', 'F'):
            cmd = 'FTR'
        elif event in ('C', 'c', 'C'):
            cmd = 'C'
        # <-- CAMBIO: Eliminado el evento 'tabla_principal' para no abrir Ver automáticamente
        elif event in ('V', 'v', 'V'):
            if registro_seleccionado:
                cmd = 'V'
                reg_sel = registro_seleccionado
        elif event in ('M', 'm', 'M'):
            if registro_seleccionado:
                cmd = 'M'
                reg_sel = registro_seleccionado
        elif event in ('E', 'e', 'E'):
            if registro_seleccionado:
                cmd = 'E'
                reg_sel = registro_seleccionado
        elif event in ('F2',):
            cmd = 'F2'
        # <-- ELIMINADO: No se procesa el evento de tabla como comando

        if cmd == 'PAGEUP':
            offset = max(0, offset - nLin)
            registros_actuales = cargar_datos()
        elif cmd == 'PAGEDOWN':
            Mem_Cur_YosCfg.execute(f"SELECT COUNT(*) FROM {Mem_Tab_Nom}")
            total_regs = Mem_Cur_YosCfg.fetchone()[0]
            offset = min(offset + nLin, max(0, ((total_regs-1)//nLin)*nLin))
            registros_actuales = cargar_datos()
        elif cmd == 'P':
            offset = 0
            registros_actuales = cargar_datos()
        elif cmd == 'R':
            offset = max(0, offset - nLin)
            registros_actuales = cargar_datos()
        elif cmd == 'A':
            Mem_Cur_YosCfg.execute(f"SELECT COUNT(*) FROM {Mem_Tab_Nom}")
            total_regs = Mem_Cur_YosCfg.fetchone()[0]
            offset = min(offset + nLin, max(0, ((total_regs-1)//nLin)*nLin))
            registros_actuales = cargar_datos()
        elif cmd == 'U':
            Mem_Cur_YosCfg.execute(f"SELECT COUNT(*) FROM {Mem_Tab_Nom}")
            total_regs = Mem_Cur_YosCfg.fetchone()[0]
            offset = max(0, ((total_regs - 1) // nLin) * nLin)
            registros_actuales = cargar_datos()
        elif cmd == 'LB':
            nueva_lin = sg.popup_get_text(f"Lineas Browse ({nLin}) :", default_text=str(nLin))
            if nueva_lin and nueva_lin.isdigit():
                val_num = int(nueva_lin)
                if val_num > 0:
                    nLin = val_num
                    offset = 0
                    window['tabla_principal'].update(num_rows=nLin)
                    registros_actuales = cargar_datos()
        elif cmd == 'ORD':
            if Mem_Tab_Ord:
                opciones = "\n".join([f"{i+1}. {o[0]}" for i, o in enumerate(Mem_Tab_Ord)])
                op_ord = sg.popup_get_text(f"SELECCIONE ORDEN:\n{opciones}\n\nOpción:")
                if op_ord and op_ord.isdigit() and 1 <= int(op_ord) <= len(Mem_Tab_Ord):
                    idx_ord = int(op_ord) - 1
                    order_by_col = Mem_Tab_Ord[idx_ord][1]
                    offset = 0
                    Mem_Ftr = ""
                    registros_actuales = cargar_datos()
        elif cmd == 'B':
            busqueda_incremental_dinamica(Mem_Cnx_YosCfg, db_col_names, obtener_anchos_reales())
            Mem_Ftr = ""
            registros_actuales = cargar_datos()
        elif cmd == 'FTR':
            etiqueta_filtro = next((o[0] for o in Mem_Tab_Ord if o[1] == order_by_col), order_by_col)
            Mem_Ftr = sg.popup_get_text(f"Filtro por {etiqueta_filtro} :", default_text=Mem_Ftr) or ""
            offset = 0
            registros_actuales = cargar_datos()
        elif cmd == 'F2':
            sg.popup_scrolled("""CONTROLES DE NAVEGACIÓN:

[P]rimero    - Ir al primer registro
[R]etroceder - Página anterior
[A]vanzar    - Página siguiente
[U]ltimo     - Ir al último registro
[PageUp]     - Retroceder página
[PageDown]   - Avanzar página

ACCIONES:
[O]rden      - Cambiar ordenamiento
[B]uscar     - Búsqueda incremental
[F]iltro     - Filtrar registros
[L]íneas     - Cambiar líneas mostradas

[C]rear      - Nuevo registro
[V]er        - Ver seleccionado (necesita selección)
[M]odificar  - Modificar seleccionado (necesita selección)
[E]liminar   - Eliminar seleccionado (necesita selección)

[S]alir      - Cerrar aplicación""", title="Ayuda del Sistema", font=('CourierPS', 9), text_color='black')
        elif cmd == 'C':
            reg_nuevo = formulario_yos(db_col_names, None, AccReg="Cre")
            if isinstance(reg_nuevo, dict):
                reg_nuevo['cModRegNik'] = usuario_actual
                reg_nuevo['cModRegTim'] = Yos_TimeStamp()
                insert_data = {k: v for k, v in reg_nuevo.items() if k != "nAutInc"}
                cols = ", ".join(insert_data.keys())
                pls = ", ".join(["?"] * len(insert_data))
                try:
                    Mem_Cur_YosCfg.execute(f"INSERT INTO {Mem_Tab_Nom} ({cols}) VALUES ({pls})", list(insert_data.values()))
                    Mem_Cnx_YosCfg.commit()
                    sg.popup_quick_message("Registro creado", background_color='green', text_color='white')
                    registros_actuales = cargar_datos()
                except Exception as e:
                    sg.popup_error(f"Error al crear: {e}")
        elif cmd == 'V' and reg_sel:
            res_ver = formulario_yos(db_col_names, reg_sel, AccReg="Ver")
            if isinstance(res_ver, tuple) and res_ver[0] == "Email":
                from Yos import EmlEnv
                EmlEnv("", f"Ficha: {res_ver[1]}", res_ver[2])
        elif cmd == 'M' and reg_sel:
            cambios = formulario_yos(db_col_names, reg_sel, AccReg="Mod")
            if isinstance(cambios, dict):
                cambios.pop("nAutInc", None)
                cambios_finales = {}
                for k, v in cambios.items():
                    permiso = next((c[2].strip() for c in Mem_Tab_ClmMod if c[0] == k), "")
                    if permiso == "Mod":
                        cambios_finales[k] = v
                cambios_finales['cModRegNik'] = usuario_actual
                cambios_finales['cModRegTim'] = Yos_TimeStamp()

                if cambios_finales:
                    set_sql = ", ".join([f"{k}=?" for k in cambios_finales.keys()])
                    valores = list(cambios_finales.values()) + [reg_sel[0]]
                    try:
                        Mem_Cur_YosCfg.execute(f"UPDATE {Mem_Tab_Nom} SET {set_sql} WHERE rowid=?", valores)
                        Mem_Cnx_YosCfg.commit()
                        sg.popup_quick_message("Registro modificado", background_color='blue', text_color='white')
                        registros_actuales = cargar_datos()
                    except Exception as e:
                        sg.popup_error(f"Error al modificar: {e}")
        elif cmd == 'E' and reg_sel:
            dato = formulario_yos(db_col_names, reg_sel, AccReg="Eli")
            if dato == "Borrar":
                try:
                    Mem_Cur_YosCfg.execute(f"DELETE FROM {Mem_Tab_Nom} WHERE rowid=?", (reg_sel[0],))
                    Mem_Cnx_YosCfg.commit()
                    sg.popup_quick_message("Registro eliminado", background_color='red', text_color='white')
                    registros_actuales = cargar_datos()
                except Exception as e:
                    sg.popup_error(f"Error al eliminar: {e}")

    window.close()
    Mem_Cnx_YosCfg.close()

# =============================================================================
# INICIO DEL SISTEMA
# =============================================================================
if __name__ == "__main__":
    Mem_Dbt = "YosCfg"
    Mem_Tab = "Mnu"
    Idd_TabMod_Gui(Mem_Dbt, Mem_Tab)
