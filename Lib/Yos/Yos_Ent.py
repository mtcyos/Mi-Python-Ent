#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
YosCtr - Desde aqui se controla todo el sistema

@author: Miguel Tortosa
"""

from Yos import Yos_FrmCls, FrmLin, FrmWit, FrmCab, AplIni

def Yos_Ent():
    import os
    import getpass
    import msvcrt

    from colorama import Fore, Back, Style

    from Yos import Yos_Pas, Idd_TabMod, Yos_Md5


    # --- PROMPT_TOOLKIT PARA Yos_Ent ---
    from prompt_toolkit.shortcuts import prompt, print_formatted_text
    from prompt_toolkit.formatted_text import HTML

    # Verifico Autorizacion (Estilo prompt_toolkit)
    Yos_FrmCls()
    FrmCab("Cab")
    print_formatted_text(HTML(f"<ansiyellow>{FrmLin('CONFIGURACIÓN DEL ENTORNO DE LA APLICACION', 'C')}</ansiyellow>"))
    print()

    if not Yos.Apl_UsrAcc_Txt("", YosCfg["Apl_AdmPas"], "md5"): # Solo pide la contraseña
        Yos_FrmCls()
        return

    # Generamos el Menu
    Yos_FrmCls()

    YosCtr_Mnu = {
    '00': {'Tip': 'Cab', 'Txt': 'ENTORNO',                          'Fnc': '',          'Ent': ''},
    '09': {'Tip': 'Opc', 'Txt': 'SALIR',                            'Fnc': 'S',         'Ent': ''},

    '100': {'Tip': 'Cab', 'Txt': 'INFORMACION',                     'Fnc': '',          'Ent': ''},
    '101': {'Tip': 'Opc', 'Txt': 'VER ENTORNO',                     'Fnc': 'EntMst',    'Ent': ''},
    '103': {'Tip': 'Opc', 'Txt': 'VER YosCfg',                      'Fnc': 'YosCfg',    'Ent': ''},

    '200': {'Tip': 'Cab', 'Txt': 'ENTORNO DE ' +YosCfg["Apl_Apl"],  'Fnc': '',          'Ent': ''}, # Entrono de la Aplicacion
    '201': {'Tip': 'Opc', 'Txt': 'Dat - DATOS DE LA APLICACION',    'Fnc': 'Dat',       'Ent': ''},
    '202': {'Tip': 'Opc', 'Txt': '------------------',              'Fnc': '',          'Ent': ''},
    '203': {'Tip': 'Opc', 'Txt': 'Mnu - MENUS',                     'Fnc': 'Mnu',       'Ent': ''},
    '204': {'Tip': 'Opc', 'Txt': 'Ord - ORDEN',                     'Fnc': 'Ord',       'Ent': ''},
    '205': {'Tip': 'Opc', 'Txt': 'Brw - BROWSE',                    'Fnc': 'Brw',       'Ent': ''},
    '206': {'Tip': 'Opc', 'Txt': 'ClmMod - COLUMNAS A MODIFICAR',   'Fnc': 'ClmMod',    'Ent': ''},
    '207': {'Tip': 'Opc', 'Txt': '------------------',              'Fnc': '',          'Ent': ''},
    '208': {'Tip': 'Opc', 'Txt': 'Bdt - BASES DE DATOS',            'Fnc': 'Bdt',       'Ent': ''},

    '300': {'Tip': 'Cab', 'Txt': 'ENTORNO DE ' +YosCfg["Yos_Apl"],  'Fnc': '',          'Ent': ''}, # Entrono de la Libreria
    '301': {'Tip': 'Opc', 'Txt': 'Dat - DATOS DE LA LIBRERIA',      'Fnc': 'Yos_Dat',   'Ent': ''},
    '302': {'Tip': 'Opc', 'Txt': '------------------',              'Fnc': '',          'Ent': ''},
    '304': {'Tip': 'Opc', 'Txt': 'Ord - ORDEN',                     'Fnc': 'Yos_Ord',   'Ent': ''},
    '305': {'Tip': 'Opc', 'Txt': 'Brw - BROWSE',                    'Fnc': 'Yos_Brw',   'Ent': ''},
    '306': {'Tip': 'Opc', 'Txt': 'ClmMod - COLUMNAS A MODIFICAR',   'Fnc': 'Yos_ClmMod','Ent': ''},
    '307': {'Tip': 'Opc', 'Txt': '------------------',              'Fnc': '',          'Ent': ''},
    '308': {'Tip': 'Opc', 'Txt': 'Bdt - BASES DE DATOS',            'Fnc': 'Yos_Bdt',   'Ent': ''},

    '400': {'Tip': 'Cab', 'Txt': 'HEERAMIENTAS',                    'Fnc': '',          'Ent': ''},
    '410': {'Tip': 'Opc', 'Txt': 'GENERAR md5',                     'Fnc': 'md5',       'Ent': ''},
#    '400': {'Tip': 'Cab', 'Txt': 'PRUEBAS',                         'Fnc': '',         'Ent': ''},
#    '401': {'Tip': 'Opc', 'Txt': 'Mnu - MENUS (Textual)',           'Fnc': '101',      'Ent': ''},
}
    # INICIO - Proceso del menu
    from Yos import Mnu, Mnu_Gui
    YosCfg['Apl_TitSub'] = "CONFIGURACIÓN DEL ENTORNO DE LA APLICACION"

    while True:
        MnuFnc = Mnu_Gui(YosCtr_Mnu)

        Mem_Svr="YosCfg"
        Mem_Tab=""

        match MnuFnc:
            case "S": # Salir al Menú Anterior
                YosCfg['Apl_TitSub'] = ""
                os.system('cls')
                break

            case "EntMst":
                Yos_Ent_Mst()
            case "YosCfg":
                Yos_Ent_Mst_YosCfg()

            # ------------------------------------------------          YosCfg
            case "Bdt": # Bdt - BASES DE DATOS
                Mem_Tab="Bdt"

            case "Dat": # Dat - DATOS DE LA APLICACION
                Mem_Tab="Dat"

            case "Mnu": # Mnu - MENUS
                Mem_Tab="Mnu"

            case "Ord": # Ord - ORDEN
                Mem_Tab="Ord"

            case "Brw": # Brw - BROWSE
                Mem_Tab="Brw"

            case "ClmMod": # ClmMod - COLUMNAS A MODIFICAR
                Mem_Tab="ClmMod"

            # ------------------------------------------------          YosLib
            case "Yos_Bdt": # YosLib.Bdt - BASES DE DATOS
                Mem_Svr="YosLib"
                Mem_Tab="Bdt"

            case "Yos_Dat": # YosLib.Dat - DATOS DE LA APLICACION
                Mem_Svr="YosLib"
                Mem_Tab="Dat"

            case "Yos_Ord": # YosLib.Ord - ORDEN
                Mem_Svr="YosLib"
                Mem_Tab="Ord"

            case "Yos_Brw": # YosLib.Brw - BROWSE
                Mem_Svr="YosLib"
                Mem_Tab="Brw"

            case "Yos_ClmMod": # YosLib.ClmMod - COLUMNAS A MODIFICAR
                Mem_Svr="YosLib"
                Mem_Tab="ClmMod"

            case "md5": # GENERAR md5
                Yos_FrmCls()
                FrmCab("Cab")

                print_formatted_text(HTML(f"<ansiyellow>{FrmLin('CONFIGURACIÓN DEL ENTORNO YosCtr', 'C')}</ansiyellow>"))
                print()

                from prompt_toolkit.application import Application
                from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
                from prompt_toolkit.widgets import Frame, TextArea, Label
                from prompt_toolkit.key_binding import KeyBindings
                from prompt_toolkit.styles import Style as PtStyle

                # 1. Estilo Yo: Marco Verde, Etiquetas Amarillas
                Frm_Style = PtStyle.from_dict({
                    'frame.border': 'green',
                    'frame.label':  'green',
                    'label':        '#ffaf00',
                    'error_msg':    'red bold italic',
                })

                # 2. Configuración de Medidas
                Mem_WX = 80
                Mem_HY = 10

                # 3. Definición de Campos
                usr_input = TextArea(multiline=False, focus_on_click=True)
                error_field = Label(text="", style='class:error_msg')

                # 4. Teclado: Validación unificada DENTRO de la ventana
                kb = KeyBindings()

                @kb.add("enter")
                def _(event):
                    import hashlib
                    Mem_Txt = usr_input.text
                    if Mem_Txt:
                        Mem_Txt_Hex = Yos_Md5(Mem_Txt)
#                        Mem_Txt_encoded = Mem_Txt.encode('utf-8')
#                        Mem_Txt_md5 = hashlib.md5()
#                        Mem_Txt_md5.update(Mem_Txt_encoded)
#                        Mem_Txt_Hex = Mem_Txt_md5.hexdigest()
                        error_field.text = f" El md5 es {Mem_Txt_Hex}"

                        event.app.exit(result=Mem_Txt_Hex)

                @kb.add("tab")
                def _(event):
                    pass

                @kb.add("c-c")
                def _(event): event.app.exit(result=False)

                # 5. Diseño del Cuerpo
                cuerpo = HSplit([
                    Window(height=1),
                    VSplit([Label(text=" Cadena a convertir : ", width=22), usr_input]),
                    Window(height=1),
                    error_field,
                ])

                # 6. Contenedor Centrado
                root_container = HSplit([
                    VSplit([
                        Window(),
                        Frame(
                            body=cuerpo,
                            title=' * GENERAR CÓDIGO md5 * ',
                            width=Mem_WX,
                            height=Mem_HY
                        ),
                        Window()
                    ])
                ])

                # 7. Ejecución
                application = Application(
                    layout=Layout(container=root_container),
                    key_bindings=kb,
                    style=Frm_Style,
                    mouse_support=True,
                    full_screen=False
                )

                Mem_Hex = application.run()

                from Yos import Yos_ClipCopy
                if Yos_ClipCopy(Mem_Hex):
                    print_formatted_text(HTML(f"<b><ansigreen>{FrmLin('Se ha copiado al portapapeles.', 'C')}</ansigreen></b>"))

                FrmWit()
                Yos_FrmCls()

#                Idd_TabMod("YosCfg", "Mnu")
#                input("Fin")

        if Mem_Tab:
            Idd_TabMod(Mem_Svr, Mem_Tab)

# FIN - Proceso del menu

def Yos_Ent_Mst():
    from prompt_toolkit.shortcuts import prompt, print_formatted_text
    from prompt_toolkit.formatted_text import HTML

    if YosCfg["Dbg"] == "S": print("******** Yos.AcdEtn() ********")
    Acd = []
    Acd.append("S.O. : " + YosCfg["Etn"] + " - " + YosCfg["Etn_Des"])
    Acd.append("")

    Acd.append("DIRECTORIOS")
    Acd.append("")

    Acd.append("Dir.Apl : " + YosCfg["Apl_Dir"])
    Acd.append("Dir.Yos : " + YosCfg["Yos_Dir"])
    Acd.append("")

    if YosCfg.get("Apl_Bdt_Sis_Dir"):
        Acd.append("Yosis : " + YosCfg["Apl_Bdt_Sis_Dir"])
        Acd.append("")

    if YosCfg.get("Apl_Bdt_Msi_Dir"):
        Acd.append("YosMsi : " + YosCfg["Apl_Bdt_Msi_Dir"])
        Acd.append("")

    if YosCfg.get("Apl_Bdt_Mrp_Dir"):
        Acd.append("YosMrp : " + YosCfg["Apl_Bdt_Mrp_Dir"])
        Acd.append("")

    if YosCfg.get("Apl_Bdt_Mae_Dir"):
        Acd.append("YosMae : " + YosCfg["Apl_Bdt_Mae_Dir"])
        Acd.append("")

    if YosCfg.get("Apl_Bdt_Dat_Dir"):
        Acd.append("YosDat : " + YosCfg["Apl_Bdt_Dat_Dir"])
        Acd.append("")

    if YosCfg.get("Apl_Bdt_Ach_Dir"):
        Acd.append("Archivo : " + YosCfg["Apl_Bdt_Ach_Dir"])
        Acd.append("")

    Acd.append("Dir.Tmp : " + YosCfg["Etn_Tmp"])

    Yos_FrmCls()
    FrmCab("Cab")
    print()

    print_formatted_text(HTML(f"<orange>{FrmLin('ENTORNO DEL SISTEMA', 'C')}</orange>"))

    print()

    Mem_nLon = max((len(linea) for linea in Acd), default=0)
    Mem_nLonMax = Mem_nLon + 4

    Mem_Txt = f'{"*" * Mem_nLonMax}'
    print_formatted_text(HTML(f"<b><ansigreen>{FrmLin(Mem_Txt, 'C')}</ansigreen></b>"))

    for lin in Acd:
        Text = f"* {lin:<{Mem_nLon}} *"
        print_formatted_text(HTML(f"<b><ansigreen>{FrmLin(Text, 'C')}</ansigreen></b>"))

    print_formatted_text(HTML(f"<b><ansigreen>{FrmLin(Mem_Txt, 'C')}</ansigreen></b>"))

    FrmWit()
    Yos_FrmCls()

def Yos_Ent_Mst_YosCfg():
    from prompt_toolkit.shortcuts import prompt, print_formatted_text
    from prompt_toolkit.formatted_text import HTML

    Yos_FrmCls()
    FrmCab("Cab")
    print_formatted_text(HTML(f"<orange>{FrmLin('YosCfg', 'C')}</orange>"))

    print_formatted_text(HTML(f"<ansigreen>{FrmLin(' SELECCIONE LOS DATOS A VER de YosCfg[*] ', 8)}</ansigreen>"))
    print_formatted_text(HTML(f"<ansigreen>{FrmLin('*****************************************', 8)}</ansigreen>"))
    print_formatted_text(HTML(f"<ansigreen>{FrmLin(' Vacio = TODO                            ', 8)}</ansigreen>"))
    print_formatted_text(HTML(f"<ansigreen>{FrmLin(' Apl_ = APLICACION                       ', 8)}</ansigreen>"))
    print_formatted_text(HTML(f"<ansigreen>{FrmLin(' Dbg_ = DEBUG / DEPURACION               ', 8)}</ansigreen>"))
    print_formatted_text(HTML(f"<ansigreen>{FrmLin(' Eml_ = EMAIL                            ', 8)}</ansigreen>"))
    print_formatted_text(HTML(f"<ansigreen>{FrmLin(' Etn_ = ENTORNO                          ', 8)}</ansigreen>"))
    print_formatted_text(HTML(f"<ansigreen>{FrmLin(' Usr_ = USUARIO                          ', 8)}</ansigreen>"))
    print_formatted_text(HTML(f"<ansigreen>{FrmLin(' Yos_ = LIBRERIA Yos                     ', 8)}</ansigreen>"))
    print()
    print_formatted_text(HTML(f"<ansigreen>{FrmLin(' Apl_Mnu = MENU APLICACION               ', 8)}</ansigreen>"))
    print_formatted_text(HTML(f"<ansigreen>{FrmLin('*****************************************', 8)}</ansigreen>"))
    print()
    Mem_Sub = prompt(HTML(f"<orange>{FrmLin('SELECCION : ', 8)}</orange>")).strip()
    print()

    Yos_FrmCls()
    FrmCab("Cab")
    print_formatted_text(HTML(f"<ansigreen>{FrmLin(f'VALORES YosCfg[{Mem_Sub}]', 8)}</ansigreen>"))
    print_formatted_text(HTML(f"<ansigreen>{FrmLin('*****************************************', 8)}</ansigreen>"))

    for k, v in YosCfg.items():
        if k.startswith(Mem_Sub):   # Empieza por el Prefijo
            if k == "Apl_Mnu" and Mem_Sub == "Apl_Mnu":
                Mem_Txt = f"<ansiyellow>{k} : </ansiyellow>"
                print_formatted_text(HTML(FrmLin(Mem_Txt, 8)))
                if isinstance(v, dict):
                    for sub_k, sub_v in v.items():
                        # Formateamos cada opción del menú en una línea nueva
                        Mem_Txt = f"   <ansicyan>'{sub_k}'</ansicyan>: <ansiwhite>{sub_v}</ansiwhite>"
                        print_formatted_text(HTML(FrmLin(Mem_Txt, 10)))
            elif k == "Apl_Mnu" and Mem_Sub != "Apl_Mnu":
                pass
            else:
                Mem_Txt = f"<ansiyellow>{k} : </ansiyellow><ansiwhite>{v}</ansiwhite>"
                print_formatted_text(HTML(FrmLin(Mem_Txt, 8)))

    print_formatted_text(HTML(f"<ansigreen>{FrmLin('*****************************************', 8)}</ansigreen>"))

    FrmWit()
    Yos_FrmCls()



