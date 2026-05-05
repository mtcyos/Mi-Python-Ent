#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import os
import re
import sys
import ctypes
import locale
import msvcrt

# 1. Herramientas de impresión y entrada rápida
from prompt_toolkit.shortcuts import print_formatted_text, prompt
from prompt_toolkit.formatted_text import HTML

# 2. El motor de la Aplicación y Gestión de Instancia
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app

# 3. Contenedores y Layout (AGRUPADOS EN UNA SOLA LÍNEA)
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, ConditionalContainer, Float

# 4. Controles de bajo nivel (Si los necesitas para Buffer)
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.buffer import Buffer

# 5. Widgets (La cara de la interfaz Yos)
from prompt_toolkit.widgets import Button, TextArea, Label, Frame

# 6. Teclado, Estilos y Filtros de Foco
from prompt_toolkit.styles import Style as PtStyle
from prompt_toolkit.filters import has_focus
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

# 7. Herramientas de Ratón y Eventos
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard

from Yos import Yos_FrmCls, FrmWit, FrmLin, AplIni, Yos_TimeStamp

try:
    locale.setlocale(locale.LC_TIME, "")
except:
    pass

# =============================================================================
# FUNCIONES DE APOYO
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
        Mem_Ancho = os.get_terminal_size().columns - (len(Mem_Tab_Brw) * 3) - 12  # le quito las | de cada columnas y los Botones
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
# BUSCAR
# =============================================================================
def busqueda_incremental_dinamica(conn, db_col_names, anchos):
    global offset, fila_resaltada, nLin, order_by_col, Mem_Ftr
    bus = ""
    pad = " " * MARGEN
    where_ftr = f"WHERE {order_by_col} LIKE ?" if Mem_Ftr else ""

    while True:
        os.system('cls')
        cur = conn.cursor()
        op_and = "AND" if where_ftr else "WHERE"
        params_bus = (f"%{Mem_Ftr}%", bus) if Mem_Ftr else (bus,)
        cur.execute(f"SELECT COUNT(*) FROM {Mem_Tab_Nom} {where_ftr} {op_and} {order_by_col} < ? COLLATE NOCASE", params_bus)
        posicion_real = cur.fetchone()[0]
        mitad = nLin // 2
        offset_temp = max(0, posicion_real - mitad)

        cur.execute(f"SELECT {order_by_col} FROM {Mem_Tab_Nom} {where_ftr} {op_and} {order_by_col} >= ? COLLATE NOCASE ORDER BY {order_by_col} COLLATE NOCASE LIMIT 1", params_bus)
        res = cur.fetchone()
        fila_resaltada = res[0] if res else None

        etiqueta_orden = next((o[0] for o in Mem_Tab_Ord if o[1] == order_by_col), order_by_col)

        print_formatted_text(HTML(f"<ansibggreen><ansiwhite> Buscar en {etiqueta_orden} : {bus.ljust(20)} </ansiwhite></ansibggreen>"))
        print_formatted_text(HTML(f"<green> [Letras]: Buscar | [Enter]: Aceptar | [Esc]: Cancelar\n</green>"))

        params_sel = (f"%{Mem_Ftr}%",) if Mem_Ftr else ()
        cur.execute(f"SELECT rowid, *, ({order_by_col}) as ord_val FROM {Mem_Tab_Nom} {where_ftr} ORDER BY {order_by_col} COLLATE NOCASE LIMIT {nLin} OFFSET {offset_temp}", params_sel)
        regs = cur.fetchall()

        for idx, r in enumerate(regs):
            n_fila = str(idx + 1).zfill(2)
            val_comparar = str(r[-1])
            es_esta_fila = (fila_resaltada is not None and val_comparar.upper() == str(fila_resaltada).upper())
            bg = "<ansibgyellow>" if es_esta_fila else ""
            ebg = "</ansibgyellow>" if es_esta_fila else ""
            fg = "<ansiwhite>" if es_esta_fila else "<ansicyan>"
            efg = "</ansiwhite>" if es_esta_fila else "</ansicyan>"
            fg2 = "<ansiwhite>" if es_esta_fila else "<ansiyellow>"
            efg2 = "</ansiwhite>" if es_esta_fila else "</ansiyellow>"

            linea = f"{bg}{fg2}{pad}{n_fila.ljust(anchos[0])}{pad}{efg2}{ebg}<ansiblue>|</ansiblue>"
            for i in range(1, len(Mem_Tab_Brw)):
                idx_bd = db_col_names.index(Mem_Tab_Brw[i][2]) + 1 if Mem_Tab_Brw[i][2] else 0
                valor = str(r[idx_bd] if idx_bd > 0 and r[idx_bd] is not None else "")[:anchos[i]].ljust(anchos[i])
                linea += f"{bg}{fg}{pad}{valor}{pad}{efg}{ebg}<ansiblue>|</ansiblue>"
            print_formatted_text(HTML(linea))

        for _ in range(nLin - len(regs)): print("")
        print_formatted_text(HTML(f"<ansiblue>{'═' * (sum(anchos) + len(anchos) * 3)}</ansiblue>"))

        char = msvcrt.getch()
        if char == b'\r':
            offset = offset_temp
            break
        elif char == b'\x1b':
            fila_resaltada = None
            break
        elif char == b'\x08':
            bus = bus[:-1]
        else:
            try:
                if len(bus) < 20: bus += char.decode('utf-8')
            except: pass

