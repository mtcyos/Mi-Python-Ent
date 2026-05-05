#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Miguel Tortosa

Yos_Ges_Frm.py  .Py donde estan todas las Def _Frm

Gestión Definiciones Frm, para el entorno Gui con base en nicegui

Tanto para Local (Loc) como Web (Www)

Estructura nombre Def

PREFIJOS    DESCRIPCION
Yos_        Def de uso General
Idd_        Def de gestion de las bases de datos
Apl_        Def de gestion de las Aplicación (Como contrl de Acceso)

SUFIJO
_Frm -> Modo Grafico -> GUI/Web

"""

#   print(f"{inspect.currentframe().f_lineno}")

import os
import sqlite3
import builtins

from Yos import Yos_ClipCopy

from nicegui import ui, app

################################################################### Inicio Def ##########################################################
def Yos_DefFrm_Frm(Fnc_Mnu, finalizar_fnc, Fnc_Img = None, Fnc_Tit_1 = None, Fnc_Tit_2 = None, Fnc_Tit_3 = None):
    # Define la pantalla con Menu

    if not Fnc_Img:
        Fnc_Img = "Log_01.png"

    if not Fnc_Tit_1:
        Fnc_Tit_1 = YosCfg.get("Apl_Apl", "Err : YosCfg.Apl_Apl")

    if not Fnc_Tit_2:
        Fnc_Tit_2 = YosCfg.get("Apl_Nom", "Err : YosCfg.Apl_Nom")

    if not Fnc_Tit_3:
        Fnc_Tit_3 = f'{YosCfg.get("Apl_Cpy", "Err : YosCfg.Apl_Cpy")} - {YosCfg.get("Apl_CpyEml", "Err : YosCfg.Apl_CpyEml")}'

    ui.add_head_html('''
        <style>
            main {
                margin-top: 0 !important;
                padding-top: 0 !important;
            }
            .nicegui-content {
                padding: 0 !important;
            }

            body {
                margin: 0 !important;    /* Asegura que el cuerpo no tenga márgenes */
                background-color: #f0f2f5;
                font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }

            /* 2. COMPONENTES (Botones y Menús) */
            .q-btn { font-size: 0.75rem !important; }
            .q-item { font-size: 0.75rem !important; min-height: 24px !important; }
            .menu-parent:hover x> .q-menu { display: block !important; }

            /* 3. ESTILO PARA LA RAYITA PEQUEÑA (HMG) */
            .hmg-separator {
                margin: 4px auto !important;
                width: 90% !important;
                background-color: #d1d5db !important;
                min-height: 1px !important;
            }

            /* 4. ESTILO CONSOLA PARA NOTICIAS (Opcional) */
            .noticias-texto {
                font-family: "Consolas", "Monaco", monospace !important;
            }
        </style>
    ''')

    # --- LÓGICA DE GENERACIÓN (Tuya Original) ---
    def generar_items(diccionario):
        for clave in sorted(diccionario.keys()):
            valor = diccionario[clave]
            texto = valor.get("Txt", "")
            comando = valor.get("Fnc", "")
            codigo = valor.get("Cod", "")

            if comando == "YosAppSld":  # opcion de Salir

                if YosCfg.get("Apl_Etn") =="Loc": # Local
                    texto ="SALIR DE LA APLICACION"

                if YosCfg.get("Apl_Etn") =="Www": # Web
                    if YosCfg.get("Apl_UsrAcc") == "S": # Control de usuarios
                        texto ="CERRAR SESION"
                    else: # SIN Control de usuarios
                        continue
#                        texto ="CERRAR SESION"

            if codigo == "Sep" or (not texto and not comando):
                ui.separator().classes('hmg-separator')
                continue

            clase_item = 'text-xs min-h-[24px] py-0 px-3'

            if "Sub" in valor and isinstance(valor["Sub"], dict):
                with ui.item().props('clickable').classes(clase_item + ' items-center').style('min-height: 25px; height: 25px;'):
                    ui.label(f"{texto}").classes('flex-grow')
                    ui.icon('chevron_right', size='xs').classes('ml-2')
#                with ui.item().props('clickable').classes(clase_item):
#                    ui.label(f"{texto}").classes('flex-grow')
#                    ui.icon('chevron_right', size='xs').classes('ml-2')

                    with ui.menu().props('anchor="top right" self="top left"').classes('bg-white border border-gray-400'):
                        generar_items(valor["Sub"])
            else:
                ui.menu_item(texto, on_click=lambda f=comando: finalizar_fnc(f)).classes(clase_item)

    # --- CABECERA REAL (ANCLADA PARA ACTUALIZACIÓN) ---
    # Guardamos la referencia de la fila para poder retornarla
    barra_menu = ui.row().classes('w-full bg-slate-200 p-0 gap-0 border-b border-gray-400 items-center')

    def dibujar_botones(datos_menu):
        with barra_menu:
            for clave in sorted(datos_menu.keys()):
                valor = datos_menu[clave]
                texto = valor.get("Txt", "Sin nombre")
                with ui.button(texto).props('flat color=black').classes('text-xs font-bold min-h-[24px] py-0 px-3 rounded-none hover:bg-slate-300'):
                    if "Sub" in valor:
                        with ui.menu().classes('bg-white border border-gray-400'):
                            generar_items(valor["Sub"])

    # Primera carga
    dibujar_botones(Fnc_Mnu)

    # --- BLOQUE DE LOGO CENTRAL (Tu diseño intacto) ---
    with ui.column().classes('w-full items-center q-pa-md gap-0'):
        ruta_limpia = os.path.join(YosCfg["Apl_Dir"], 'Img', Fnc_Img)
        ui.image(ruta_limpia).style('width: 100px; margin-top: -10px;')
        ui.label(Fnc_Tit_1).classes('text-h4 font-bold q-my-none').style('line-height: 1;')
        ui.label(Fnc_Tit_2).classes('text-h5 font-normal q-my-none').style('line-height: 1;')
        ui.label(Fnc_Tit_3).classes('text-h6 font-normal q-my-none').style('line-height: 1;')

    if YosCfg["Apl_Not"] == "S":
        Yos_DefFrm_NotBrw_Frm()

    barra_menu.refrescar = lambda nuevos_datos: dibujar_botones(nuevos_datos)

    return barra_menu

def Yos_DefFrm_Mnu_Frm(diccionario, finalizar_fnc):
    """Procesa el diccionario y dibuja los items/submenús"""
    for clave in sorted(diccionario.keys()):
        valor = diccionario[clave]
        texto = valor.get("Txt", "")
        comando = valor.get("Fnc", "")
        codigo = valor.get("Cod", "")

        # Lógica de seguridad para entorno Web
        if YosCfg.get("Apl_UsrAcc") != "S" and YosCfg.get("Apl_Etn") == "Www" and comando == "YosAppSld":
            continue
        if YosCfg.get("Apl_UsrAcc") != "S" and comando == "YosAppSld":
            texto = "SALIR DE LA APLICACION"

        # Detección de Separador
        if codigo == "Sep" or (not texto and not comando):
            ui.separator()
            continue

        clase_item = 'text-xs min-h-[24px] py-0 px-3'

        if "Sub" in valor and isinstance(valor["Sub"], dict):
            with ui.item().props('clickable').classes(clase_item):
                ui.label(f"{texto}").classes('flex-grow')
                ui.icon('chevron_right', size='xs').classes('ml-2')
                with ui.menu().props('anchor="top right" self="top left"').classes('bg-white border border-gray-400'):
                    Yos_DefFrm_Mnu_Frm(valor["Sub"], finalizar_fnc) # Recursividad
        else:
            ui.menu_item(texto, on_click=lambda f=comando: finalizar_fnc(f)).classes(clase_item)

def Yos_DefFrm_NotBrw_Frm():
    # 1. RENDERIZADO (ANCHO 99% BLOQUEADO)
    with ui.column().classes('w-full items-center no-wrap q-pa-none q-mt-xl').style('height: calc(100vh - 360px);'):

        with ui.card().classes('p-0 gap-0 shadow-0').style('width: 99%; height: 100%; border: 1px solid #333; border-radius: 0px;'):

            # Cabecera técnica
            with ui.row().classes('w-full q-px-sm bg-grey-4 items-center border-b').style('height: 28px;'):
                ui.icon('list', size='16px').classes('text-black')
                ui.label('NOTICIAS').style('font-size: 0.75rem;').classes('text-bold text-black')

            # Área de scroll
            with ui.scroll_area().classes('w-full').style('height: calc(100% - 28px); background: #fff;'):
                lista_noticias = ui.column().classes('w-full gap-0 q-pa-none')

    def refrescar_datos():
        noticias = []
        db_path = os.path.join(builtins.YosCfg["Apl_Dir"], '_Bdt', 'Dbt', 'YosNot.db')

        try:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                # Ajustamos la SELECT al nuevo orden: TIPO, FECHA, DETALLE, DESCRIPCION
                cursor.execute("SELECT TIPO, FECHA, DETALLE, DESCRIPCION FROM Noticias ORDER BY FECHA DESC LIMIT 20")
                noticias = cursor.fetchall()
                conn.close()
            else:
                noticias = [("Err", "ATENCION", "Sistema", f"NO SE PUDO ACCEDER A {db_path}", "Compruebe la ruta de la DB.")]
        except Exception as e:
            noticias = [("Err", "ATENCION", "Sistema", f"Error en Yos_DefFrm_NotBrw_Frm : {e}", "Compruebe la ruta de la DB.")]

        noticias += [
            ("Inf", "21/04/2026", "mtcyos", "Sistema YosCtr iniciado correctamente en entorno Web.", "DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR DESCRIPCION LARGA A MOSTRAR "),
            ("Err", "21/04/2026", "mtcyos", "Error de conexión detectado en el módulo de respaldos SQLite.", "DESCRIPCION LARGA A MOSTRAR"),
            ("Sis", "25/04/2026", "mtcyos", "Nueva actualización de la librería Yos_Ges_Frm disponible.", "DESCRIPCION LARGA A MOSTRAR"),
            ("Inf", "25/04/2026", "mtcyos", "Aviso: Se realizará un mantenimiento programado del servidor NAS.", "DESCRIPCION LARGA A MOSTRAR"),
            ("Sis", "21/08/2026", "mtcyos", "El usuario mtcyos ha actualizado los permisos.", ""),
        ]

        lista_noticias.clear()
        with lista_noticias:
            # APLICAMOS EL CAMBIO DE ORDEN AQUÍ:
            for tipo, fecha, usuario, titular, texto in noticias:
                color_hex = '#1976d2' if tipo == 'Inf' else '#c10015' if tipo == 'Err' else '#000'

                fila = ui.row().classes('w-full items-center no-wrap border-b border-grey-1 gap-0 p-0').style('min-height: 22px; cursor: pointer;')

                with fila:
                    ui.label(f' {fecha}').classes('shrink-0 q-pa-none q-ma-none').style(
                        f'color: {color_hex}; font-family: monospace; font-size: 0.8rem; width: 80px; margin-left: 0px;'
                    )
                    ui.label(f'{titular}').classes('truncate q-pa-none q-ma-none').style(
                        f'color: {color_hex}; font-size: 0.85rem; margin-left: 0px;'
                    )

                # Evento para mostrar 'texto' (la descripción)


                # --- EVENTO CLICK PARA MOSTRAR DETALLE ---
                def mostrar_detalle(Fnc_Fec=fecha, Fnc_Tit=titular, Fnc_Txt=texto, Fnc_Usr=usuario):
                    # RESTRICCIÓN: Si no hay texto largo, no hacemos nada
                    if not Fnc_Txt or not Fnc_Txt.strip():
                        return

                    # Si hay texto, abrimos el diálogo
                    with ui.dialog() as dialog, ui.card().classes('q-pa-md').style('min-width: 550px; border: 1px solid #333; border-radius: 0px;'):
                        dialog.props('persistent') # YA NO se cierra al clicar fuera

                        # Cabecera con botón de copiado integral
                        with ui.row().classes('w-full items-center justify-between border-b q-mb-sm'):
                            ui.label(f'NOTICIA - FECHA FIN {Fnc_Fec}').classes('text-bold uppercase').style('user-select: text;')

                            # Bloque de texto para tu función Yos_ClipCopy
                            bloque_info = f"{YosCfg["Apl_Nom"]} - NOTICIA\n\nFECHA FIN : {Fnc_Fec}\nTITULO : {Fnc_Tit}\nNOTICIA : {Fnc_Txt}\nAUTOR : {Fnc_Usr}"
                            ui.button(icon='content_copy', on_click=lambda: Yos_ClipCopy(bloque_info)) \
                                .props('flat round dense size=sm').classes('text-blue-600') \
                                .tooltip('Copiar al PortaPapeles')

                        # Titular (Copiable)
                        ui.label(Fnc_Tit).classes('text-subtitle2 q-mb-sm font-bold').style('user-select: text;')

                        ui.separator().classes('q-my-sm')

                        # Descripción larga (Copiable)
                        ui.label(Fnc_Txt).classes('text-body2 q-mb-md').style('user-select: text;')

                        # Pie: Usuario y Cerrar
                        with ui.row().classes('w-full items-center justify-between border-t q-pt-sm q-mt-sm'):
                            ui.label(f'Creada por : {Fnc_Usr}').classes('text-caption text-grey-7 italic').style('user-select: text;')
                            ui.button('CERRAR', on_click=dialog.close).props('flat').classes('text-blue-500 font-bold')

                    dialog.open()

                    print(f'{Yos.Yos_TimeStamp()} -> {YosSes["Usr_Ipd"]} - {YosSes["Usr_Nik"]} : VE NOTICIA {Fnc_Tit}')

                # Asignamos el evento a la fila
                fila.on('click', mostrar_detalle)

    refrescar_datos()

    ui.timer(60.0, lambda: refrescar_datos())

def Yos_DefFrm_BarEst_Frm():
    import builtins
    with ui.footer(fixed=True).classes('bg-grey-3 text-black items-center py-1 px-4 border-t'):
# YosCfg["Usr_Nik"] = app.storage.user.get('nick', '') # Usuario
# YosCfg["Usr_Pas"] = password.value # Contraseña en md5
# YosCfg["Usr_Niv"] = "99" # Nivel del Usuario
# YosCfg["Usr_Ipd"] = user_ip # Direccion Ip del usuario
        usr_actual = YosSes.get('Usr_Nik')
        if usr_actual == "SinUsr":
            ui.label(f'{YosSes["Usr_Nom"]}').classes('text-caption font-bold')
        elif not usr_actual and YosCfg.get("Apl_UsrAcc") == "S":
            ui.label(f'IDENTIFIQUESE').classes('text-caption font-bold')
        else:
            Mem_Tit = ""
            match YosSes["Usr_Niv"]:
                case "99":
                    Mem_Tit = "ADMINISTRADOR : "
                case _:
                    Mem_Tit = "USUARIO : "

            ui.label(f'👤 {Mem_Tit}{YosSes["Usr_Nom"]}').classes('text-caption font-bold')

def Yos_Msg_Frm(Fnc_Tit="YOS SYSTEM", Fnc_Msg="", Fnc_Tip="Inf", Ancho="450px", Alto="auto"):
    # Muestra un mensaje en pantalla
    YosCfg = builtins.YosCfg

    Fnc_TipCfg = {
        "Inf": {"img": YosCfg["Yos_Dir"] + "/Img/YosInf.png", "color": "#1976d2"},
        "Err": {"img": YosCfg["Yos_Dir"] + "/Img/YosErr.png", "color": "#c10015"},
        "Atn": {"img": YosCfg["Yos_Dir"] + "/Img/YosExc.png", "color": "#f2c037"}
    }

    if Fnc_Tip in ["Err", "Atn"]:
        Fnc_Tit = f"ATENCION : {Fnc_Tit}"

    cfg = Fnc_TipCfg.get(Fnc_Tip, Fnc_TipCfg["Inf"])
    estilo_card = f'width: {Ancho}; height: {Alto}; max-height: 95vh;'

    with ui.dialog().props('persistent') as dialog, ui.card().classes('p-0 overflow-hidden shadow-2xl').style(estilo_card):
        # Encabezado
        with ui.row().classes('w-full p-3 items-center gap-3').style(f'background-color: {cfg["color"]}'):
            ui.image(cfg["img"]).style('width: 28px; height: 28px;')
            ui.label(Fnc_Tit).classes('text-white font-bold text-md uppercase tracking-tight')

        # Cuerpo
        with ui.column().classes('pt-1 pb-1 pl-4 pr-4 w-full overflow-auto'):
            ui.html(Fnc_Msg).classes('text-gray-700 text-sm')

        # Botón de cierre
        with ui.row().classes('w-full p-0 mt-auto border-t border-gray-100'):
            ui.button('CERRAR', on_click=dialog.close).props('flat square').classes('w-full py-3 font-bold text-white').style(f'background-color: {cfg["color"]}; border-radius: 0;')

    dialog.open()

async def Yos_MsgPgt_Frm(Fnc_Tit="ATENCIÓN", Fnc_Bot="SÍ/NO", Fnc_Msg="¿ Desea Salir ?", Ancho="400px", Alto="auto"):
    # Muestra un mensaje de Opc_1/Opc_2 en pantalla
    """
    DIÁLOGO DE PREGUNTA DINÁMICO:
    Fnc_Bot="S/N" -> Botones SÍ y NO
    Fnc_Bot="Aceptar/Cancelar" -> Botones Aceptar y Cancelar

    Mem_Rpt = await Yos.Yos_MsgPgt_Frm(Fnc_Tit="TITULO", Fnc_Msg=f'MENSAJE<br><br>OTRA LINEA', Fnc_Bot="Izq/Dcho")
    if Mem_Rpt: # Pulso Boton Izquierdo
        print("Pulso Boton Izquierdo")
    else: # Pulso Boton Derecho
        print("Pulso Boton Derecho")
    """
    import builtins
    YosCfg = builtins.YosCfg

    # Extraemos los textos de los botones
    btn_textos = Fnc_Bot.split('/')
    txt_A = btn_textos[0] if len(btn_textos) > 0 else "SÍ"
    txt_B = btn_textos[1] if len(btn_textos) > 1 else "NO"

    # Configuración de color e imagen de la librería Yos
    cfg = {"img": YosCfg["Yos_Dir"] + "/Img/YosInt.png", "color": "#34495e"}
    estilo_card = f'width: {Ancho}; height: {Alto}; max-height: 95vh;'

    with ui.dialog().props('persistent') as dialog, ui.card().classes('p-0 overflow-hidden shadow-2xl').style(estilo_card):

        # 1. ENCABEZADO (Estilo YosCfg)
        with ui.row().classes('w-full p-3 items-center gap-3').style(f'background-color: {cfg["color"]}'):
            ui.image(cfg["img"]).style('width: 28px; height: 28px;')
            ui.label(Fnc_Tit).classes('text-white font-bold text-md uppercase tracking-tight')

        # 2. CUERPO (Fondo blanco)
        with ui.column().classes('p-6 w-full bg-white'):
            ui.html(Fnc_Msg).classes('text-slate-700 text-sm')

        # 3. PIE CON BOTONES DINÁMICOS
        with ui.row().classes('w-full p-0 mt-auto border-t border-gray-100 items-stretch gap-0'):
            # Botón de la izquierda (Retorna True)
            ui.button(txt_A.upper(), on_click=lambda: dialog.submit(True)) \
                .props('flat square') \
                .classes('w-1/2 py-3 font-bold text-white border-r border-white/20') \
                .style(f'background-color: {cfg["color"]}; border-radius: 0;')

            # Botón de la derecha (Retorna False)
            ui.button(txt_B.upper(), on_click=lambda: dialog.submit(False)) \
                .props('flat square') \
                .classes('w-1/2 py-3 font-bold text-white') \
                .style(f'background-color: {cfg["color"]}; border-radius: 0;')

    return await dialog
################################# A REVISAR #################################################################
from nicegui import ui

async def Yos_EntDat_Frm(**Fnc_Dic):
    from nicegui import ui
    import Yos

    # 1. Sacamos la lista de campos. Si no viene, usamos uno por defecto.
    Mem_Campos = Fnc_Dic.get("Campos", [])
    if not Mem_Campos:
        # Por seguridad, si llega vacío creamos un campo genérico
        Mem_Campos = [{"Clm": "Dato", "Rot": "Valor", "Vfy": "", "Lon": 0}]

    # Aquí guardaremos los objetos de NiceGUI para leer sus valores después
    entradas_gui = {}

    # DEFINO LA PANTALLA
    if Fnc_Dic.get("Frm") == "Max": # Maximizo la pantalla
        p_dlg = 'persistent maximized transition-show=slide-up transition-hide=slide-down'
        c_crd = 'w-full h-full p-0 no-shadow border-none rounded-none gap-0'
#        c_crd = 'w-full p-0 overflow-hidden gap-0' # Se eliminó max-w-lg
    else:
        p_dlg = 'persistent'
        c_crd = 'w-full max-w-lg p-0 overflow-hidden gap-0'

    with ui.dialog().props(p_dlg) as dialog, ui.card().classes(c_crd):
#    with ui.dialog().props(p_dlg) as dialog, ui.card().classes(c_crd).style('min-width: 95vw;'):
    # FIN DEFINO LA PANTALLA

        Acn = Fnc_Dic.get("Acn", "Ver")

        Acn_Fmt = {
            "Cre": ("#2e7d32", "Crear", "YosCre.png"),  # Verde - Crear
            "Ver": ("#1976d2", "Ver", "YosVer.png"),  # Azul  - Ver/Info
            "Mod": ("#ed6c02", "Modificar", "YosMod.png"),  # Naranja - Modificar
            "Eli": ("#d32f2f", "Eliminar", "YosEli.png")   # Rojo - Eliminar
        }

        solo_lectura = True if Acn in ["Ver", "Eli"] else False
        # --- ENCABEZADO AZUL ESTILO YOS ---
        # Color Segun Accion
        # Crear -> Verde
        # Ver -> Azul -> Por Omision
        # Modificar -> Naranja
        # Eliminar -> Rojo
        '''
        pt-0 (Padding Top): Le dice que el espacio de arriba sea 0. Por eso ahora la franja verde se pega al encabezado azul sin dejar el hueco blanco.
        pb-4 (Padding Bottom): Deja un espacio de 4 unidades (unos 16px) abajo, para que el último campo no choque con el borde de la ventana.
        pl-4 (Padding Left): Espacio a la izquierda.
        pr-4 (Padding Right): Espacio a la derecha.
        bg-green-300 -> Verde
        '''
        AcnCol, Mem_BotTxt, AcnImg = Acn_Fmt.get(Acn)
        ruta_icono = builtins.YosCfg["Yos_Dir"] + "/Img/"+AcnImg

        with ui.row().classes('w-full p-3 items-center gap-3').style(f'background-color: {AcnCol}'):
            ui.image(ruta_icono).style('width: 28px; height: 28px;')
            ui.label(Fnc_Dic.get("Tit", "INTRODUCCIÓN DE DATOS")).classes('text-white font-bold text-md uppercase tracking-tight')

        # --- CUERPO DEL FORMULARIO (Con padding p-4 para separar del borde) ---
        with ui.column().classes('pt-0 pb-4 pl-4 pr-4 w-full gap-0'):

            # BOTONERA
#           with ui.row().classes('pt-1 pb-2 pl-0 pr-0 w-full gap-0'):
#
            with ui.button_group():
                ui.button('Salir', on_click=lambda: dialog.submit({}))#.props('flat')

                async def procesar():
                    print(f"{inspect.currentframe().f_lineno}")
                    datos_validados = {}
                    # Recorremos cada campo para validarlo con el "Cerebro" Vfy
                    for campo in Mem_Campos:
                        # --- NECESARIO: Ignorar el salto para no validar un campo que no existe ---
                        if campo.get("Clm") == "SaltoDeLinea": continue

                        id_clm = campo.get("Clm")
                        obj_gui = entradas_gui[id_clm]

                        # segundo Campo de Verificacion de Pas
                        id_vfy = f"{id_clm}_Vfy"
                        if id_vfy in entradas_gui:
                            if obj_gui.value != entradas_gui[id_vfy].value:
                                lbl_error.set_text("Error : Las contraseñas no coinciden")
                                return

                        val_a_validar = obj_gui.value
                        if campo.get("Tip") == "N":
                            val_a_validar = str(val_a_validar).replace(',', '') if val_a_validar is not None else ""

                        # Llamada a la verificación individual
                        val_limpio, err = Yos.Yos_EntDat_Vfy(
                            val_a_validar,
                            campo.get("Vfy", ""),
                            campo.get("Rot", id_clm),
                            campo.get("Tip", "C"),
                            int(campo.get("Lon", 0))
                        )

                        if err:
                            lbl_error.set_text(err)
                            return # Detenemos el proceso si hay un solo error

                        # Guardamos el dato ya limpio (ej: en mayúsculas)
                        datos_validados[id_clm] = val_limpio
                    #print(f'{id_clm}={val_limpio}')

                    # Si llegamos aquí, todo está OK. Devolvemos el diccionario completo.
                    dialog.submit(datos_validados)

                if Acn != "Ver":
                    ui.button(Mem_BotTxt, on_click=procesar)

            # Mensaje de error
#            lbl_error = ui.label(' ').classes('text-red-600 text-sm font-bold w-full text-center mt-0')
            lbl_error = ui.label('').classes('text-red-600 text-sm font-bold w-full text-center mt-0 min-h-[20px]')

            # Descripcion
            ui.html(Fnc_Dic.get("Des", "")).classes('text-caption text-black mb-0')

            # GENERACIÓN DINÁMICA DE CAMPOS
            # --- MODIFICADO: Usamos una rejilla de 12 columnas para control total como en tu imagen ---
            grid_yos = ui.element('div').classes('grid grid-cols-12 w-full gap-x-4 gap-y-2 items-start')

            with grid_yos:
                for campo in Mem_Campos:

                    # --- MODIFICADO: Si es SaltoDeLinea, forzamos el salto en el grid ---
                    if campo.get("Clm") == "SaltoDeLinea":
                        ui.element('div').classes('col-span-12') # Fuerza el salto de fila[cite: 2]
                        continue

                    # --- MODIFICADO: Definimos cuánto ocupa cada campo (Col-Span) ---
                    # Por defecto ocupa 3 de 12 (4 campos por línea)
                    ancho_col = f"col-span-{campo.get('Grid', 6)}"

                    with ui.column().classes(f'{ancho_col} w-full'):
                        id_clm = campo.get("Clm", "SinId")
                        rotulo = campo.get("Rot", id_clm)
                        Dat = str(campo.get("Dat", ""))
                        Mod = campo.get("Mod", "Mod")
                        vfy = campo.get("Vfy", "")
                        Tip = campo.get("Tip", "C")
                        Lon = int(campo.get("Lon", 0))
                        Dec = int(campo.get("Dec", 0))
                        opciones = campo.get("Opc", [])

                        import inspect
                        print(f"Inicio Columna {id_clm} - {inspect.currentframe().f_lineno}")

                        esta_bloqueado = solo_lectura or (Acn == "Mod" and Mod == "Cre")
                        print(f"Inicio Columna {id_clm} - {inspect.currentframe().f_lineno}")
                        # Si tiene opciones, dibujamos un Select
                        if "Opc" in vfy and opciones:
                            print(f"ES UNA OPCION - {inspect.currentframe().f_lineno}")

                            valor_a_mostrar = Dat if Dat in opciones else (opciones[0] if opciones else "")

                            sel = ui.select(
                                label=rotulo,
                                options=opciones,
                                value=valor_a_mostrar
                            ).classes('w-full')

                            if esta_bloqueado:
                                sel.props('disable') # En selects se usa disable para que no abran el menú

                            entradas_gui[id_clm] = sel

                            print(f"FIN OPCION - {inspect.currentframe().f_lineno}")

                        elif Tip == "N":  # --- LÓGICA PARA NUMÉRICOS (N) ---
                            print(f"{inspect.currentframe().f_lineno}")
                            try:
                                n_puro = float(Dat) if Dat and str(Dat).strip() else 0.0
                                val_str = "{:,.{prec}f}".format(n_puro, prec=Dec)
                            except ValueError:
                                val_str = "0.00"

                            def formatear_miles(e, d=Dec):
                                try:
                                    limpio = e.sender.value.replace(',', '')
                                    if limpio:
                                        e.sender.value = "{:,.{prec}f}".format(float(limpio), prec=d)
                                except ValueError:
                                    pass

                            # 3. Creamos el input
                            ipt = ui.input(
                                label = rotulo,
                                value = val_str,
                            ).props('input-class="text-right"').classes('w-full').props('clearable')

                            # 4. Asignamos el evento y lo registramos en el diccionario
                            ipt.on('blur', lambda e: formatear_miles(e))

                            if esta_bloqueado:
                                ipt.props('readonly')

                            entradas_gui[id_clm] = ipt

                            '''
                                print(f"ES NUMERICO - {inspect.currentframe().f_lineno}")
                                # 1. Extraemos precisión desde Lon (ej: 13.2 -> 2)
                                val_num = float(Dat) if Dat and Dat.strip() else 0.0
                                ipt = ui.number(
                                    label = rotulo,
                                    value = val_num,
                                    max = int('9' * Lon),
                                    format=f'%.{Dec}f',
                                    precision=Dec,
                                    step=None
                                ).classes('w-full').props('clearable')
    #                            ipt.props(f'input-class="text-right" step=0.{"0"*(Dec-1)}1')
                                ipt.props(f'input-class="text-right"')

                                print(f"Estoy en la línea: {inspect.currentframe().f_lineno}")
                                # Para las comas de millares (formato europeo/contable) en el valor visual
                                # NiceGUI usa el formateo de Quasar por debajo
                                ipt.props('mask="###.###.###.###,##" reverse-fill-mask')
                                print(f"FIN NUMERICO - {inspect.currentframe().f_lineno}")

                                if esta_bloqueado:
                                    ipt.props('readonly')

                                entradas_gui[id_clm] = ipt
                            '''
                            print(f"{inspect.currentframe().f_lineno}")

                        elif Tip == "D":  # FECHAS
                            print(f"ES FECHA - {inspect.currentframe().f_lineno}")
#                            # Fecha de solo lectura
#                            date = ui.date_input(label='Fecha Fija', value='21/01/1967')
#                            date.picker.props('mask="DD/MM/YYYY"')
#                            date.disable()  # Es su solo lectura

                            # Normal
                            ipt = ui.date_input(rotulo, value=Dat)
                            ipt.picker.props('mask="DD/MM/YYYY"')
                            ipt.props('readonly')
                            ipt.picker.props('mask="DD/MM/YYYY" today-btn')
#                            ipt.props('minimal')
#                            ui.label().bind_text_from(date, 'value', lambda v: f'Fecha : {v}')
                            '''
                            # Rango de Fechas
                            date = ui.date_input('Rango : ', value='01/05/2026 - 21/05/2026', range_input=True)
                            date.classes('w-60')
                            date.picker.props('mask="DD/MM/YYYY"')
                            date.props('readonly')
#                            ui.label().bind_text_from(date, 'value', lambda v: f'Rango : {v}')

                            # Fecha con Bloque inicial
                            date = ui.date_input('Date', value='29/04/2026')
                            date.picker.props[':options'] = 'date => date >= "2026/04/29"'
                            date.picker.props('mask="DD/MM/YYYY"')
                            date.props('readonly')
#                            ui.label().bind_text_from(date, 'value', lambda v: f'Fecha : {v}')
                            '''
                            if esta_bloqueado:
                                ipt.disable()  # Es su solo lectura
#                                ipt.props('readonly')

                            entradas_gui[id_clm] = ipt  # Añado a la pantalla
                            print(f"FIN FECHA - {inspect.currentframe().f_lineno}")
                        else:   # --- TIPO C ---
                            print(f"ES GENERAL - {inspect.currentframe().f_lineno}")
                            print(f"Estoy en la línea: {inspect.currentframe().f_lineno}")
                            ipt = ui.input(
                                label=rotulo,
                                value=Dat
                                ).classes('w-full').props('clearable')
                            print(f"Estoy en la línea: {inspect.currentframe().f_lineno}")

                            lon_int = int(float(Lon))
                            if lon_int > 0:
                                ipt.props(f'maxlength={lon_int}')
    #                           if lon > 0:
    #                               ipt.props(f'maxlength={lon}')

                            if "Pas" in vfy:
                                ipt.props('type=password')

                            print(f"FIN GENERAL - {inspect.currentframe().f_lineno}")

                            if esta_bloqueado:
                                ipt.props('readonly')

                            print(f"GRABO - {inspect.currentframe().f_lineno}")
                            entradas_gui[id_clm] = ipt
                            print(f"FIN GRABO - {inspect.currentframe().f_lineno}")

                        # CREAR SEGUNDO CAMPO SI ES CONTRASEÑA ---
                        if "Pas" in vfy and not (solo_lectura or (Acn == "Mod" and ClmMod == "Cre")):
                            # Creamos el campo de verificación con ID único
                            id_vfy = f"{id_clm}_Vfy"
                            entradas_gui[id_vfy] = ui.input(label=f"Verifique {rotulo}").classes('w-full').props('type=password')

    return await dialog
