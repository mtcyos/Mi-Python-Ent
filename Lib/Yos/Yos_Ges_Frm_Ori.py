# -*- coding: utf-8 -*-
from nicegui import ui, app
import builtins

def Yos_BarEst_Frm():
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

def FrmGen(Fnc_Mnu, finalizar_fnc):
    """Define la interfaz con menús en cascada y separadores estilo HMG."""

    ui.add_head_html('''
        <style>
            body { background-color: #f0f2f5; }
            .q-btn { font-size: 0.75rem !important; }
            .q-item { font-size: 0.75rem !important; min-height: 24px !important; }
            .menu-parent:hover > .q-menu { display: block !important; }

            /* 1. ESTILO PARA LA RAYITA PEQUEÑA (HMG) */
            .hmg-separator {
                margin: 4px auto !important; /* Centrada horizontalmente */
                width: 90% !important;        /* No llega a los bordes */
                background-color: #d1d5db !important; /* Gris suave */
                min-height: 1px !important;
            }
        </style>
    ''')

    def generar_items(diccionario):
        for clave in sorted(diccionario.keys()):
            valor = diccionario[clave]
            texto = valor.get("Txt", "")
            comando = valor.get("Fnc", "")
            codigo = valor.get("Cod", "") # Importante para detectar Sep

            if YosCfg.get("Apl_UsrAcc") != "S" and YosCfg.get("Apl_Etn") =="Www" and comando == "YosAppSld":
                continue
            if YosCfg.get("Apl_UsrAcc") != "S" and comando == "YosAppSld": # Si no hay control de usuario, no grabo la opcion YosAppSld en el Menu
                texto ="SALIR DE LA APLICACION"

            # 2. DETECCIÓN DE SEPARADOR
            # Si el código es 'Sep' o no tiene texto ni función, dibujamos la rayita
            if codigo == "Sep" or (not texto and not comando):
                ui.separator().classes('hmg-separator')
                continue

            clase_item = 'text-xs min-h-[24px] py-0 px-3'

            if "Sub" in valor and isinstance(valor["Sub"], dict):
                with ui.item().props('clickable').classes(clase_item):
                    ui.label(f"{texto}").classes('flex-grow')
                    ui.icon('chevron_right', size='xs').classes('ml-2')

                    with ui.menu().props('anchor="top right" self="top left"').classes('bg-white border border-gray-400'):
                        generar_items(valor["Sub"])
            else:
                ui.menu_item(texto, on_click=lambda f=comando: finalizar_fnc(f)).classes(clase_item)

    # --- CABECERA REAL (Mantenemos tu lógica original de botones) ---
    with ui.row().classes('w-full bg-slate-200 p-0 gap-0 border-b border-gray-400 items-center'):
        for clave in sorted(Fnc_Mnu.keys()):
            valor = Fnc_Mnu[clave]
            texto = valor.get("Txt", "Sin nombre")
            with ui.button(texto).props('flat color=black').classes('text-xs font-bold min-h-[24px] py-0 px-3 rounded-none hover:bg-slate-300'):
                if "Sub" in valor:
                    with ui.menu().classes('bg-white border border-gray-400'):
                        generar_items(valor["Sub"])

    # --- BLOQUE DE LOGO CENTRAL (AÑADIR AQUÍ) ---
    with ui.column().classes('w-full items-center q-pa-md gap-0'):

        # Si quieres que suba MÁS, puedes usar .style('margin-top: -10px;')
        ui.image(YosCfg["Apl_Dir"]+'Img/Log_01.png').style('width: 100px; margin-top: -30px;')

        ui.label(YosCfg.get("Apl_Apl", "Err : YosCfg.Apl_Apl")).classes('text-h4 font-bold q-my-none').style('line-height: 1;')
        ui.label(YosCfg.get("Apl_Nom", "Err : YosCfg.Apl_Nom")).classes('text-h6 font-bold q-my-none').style('line-height: 1;')
        # 4. Copyright y Email (q-mt-xs solo para un pequeño respiro final)
        with ui.row().classes('gap-2 text-subtitle2 q-mt-xs'):
            ui.label(f'{YosCfg.get("Apl_Cpy", "2025 Err : YosCfg.Apl_Cpy")}')
            ui.label('-')
            ui.label(YosCfg.get("Apl_CpyEml", "Err : YosCfg.Apl_CpyEml"))

    # BROWSE DE NOTICIAS ---
    # 1. Quitamos q-px-md y usamos q-px-none para que el Browse toque los bordes
    with ui.column().classes('w-full q-px-none q-mt-none gap-0'):

        # Etiqueta de título con un poco de padding lateral para que no toque el borde del cristal
        ui.label('📰 ULTIMAS NOTICIAS').classes('text-bold text-grey-8 border-b w-full q-px-md bg-grey-2')

        # 2. El área de scroll al 100% de ancho (width: 100%)
        # He subido el alto a 55vh para que cubra más pantalla hasta la barra de estado
        with ui.scroll_area().style('height: 55vh; width: 100%; border-top: 1px solid #ddd; background: #ffffff;'):
            with ui.column().classes('q-pa-md gap-1'):
                # Las líneas de noticias
                ui.label('• [2026-04-15] Sistema optimizado para Windows 10.').classes('text-caption font-medium')
                ui.label('• [2026-04-14] Nueva librería Yos_DefLib cargada con éxito.').classes('text-caption text-blue-9')
                ui.label('• [2026-04-13] Bienvenido al sistema YosCtr, mtcyos.').classes('text-caption')

                # Ejemplo de noticia larga para probar el ancho
                ui.label('• Recordatorio: El árbol de directorios definitivo ya está configurado en Python/Lib/Yos.').classes('text-caption')


#    Yos_BarEst_Frm()
    return "OK"