# =============================================================================
# FORMULARIO YOS
# =============================================================================
estilo_yos = PtStyle([
    ("button", "bg:#0000aa fg:#ffffff"),           # AZUL
    ("button.focused", "bg:#00ff00 fg:#000000"),    # VERDE
    ("text-area", "bg:#333333 fg:#ffffff"),        # GRIS
    ("titulo-top", "bg:#00aaaa fg:white bold"),    # CYAN (Estándar)
    ("titulo-rojo", "bg:#aa0000 fg:white bold"),   # ROJO (Peligro)
    ("button titulo-rojo", "bg:#aa0000 fg:white bold"),
    ("msg-error", "fg:#ff0000 bg:#000000 bold")
])
#def formulario_yos(db_col_names, registro=None, solo_lectura=False, eliminar=False):
def formulario_yos(db_col_names, registro=None, AccReg="Cre"):
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

    for i, f in enumerate(Mem_Tab_ClmMod):
        nom_col = f[0]
        etiqueta = f[1]
        Mem_Mod = f[2]
        Mem_Mod_Style = "text-area"
        ancho_sql = Mem_Tab_ClmMod_Def[i][1]
        ancho_Clm = Mem_Tab_ClmMod_Def[i][1]

        match AccReg:
            case "Cre":
                es_obligatorio = "*" if (len(f) > 3 and f[3] == "N") else " "
            case "Ver":
                es_obligatorio = ""
            case "Mod":
                es_obligatorio = "*" if (len(f) > 3 and f[3] == "N") else " "
                if Mem_Mod == "Cre":
                    solo_lectura=True
                    Mem_Mod_Style = "button.focused"
            case "Eli":
                es_obligatorio = ""

        texto_label = f" {es_obligatorio}{etiqueta}"

        # Verifico el ancho maximo de la pantalla
        if ancho_Clm > YosCfg["Apl_Etn_Lon"]:
            ancho_Clm= YosCfg["Apl_Etn_Lon"] -21

        # CREACIÓN DEL CAMPO
        # 1. CREACIÓN DEL CAMPO
        txt_input = TextArea(
            text=str(registro[i+1] if registro else ""),
            multiline=False,
            width=ancho_Clm,
            read_only=solo_lectura,
            style=f"class:{Mem_Mod_Style}"
        )
        # SOLUCIÓN DEFINITIVA: Desactivar el accept_handler del buffer
        # Esto evita que Enter "acepte" el buffer y salga del campo
        txt_input.buffer.accept_handler = None

        # Key binding local que captura Enter ANTES que cualquier otro manejador
        kb_local = KeyBindings()

        @kb_local.add('enter', eager=True)
        def _(event):
            # Solo mover foco, nada más
            get_app().layout.focus_next()
            # No retornamos nada para no propagar el evento

        # Inyectar al control interno
        txt_input.control.key_bindings = kb_local

        # 2. FUNCIÓN DE RECORTE AUTOMÁTICO (El "Filtro Yos")
        def limitar_texto(buffer, max_l=ancho_sql):
            if len(buffer.text) > max_l:
                # Si se pasa, cortamos el texto al máximo permitido
                buffer.text = buffer.text[:max_l]
                # Movemos el cursor al final del nuevo texto
                buffer.cursor_position = max_l

        # Aplicamos el limitador al buffer interno del campo
        txt_input.buffer.on_text_changed += limitar_texto

        inputs_dic[nom_col] = txt_input

        # CREACION DE LOS ROTULOS
        def click_label(mouse_event, t=txt_input):
            if mouse_event.event_type == MouseEventType.MOUSE_UP:
                get_app().layout.focus(t)

        label_win = Window(
            content=FormattedTextControl(
                text=texto_label.ljust(15),
                focusable=False, # El TAB lo ignora
                show_cursor=False
            ),
            width=18,
            height=1,
            style="class:button"
        )
        # Inyectamos el manejador directamente al control de contenido
        label_win.content.mouse_handler = click_label

        # 3. Agregamos al layout
        campos_dinamicos.append(VSplit([label_win, Window(width=2), txt_input]))

    # Añado cModRegNik cModRegTim
    campos_dinamicos.append(Window(height=1)) # Un pequeño respiro

    campos_auditoria = [
        ('cModRegNik', 'USUARIO', 20),
        ('cModRegTim', 'MODIFICADO', 20)
    ]

    for nom_col, etiqueta, ancho_fijo in campos_auditoria:
        # 1. Buscamos el valor en el registro por el nombre de la columna
        # registro es un sqlite3.Row, así que admite acceso por nombre
        valor_auditoria = str(registro[nom_col] if registro else "")

        # 2. Creamos el campo (Siempre Solo Lectura)
        txt_auditoria = TextArea(
            text=valor_auditoria,
            multiline=False,
            width=ancho_fijo,
            read_only=True,
            style="class:button.focused" # O usa un estilo más tenue si prefieres
        )
        # Desactivar accept_handler y agregar Enter local
        txt_auditoria.buffer.accept_handler = None
        kb_auditoria = KeyBindings()
        @kb_auditoria.add('enter', eager=True)
        def _(event):
            get_app().layout.focus_next()
        txt_auditoria.control.key_bindings = kb_auditoria

        inputs_dic[nom_col] = txt_auditoria

        # 3. Rótulo informativo (Sin asteriscos porque es sistema)
        label_auditoria = Window(
            content=FormattedTextControl(
                text=f"  {etiqueta}".ljust(15),
                focusable=False,
                show_cursor=False
            ),
            width=18,
            height=1,
            style="class:button.focused"
        )

        # 4. Lo añadimos al final de la lista de campos
        campos_dinamicos.append(VSplit([label_auditoria, Window(width=2), txt_auditoria]))


    # CREACIÓN DEL CAMPO DE MENSAJE (Msg_Err) ---
#***************************************************************************
    # 1. HERRAMIENTAS DE CONTROL Y VALIDACIÓN
    res = {"save": False}
    verificaciones_dic = {}
    for f in Mem_Tab_ClmMod:
        # f[0]=Nombre, f[1]=Etiqueta, f[3]=Nul ('N'), f[4]=Opciones ('c,d,m,l')
        opc_raw = str(f[4]).strip() if (len(f) > 4 and f[4]) else ""
        lista_opc = [o.strip() for o in opc_raw.split(',')] if opc_raw else []

        verificaciones_dic[f[0]] = {
            "req": (len(f) > 3 and f[3] == "N"),
            "lab": f[1],
            "opc": lista_opc
        }

    # 2. OBJETO DE MENSAJE DE ERROR (Debe existir antes que las funciones)
    Msg_Err = TextArea(
        text="",
        multiline=False,
        read_only=True,
        height=1,
        focusable=False,
        style="class:msg-error"
    )
    Msg_Err.control.focusable = lambda: False
    Msg_Err.buffer.accept_handler = None

    # 3. FUNCIONES DE ACCIÓN (Usan Msg_Err y res)
    def do_save():
        Msg_Err.text = ""

        # Recorremos los inputs para validar
        for nom_col, txt_obj in inputs_dic.items():
            # USAMOS 'info' que es como lo definimos en verificaciones_dic
            info = verificaciones_dic.get(nom_col)
            if not info:
                continue

            valor = txt_obj.text.strip()

            # --- VALIDACIÓN 1: OBLIGATORIO ---
            if info["req"] and not valor:
                Msg_Err.text = f" ERROR: El campo [{info['lab']}] es OBLIGATORIO. "
                get_app().layout.focus(txt_obj)
                return

            # --- VALIDACIÓN 2: OPCIONES DINÁMICAS (cOpc - 4ª Columna) ---
            if info["opc"] and valor:
                if valor not in info["opc"]:
                    validas = ", ".join(info["opc"])
                    Msg_Err.text = f" ERROR en [{info['lab']}]: Use solo ({validas}) "
                    get_app().layout.focus(txt_obj)
                    return
#########################################################################
        # 1. Nombre de la función (ej: "Abv_VfyDat")
        Mem_FncNom = f"{Mem_Tab}_VfyDat"
        Mem_FncNomVfy = None

        # 2. RASTREO DINÁMICO EN BUILTINS (Cualquier contenedor)
        import builtins
        import inspect

        for Mem_NomAtr in dir(builtins):
            contenedor = getattr(builtins, Mem_NomAtr)

            if hasattr(contenedor, '__dict__'): # Verificamos que sea un objeto capaz de tener atributos (como tus contenedores)
                if hasattr(contenedor, Mem_FncNom):
                    Mem_FncNomVfy = getattr(contenedor, Mem_FncNom)
                    break

        # 3. RASTREO DE EMERGENCIA (Pila de llamadas)
        if not Mem_FncNomVfy:
            for Mem_FemInf in inspect.stack():
                if Mem_FncNom in Mem_FemInf.frame.f_globals:
                    Mem_FncNomVfy = Mem_FemInf.frame.f_globals[Mem_FncNom]
                    break

        # 4. EJECUCIÓN
        if Mem_FncNomVfy and callable(Mem_FncNomVfy):
#            Mem_DatVfy = {k: v.text for k, v in inputs_dic.items()}
            Mem_Err, Mem_Err_Clm = Mem_FncNomVfy(inputs_dic, verificaciones_dic, AccReg) # Ejecutamos la función de validación

            # REGLA: Si devuelve algo que no sea un string vacío, es un error
            if Mem_Err != "":
                Msg_Err.text = f" ERROR : {Mem_Err})"
                # 2. POSICIONAMOS EL CURSOR EN EL CAMPO DEL ERROR
                if Mem_Err_Clm in inputs_dic:
                    # Obtenemos el widget de esa columna
                    obj_error = inputs_dic[Mem_Err_Clm]
                    # Le pedimos a la App que ponga el foco ahí
                    get_app().layout.focus(obj_error)
                return  # Bloquea el guardado

#        print(inputs_dic.items())

######################################################################

        # Si todo está correcto, guardamos y salimos
        res["save"] = True
        app.exit()

    def do_delete_step():
        if btn_g.text == " [Ctrl+E] ELIMINAR ":
            btn_g.text = " [Ctrl+E] ¿ SEGURO ? "
            btn_g.style = "class:titulo-rojo"
        else:
            app.exit("Borrar")

    def do_copy_clipboard():
        from Yos.YosLib import Yos_ClipCopy
        lineas = []
        for nom_col, txt_obj in inputs_dic.items():
            info = verificaciones_dic.get(nom_col)
            if info:
                lineas.append(f"{info['lab']} : {txt_obj.text}")
        txt_ficha = "\n".join(lineas)
        Yos_ClipCopy(txt_ficha)
        Msg_Err.text = " [ INFO ] Registro copiado al portapapeles. "

    def do_send_email():
        lineas = []
        asunto_id = "Registro"
        for nom_col, txt_obj in inputs_dic.items():
            info = verificaciones_dic.get(nom_col)
            if info:
                lineas.append(f"{info['lab']} : {txt_obj.text}")
                if nom_col in ('cNom', 'cTxt'):
                    asunto_id = txt_obj.text
        txt_ficha = "\n".join(lineas)
        app.exit(result=("Email", asunto_id, txt_ficha))

    # 4. DEFINICIÓN DE BOTONES (Aquí se asigna valor a btn_g)
    if AccReg == "Cre":
        btn_g = Button(" [Ctrl+G] CREAR ", handler=do_save, width=21)
    elif AccReg == "Mod":
        btn_g = Button(" [Ctrl+G] MODIFICAR ", handler=do_save, width=21)
    elif AccReg == "Eli":
        btn_g = Button(" [Ctrl+E] ELIMINAR ", handler=do_delete_step, width=21)
    else:
        btn_g = Button(" --- ", handler=lambda: None, width=21)

    btn_g.left_symbol = ""; btn_g.right_symbol = ""
    btn_s = Button(" [Ctrl+S] SALIR ", handler=lambda: app.exit(), width=21)
    btn_s.left_symbol = ""; btn_s.right_symbol = ""

    btn_copy = Button(" [Ctrl+C] COPIAR ", handler=do_copy_clipboard, width=21)
    btn_copy.left_symbol = ""; btn_copy.right_symbol = ""
    btn_email = Button(" [Ctrl+M] EMAIL ", handler=do_send_email, width=21)
    btn_email.left_symbol = ""; btn_email.right_symbol = ""

    # 5. TÍTULOS Y CABECERAS
    titulos = {"Cre": "CREAR", "Ver": "VER", "Mod": "MODIFICAR", "Eli": "ELIMINAR"}
    txt_titulo = titulos.get(AccReg, "GESTIÓN")
    clase_cabecera = "class:titulo-rojo" if AccReg == "Eli" else "class:titulo-top"

    # 6. EL LAYOUT FINAL (Se monta cuando TODO lo anterior ya existe)
    layout_final = HSplit([
        Label(f" **** {txt_titulo} **** ", style=clase_cabecera),
        Window(height=1),
        *campos_dinamicos,
        Window(height=1),
        Msg_Err,
        Window(height=1),
        VSplit([btn_g, Window(width=5), btn_s] if AccReg in ["Cre", "Mod", "Eli"] else [btn_copy, Window(width=2), btn_email, Window(width=2), btn_s])
    ])

#***************************************************************************
    # 6. EL MOTOR (Si no hay app.run(), no verás nada)
    kb_f = KeyBindings()

    @kb_f.add('tab')    # Avanzar
    def _(event):
        event.app.layout.focus_next()

    @kb_f.add('s-tab') # Retroceder
    def _(event):
        event.app.layout.focus_previous()

    @kb_f.add('c-m', eager=True)
    def _(event):
        if AccReg == "Ver":
            do_send_email()

    @kb_f.add('c-s', eager=True)    # Ctrl + S SALIR
    def _(event):
        event.app.exit()

    @kb_f.add('c-g', eager=True)    # Ctrl + G GRABAR
    def _(event):
        if AccReg in ["Cre", "Mod"]:
            do_save()

    @kb_f.add('c-e', eager=True)    # Ctrl + E ELIMINAR
    def _(event):
        if AccReg == "Eli":
            do_delete_step()

    @kb_f.add('insert')
    def _(event):
        """Anula la tecla Insert para que no escriba códigos extraños"""
        pass

    @kb_f.add('c-v', eager=True)    # Ctrl + V Pegar del portapapeles
    def _(event):
        """Fuerza el pegado limpio desde el portapapeles de Windows"""
        data = event.app.clipboard.get_data()
        event.current_buffer.insert_text(data.text)


    @kb_f.add('c-c')    # CTRL + C (Copiar o Salida de emergencia)
    def _(event):
        buffer = event.current_buffer
        if buffer.selection_state:
            data = buffer.copy_selection()
            event.app.clipboard.set_data(data)
        else:
            if AccReg == "Ver":
                do_copy_clipboard()
            else:
                event.app.exit("Sal")

    app = Application(
        layout=Layout(layout_final),
        key_bindings=kb_f,
        style=estilo_yos,
        mouse_support=True,
        full_screen=True,
        erase_when_done=True,
        clipboard=PyperclipClipboard(),
    )

    Sal_boton=app.run() # ESTO bloquea la pantalla y muestra la interfaz azul/gris

    if res["save"]:
        return {n: w.text for n, w in inputs_dic.items()}
    return Sal_boton

def click_handler_fila(reg_val, btn_foco):
    def _on_mouse(mouse_event):
        if mouse_event.event_type == MouseEventType.MOUSE_DOWN:
            global fila_resaltada
            fila_resaltada = reg_val # Guardamos el ID pinchado

            # Salimos de la aplicación actual para que el bucle principal
            # de Idd_TabMod vuelva a pasar por la línea 649 (donde se calcula el bg)
            get_app().exit()
    return _on_mouse

# =============================================================================
# FUNCION PRINCIPAL
# =============================================================================
def Idd_TabMst(Fnc_Svr, Fnc_Tab, Fnc_Ord=None, Fnc_Brw=None, Fnc_ClmMod=None):
    global usuario_actual, nLin, offset, fila_resaltada, MARGEN
    global Mem_Dbt_Svr, Mem_Tab_Nom, Mem_Tab_Brw, Mem_Tab_Ord, Mem_Tab_ClmMod, Mem_Tab_ClmMod_Def, order_by_col, Mem_Ftr
    global Mem_Svr, Mem_Tab

    # 2. Asignamos el valor de los parámetros a las globales
    Mem_Svr = Fnc_Svr
    Mem_Tab = Fnc_Tab

    Err_CalFra = inspect.stack()[1]
    Err_Ach = os.path.basename(Err_CalFra.filename)
    Err_Lin = Err_CalFra.lineno
    Err_Fnc = Err_CalFra.function
    if Err_Fnc == '<module>':
        Err_Fnc = "Nivel Principal (Main)"

    if not Fnc_Svr:
        print_formatted_text(HTML(f"<ansired>Idd_Tab_Dat(Fnc_Svr, Fnc_Tab) Fnc_Svr=Servidor es Obligatorio ({Err_Fnc} {Err_Ach} - {Err_Lin})</ansired>"))
        prompt(HTML(f"<ansigreen>Cualquier tecla para salir...</ansigreen>"))
        return None

    if not Fnc_Tab:
        print_formatted_text(HTML(f"<ansired>Idd_Tab_Dat(Fnc_Svr, Fnc_Tab) Fnc_Tab=Tabla es Obligatoria ({Err_Fnc} {Err_Ach} - {Err_Lin})</ansired>"))
        prompt(HTML(f"<ansigreen>Cualquier tecla para salir...</ansigreen>"))
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

    if Mem_Tab_Brw[0][0] != "ID":
        Mem_Tab_Brw.insert(0, ("ID", "2", None))
    idx_ord = 0
    order_by_col = " " + Mem_Tab_Ord[idx_ord][1]
    pad = " " * MARGEN

    while True:
        anchos = obtener_anchos_reales()
        anchos[0]= 8 # Es el nuevo Ancho con los Botones V,M,E
        ancho_linea = sum(anchos) + (len(anchos) * 3) + 6 # +12 para los botones M/E _v_ _m_ _e_
        Mem_Cur_YosCfg.execute(f"PRAGMA table_info({Mem_Tab_Nom})")
        db_col_names = [col[1] for col in Mem_Cur_YosCfg.fetchall()]

        where_ftr = f"WHERE {order_by_col} LIKE ?" if Mem_Ftr else ""
        params_filtro = (f"%{Mem_Ftr}%",) if Mem_Ftr else ()
        Mem_Cur_YosCfg.execute(f"SELECT COUNT(*) FROM {Mem_Tab_Nom} {where_ftr}", params_filtro)
        total_regs = Mem_Cur_YosCfg.fetchone()[0]
        Mem_Cur_YosCfg.execute(f"SELECT rowid, *, ({order_by_col}) as ord_val FROM {Mem_Tab_Nom} {where_ftr} ORDER BY {order_by_col} COLLATE NOCASE LIMIT {nLin} OFFSET {offset}", params_filtro)
        registros = Mem_Cur_YosCfg.fetchall()

        pag_actual = (offset // nLin) + 1
        total_paginas = (total_regs + nLin - 1) // nLin if total_regs > 0 else 1

        etiqueta_orden = next((o[0] for o in Mem_Tab_Ord if o[1] == order_by_col), order_by_col)
        Mem_Tit_Ftr = ""
        if Mem_Ftr:
            Mem_Tit_Ftr = f"<ansicyan>Filtro : </ansicyan><ansired>{Mem_Ftr} </ansired>"

        cabecera_titulo = f"<ansicyan>TABLA : </ansicyan><ansiwhite>{Fnc_Svr} -> {Mem_Tab_Nom}</ansiwhite><ansicyan> | Orden : </ansicyan><ansiyellow>{etiqueta_orden} </ansiyellow>{Mem_Tit_Ftr}<ansicyan>| Reg : </ansicyan><ansiwhite>{offset+1}/{total_regs}</ansiwhite><ansicyan> | Pag : </ansicyan><ansiwhite>{pag_actual}/{total_paginas}</ansiwhite><ansicyan> | Lineas Browse : </ansicyan><ansiwhite>{nLin}</ansiwhite>\n"

        def b(d, t): return f"<ansiwhite>{d} </ansiwhite><ansiyellow>({t})</ansiyellow> "
        SEP = f"<ansiblue>|</ansiblue> "
        menu_comandos1 = f"{b(' Ayuda','F2')}{SEP}{b('Primero','P')}{b('Retroceder','R')}{b('Avanzar','A')}{b('Ultimo','U')}{SEP}{b('Orden','O')}{b('Buscar','B')}{b('Filtro','F')}{SEP}{b('Lineas Browse','L')}"
        menu_comandos2 = f"{b(' Salir','S')} {SEP}{b('Crear','C')}{b('Ver','nn,V')}{b('Modificar','nn,M')}{b('Eliminar','nn,E')}"

        header_cols = "".join([f"<ansiwhite>{pad}{c[0].ljust(anchos[i])}{pad}</ansiwhite><ansiblue>|</ansiblue>" for i, c in enumerate(Mem_Tab_Brw)])

        anchos[0] = 2

        # Variables de estado para prompt_toolkit
        accion_solicitada = None
        registro_afectado = None
        input_manual = [""]  # Lista mutable para capturar input

        def hacer_click_handler(accion, reg):
            def handler():
                nonlocal accion_solicitada, registro_afectado
                accion_solicitada = accion
                registro_afectado = reg
                app.exit()
            return handler

        def crear_boton(texto, handler):
            btn = Button(text=texto, handler=handler, width=3)
            btn.left_symbol = ""
            btn.right_symbol = ""
            return btn

        filas_widgets = []
        for idx, r in enumerate(registros):
            n_pan = str(idx + 1).zfill(2)

            es_la_fila = (fila_resaltada is not None and str(r[-1]) == str(fila_resaltada))
            bg = "<ansibgyellow>" if es_la_fila else ""

            ebg = "</ansibgyellow>" if (fila_resaltada and str(r[-1]).upper() == str(fila_resaltada).upper()) else ""
            fg1 = "<ansiwhite>" if bg else "<ansiyellow>"
            efg1 = "</ansiwhite>" if bg else "</ansiyellow>"
            fg2 = "<ansiwhite>" if bg else "<ansicyan>"
            efg2 = "</ansiwhite>" if bg else "</ansicyan>"

            linea = f"{bg}{fg1}{pad}{n_pan.ljust(anchos[0])}{pad}{efg1}{ebg}<ansiblue>|</ansiblue>"
            for i in range(1, len(Mem_Tab_Brw)):
                idx_bd = db_col_names.index(Mem_Tab_Brw[i][2]) + 1 if Mem_Tab_Brw[i][2] else 0
                txt_v = str(r[idx_bd] if idx_bd > 0 and r[idx_bd] is not None else "")[:anchos[i]].ljust(anchos[i])
                linea += f"{bg}{fg2}{pad}{txt_v}{pad}{efg2}{ebg}<ansiblue>|</ansiblue>"

            # Botones V, M, E con handlers funcionales
            btn_v = crear_boton("V", hacer_click_handler("V", r))
            btn_m = crear_boton("M", hacer_click_handler("M", r))
            btn_e = crear_boton("E", hacer_click_handler("E", r))

            # 1. Creamos el control de texto
            control_texto = FormattedTextControl(HTML(linea))

            # 2. Le asignamos el manejador de ratón directamente al objeto
            control_texto.mouse_handler = click_handler_fila(r[-1], btn_v)

            fila_contenedor = VSplit([
                btn_v,
                Window(width=1, char=""),
                btn_m,
                Window(width=1, char=""),
                btn_e,
                Window(width=1, char=""),
#                Window(FormattedTextControl(HTML(linea)))
                Window(content=control_texto)
            ])
            filas_widgets.append(fila_contenedor)

        # Input manual para comandos de teclado
        input_buffer = Buffer(multiline=False)

        def aceptar_input(buff):
            input_manual[0] = buff.text.strip().upper()
            app.exit()
            return True
##################################################################################################
        # ============ SISTEMA DE AYUDA F2 ============
        from prompt_toolkit.filters import Condition

        estado_ayuda = {"visible": False}

        @Condition
        def is_help_visible():
            return estado_ayuda["visible"]

        def ocultar_ayuda():
            estado_ayuda["visible"] = False

        Mem_F2 = """CONTROLES DE NAVEGACIÓN:

[Letras]      : Salir, Primero, Retroceder, Avanzar, Último
[O]rden       : Cambiar ordenamiento de la lista
[B]uscar      : Búsqueda incremental en el campo ordenado
[F]iltro      : Filtrar registros por texto
[L]íneas      : Cambiar cantidad de líneas mostradas

ACCIONES SOBRE REGISTROS:
[C]rear       : Crear nuevo registro
[nn,V]er      : Ver registro número nn
[nn,M]odificar: Modificar registro número nn
[nn,E]liminar : Eliminar registro número nn

TECLAS ESPECIALES:
[Enter]       : Aceptar / Activar botón seleccionado
[Tab]         : Mover foco al siguiente elemento
[Shift+Tab]   : Mover foco al elemento anterior
[PageUp]      : Retroceder página completa
[PageDown]    : Avanzar página completa
[F2]          : Mostrar esta ayuda
[Esc]         : Salir de la ayuda o del formulario"""

        Mem_F2_WX = 60
        Mem_F2_HY = 22

        txt_ayuda = TextArea(
            text=Mem_F2,
            multiline=True,
            read_only=True,
            scrollbar=True,
            focusable=True,
            width=Mem_F2_WX,
            height=Mem_F2_HY,
            style="fg:ansiwhite bg:black"
        )

        btn_cerrar_ayuda = Button(" CERRAR [Esc] ", handler=ocultar_ayuda, width=14)
        btn_cerrar_ayuda.left_symbol = ""; btn_cerrar_ayuda.right_symbol = ""

        marco_ayuda = Frame(
            body=HSplit([
                Window(height=1),
                txt_ayuda,
                Window(height=1),
                VSplit([Window(), btn_cerrar_ayuda, Window()])
            ]),
            title=HTML("<b><ansiyellow>*** AYUDA DEL SISTEMA ***</ansiyellow></b>"),
            style="fg:ansicyan bg:black"
        )

        ayuda_float = Float(
            content=ConditionalContainer(content=marco_ayuda, filter=is_help_visible),
            transparent=False
        )
        # ============ FIN SISTEMA AYUDA ============
#############################################################################################
        area_input = VSplit([
#            Window(FormattedTextControl(HTML("<orange>  Seleccione Opción : </ansiyellow>")), width=23),
            Window(FormattedTextControl(HTML("<orange>  Seleccione Opción : </orange>")), width=23),
            Window(content=BufferControl(buffer=input_buffer, focusable=True), width=5)
        ])
        input_buffer.accept_handler = aceptar_input
#########################################################
        from prompt_toolkit.layout.containers import FloatContainer

        contenido_base = HSplit([
            Window(FormattedTextControl(HTML(cabecera_titulo)), height=2),
            Window(FormattedTextControl(HTML(menu_comandos1)), height=1),
            Window(FormattedTextControl(HTML(menu_comandos2)), height=2),
            Window(FormattedTextControl(HTML(f"      {header_cols}")), height=1),
            Window(FormattedTextControl(HTML(f"<ansiblue>{'═' * ancho_linea}</ansiblue>")), height=1),
            *filas_widgets,
            Window(FormattedTextControl(HTML(f"<ansiblue>{'═' * ancho_linea}</ansiblue>")), height=1),
            area_input
        ])

        contenido_principal = FloatContainer(
            content=contenido_base,
            floats=[ayuda_float]
        )
#########################################################################################
#        contenido_principal = HSplit([
#            Window(FormattedTextControl(HTML(cabecera_titulo)), height=2),
#            Window(FormattedTextControl(HTML(menu_comandos1)), height=1),
#            Window(FormattedTextControl(HTML(menu_comandos2)), height=2),
#            Window(FormattedTextControl(HTML(f"      {header_cols}")), height=1),
#            Window(FormattedTextControl(HTML(f"<ansiblue>{'═' * ancho_linea}</ansiblue>")), height=1),
#            *filas_widgets,
#            Window(FormattedTextControl(HTML(f"<ansiblue>{'═' * ancho_linea}</ansiblue>")), height=1),
#            area_input
#        ])

        # KeyBindings (atajos de teclado)
        kb = KeyBindings()

       # ============ TECLAS DE AYUDA (solo cuando ayuda visible) ============
        @kb.add('f2')
        def _(event):
            estado_ayuda["visible"] = True
            event.app.layout.focus(txt_ayuda)

        @kb.add('escape')
        def _(event):
            if estado_ayuda["visible"]:
                estado_ayuda["visible"] = False
                event.app.layout.focus(input_buffer)
            else:
                event.app.exit(result=False)

        @kb.add('tab', filter=is_help_visible)
        def _(event):
            if event.app.layout.has_focus(txt_ayuda):
                event.app.layout.focus(btn_cerrar_ayuda)
            else:
                event.app.layout.focus(txt_ayuda)

        @kb.add('s-tab', filter=is_help_visible)
        def _(event):
            if event.app.layout.has_focus(btn_cerrar_ayuda):
                event.app.layout.focus(txt_ayuda)
            else:
                event.app.layout.focus(btn_cerrar_ayuda)

        @kb.add('pageup', filter=is_help_visible)
        def _(event):
            for _ in range(10):
                txt_ayuda.buffer.cursor_up()

        @kb.add('pagedown', filter=is_help_visible)
        def _(event):
            for _ in range(10):
                txt_ayuda.buffer.cursor_down()
        # ============ FIN TECLAS AYUDA ============

        @kb.add("pageup", filter=~is_help_visible)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "PAGEUP"
            event.app.exit()

        @kb.add("pagedown", filter=~is_help_visible)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "PAGEDOWN"
            event.app.exit()

        @kb.add("s", eager=True, filter=~is_help_visible)
        @kb.add("S", eager=True, filter=~is_help_visible)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "S"
            event.app.exit()

        @kb.add("p", eager=True)
        @kb.add("P", eager=True)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "P"
            event.app.exit()

        @kb.add("r", eager=True)
        @kb.add("R", eager=True)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "R"
            event.app.exit()

        @kb.add("a", eager=True)
        @kb.add("A", eager=True)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "A"
            event.app.exit()

        @kb.add("u", eager=True)
        @kb.add("U", eager=True)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "U"
            event.app.exit()

        @kb.add("c", eager=True)
        @kb.add("C", eager=True)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "C"
            event.app.exit()

        @kb.add("b", eager=True)
        @kb.add("B", eager=True)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "B"
            event.app.exit()

        @kb.add("l", eager=True)
        @kb.add("L", eager=True)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "LB"
            event.app.exit()

        @kb.add("o", eager=True)
        @kb.add("O", eager=True)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "ORD"
            event.app.exit()

        @kb.add("f", eager=True)
        @kb.add("F", eager=True)
        def _(event):
            nonlocal accion_solicitada
            accion_solicitada = "FTR"
            event.app.exit()

        # Teclas de navegación entre botones
        @kb.add("tab", filter=~is_help_visible)  # ← FILTRO AGREGADO
        def focus_next(event):
            event.app.layout.focus_next()

        @kb.add("s-tab", filter=~is_help_visible)  # ← FILTRO AGREGADO
        def focus_previous(event):
            event.app.layout.focus_previous()

        @kb.add("down", filter=~is_help_visible)  # ← FILTRO AGREGADO
        def focus_down(event):
            event.app.layout.focus_next()

        @kb.add("up", filter=~is_help_visible)  # ← FILTRO AGREGADO
        def focus_up(event):
            event.app.layout.focus_previous()

        @kb.add("enter", filter=~is_help_visible)  # ← FILTRO AGREGADO
        def enter_pressed(event):
            if event.app.layout.has_focus(input_buffer):
                aceptar_input(input_buffer)

        estilo_app = PtStyle([
            ("button", "fg:white bg:#0000aa"),
            ("button.focused", "fg:white bg:#00aa00 bold"),
            ("text-area", "bg:#333333 fg:white"),
        ])

        app = Application(
            layout=Layout(contenido_principal),
            key_bindings=kb,
            mouse_support=True,
            style=estilo_app,
            full_screen=True,
            erase_when_done=True
        )

        # Foco inicial en el input
        # Si acabamos de pinchar una fila, buscamos su botón V para darle el foco
        boton_a_enfocar = input_buffer
        if fila_resaltada:
            # Buscamos en nuestros widgets cuál coincide con la fila resaltada
            for idx, r in enumerate(registros):
                if str(r[-1]) == str(fila_resaltada):
                    # El primer elemento de nuestro VSplit es btn_v
                    boton_a_enfocar = filas_widgets[idx].children[0].content
                    break

        app.layout.focus(boton_a_enfocar)
#        app.layout.focus(input_buffer)

        app.run()
        os.system('cls')

        # Procesar resultado
        cmd = accion_solicitada if accion_solicitada else input_manual[0]
        reg_sel = registro_afectado

        if not cmd:
            continue

        # Procesar comandos
        if cmd == 'S':
            break
        elif cmd == 'PAGEUP':  # <-- AQUÍ PROCESAS PAGEUP
            offset = max(0, offset - nLin)
        elif cmd == 'PAGEDOWN':  # <-- AQUÍ PROCESAS PAGEDOWN
            offset = min(offset + nLin, max(0, ((total_regs-1)//nLin)*nLin))
        elif cmd == 'LB':
            os.system('cls')
            nueva_lin = prompt(HTML(f"<orange> Lineas Browse ({nLin}) : </orange>")).strip()
            if nueva_lin.isdigit():
                val_num = int(nueva_lin)
                if val_num > 0:
                    nLin = val_num
                    offset = 0
        elif cmd == 'P':
            offset = 0
        elif cmd == 'A':
            offset = min(offset + nLin, max(0, ((total_regs-1)//nLin)*nLin))
        elif cmd == 'R':
            offset = max(0, offset - nLin)
        elif cmd == 'U':
            offset = max(0, ((total_regs - 1) // nLin) * nLin)
        elif cmd == 'ORD':
            if Mem_Tab_Ord:
                os.system('cls')
                print_formatted_text(HTML(f"\n   <green>SELECCIONE ORDEN:</green>"))
                for i, o in enumerate(Mem_Tab_Ord):
                    print_formatted_text(HTML(f"   <ansigreen>{i+1}</ansigreen> <ansiwhite>{o[0]}</ansiwhite>"))
                op_ord = prompt(HTML(f"   <ansiyellow>Opción: </ansiyellow>"))
                if op_ord.isdigit() and 1 <= int(op_ord) <= len(Mem_Tab_Ord):
                    idx_ord = int(op_ord) - 1
                    order_by_col = Mem_Tab_Ord[idx_ord][1]
                    offset = 0
        elif cmd == 'B':
            busqueda_incremental_dinamica(Mem_Cnx_YosCfg, db_col_names, anchos)
        elif cmd == 'FTR':
            os.system('cls')
            Mem_Ftr = prompt(HTML(f"<ansiyellow> Filtro por {etiqueta_orden} : </ansiyellow>")).strip()
            offset = 0
        elif cmd == 'C':
            reg_nuevo = formulario_yos(db_col_names, "" ,AccReg="Cre")
            if isinstance(reg_nuevo, dict):
                reg_nuevo['cModRegNik'] = usuario_actual
                reg_nuevo['cModRegTim'] = Yos_TimeStamp()
                insert_data = {k: v for k, v in reg_nuevo.items() if k != "nAutInc"}
                cols = ", ".join(insert_data.keys())

                pls = ", ".join(["?"] * len(insert_data))
                Mem_Cur_YosCfg.execute(f"INSERT INTO {Mem_Tab_Nom} ({cols}) VALUES ({pls})", list(insert_data.values()))
                Mem_Cnx_YosCfg.commit()
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
                    Mem_Cur_YosCfg.execute(f"UPDATE {Mem_Tab_Nom} SET {set_sql} WHERE rowid=?", valores)
                    Mem_Cnx_YosCfg.commit()
        elif cmd == 'E' and reg_sel:
            dato=formulario_yos(db_col_names, reg_sel, AccReg="Eli")
            if dato == "Borrar":
#                print_formatted_text(HTML(f" \n   <ansibgred><ansiorange>¿ ELIMINAR ESTE REGISTRO ? (S/N) </ansiorange></ansibgred>"))
#                if msvcrt.getch().upper() == b'S':
                    Mem_Cur_YosCfg.execute(f"DELETE FROM {Mem_Tab_Nom} WHERE rowid=?", (reg_sel[0],))
                    Mem_Cnx_YosCfg.commit()
        elif ',' in cmd:
            try:
                partes = cmd.split(',')
                idx_p = int(partes[0]) - 1
                accion = partes[1].upper()
                if 0 <= idx_p < len(registros):
                    reg_sel = registros[idx_p]
                    if accion == 'V':
                        res_ver = formulario_yos(db_col_names, reg_sel, AccReg="Ver")
                        if isinstance(res_ver, tuple) and res_ver[0] == "Email":
                            from Yos.YosLib import EmlEnv
                            EmlEnv("", f"Ficha: {res_ver[1]}", res_ver[2])
                    elif accion == 'M':
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
                                Mem_Cur_YosCfg.execute(f"UPDATE {Mem_Tab_Nom} SET {set_sql} WHERE rowid=?", valores)
                                Mem_Cnx_YosCfg.commit()
                    elif accion == 'E':
                        dato=formulario_yos(db_col_names, reg_sel, AccReg="Eli")
                        if dato== "Borrar":
#                            print_formatted_text(HTML(f" \n   <ansibgred><ansiorange>¿ ELIMINAR ESTE REGISTRO ? (S/N) </ansiorange></ansibgred>"))
#                            if msvcrt.getch().upper() == b'S':
                                Mem_Cur_YosCfg.execute(f"DELETE FROM {Mem_Tab_Nom} WHERE rowid=?", (reg_sel[0],))
                                Mem_Cnx_YosCfg.commit()
            except Exception as e:
                print_formatted_text(HTML(f"<ansired>Error: {e}</ansired>"))
                msvcrt.getch()

    Mem_Cnx_YosCfg.close()

# =============================================================================
# INICIO DEL SISTEMA
# =============================================================================
if __name__ == "__main__":
    Mem_Dbt = "YosCfg"
    Mem_Tab = "Mnu"
    Idd_TabMst(Mem_Dbt, Mem_Tab)
