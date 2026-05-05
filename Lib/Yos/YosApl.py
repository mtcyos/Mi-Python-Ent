#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 16:12:06 2025
@author: mtcyos

yosLib_CtrApl - Libreria de Control de Acceso a las Aplicaciones y Subprogramas
"""

import builtins


################################################################### Inicio Def ##########################################################
async def Apl_UsrAcc(Fnc_Usr=None, Fnc_Pas=None, Fnc_Enc=None):
    # Control el acceso del usuario al sistema
    '''
    Fnc_Usr -> Usuario
    Fnc_Pas -> Contraseña
    Fnc_Enc -> Encriptacion (md5)
               ""  - Fnc_Pas este en texto plano
               md5 - Fnc_Pas ya esta encriptado en md5
    Si Fnc_Usr=="" y Fnc_Pas|="" -> Solo pide la contraseña

    if not Yos.Apl_UsrAcc(YosSes["Usr_Nik"], YosSes['Usr_Pas'], "md5"): # Usuario y Contraseña en md5 de usuario activo (Reverificacion Completa)
        input("INCRRECTO")
    input("CORRECTO")

    if not Yos.Apl_UsrAcc("", YosSes['Usr_Pas'], "md5"): # Contraseña en md5 de usuario activo (Reverificacion Parcial)
        print("ACCESO INCORRECTO")
    print("ACCESO CORRECTO")


    if not await Yos.Apl_UsrAcc(Fnc_Pas=YosCfg["Apl_AdmPas"], Fnc_Enc="md5"): # Solo pide la contraseña de YosCfg.Apl_AdmPas
        print("ACCESO INCORRECTO")
    print("ACCESO CORRECTO")

    '''
#    print(f'Apl_UsrAcc({Fnc_Usr}, {Fnc_Pas}, {Fnc_Enc}):')
    # Def / aplicacion Donde se encuentra
    YosSes['Apl_Def'] = YosCfg.get("Apl_Apl")

    # Capturar IP
    if builtins.Mem_Ini_AplEtn == "Txt":    # Entorno Txt
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            YosSes['Usr_Ipd'] = s.getsockname()[0].ljust(15)
            s.close()
        except:
            YosSes['Usr_Ipd'] = "127.0.0.1"
    else:
        from nicegui import ui
        try:
            # Captura segura: solo si hay un cliente conectado
            ip_web = str(ui.context.client.ip).ljust(15)
        except:
            ip_web = "127.0.0.1".ljust(15)

        YosSes['Usr_Ipd'] = ip_web

#    print(f'YosCfg[Apl_UsrAcc]={YosCfg.get("Apl_UsrAcc")} YosApl.64')
    if YosCfg.get("Apl_UsrAcc") != "S": # Sin Control de Acceso
        Apl_UsrAcc_UsrEliDat(Fnc_Cmd="SinUsr")
        return  # salgo con los datos de Usuario SIN USUARIO y sin Control de Acceso

    # Control de Usuario
    Apl_UsrAcc_UsrEliDat()

    if builtins.Mem_Ini_AplEtn == "Txt":    # Entorno Txt
        # PASAMOS los parámetros que recibimos (Fnc_Usr, Fnc_Pas, Fnc_Enc)
        return Yos.Apl_UsrAcc_Txt(Fnc_Usr=Fnc_Usr, Fnc_Pas=Fnc_Pas, Fnc_Enc=Fnc_Enc)
    else:
        # PASAMOS los parámetros que recibimos (Fnc_Usr, Fnc_Pas, Fnc_Enc)
        return await Yos.Apl_UsrAcc_Frm(Fnc_Usr=Fnc_Usr, Fnc_Pas=Fnc_Pas, Fnc_Enc=Fnc_Enc)

def Apl_UsrAcc_UsrEliDat(Fnc_Cmd=None):
    # Elimino los datos del Uuuaio
    if Fnc_Cmd == "SinUsr":
        YosSes['Usr_Nik'] = "SinUsr"
        YosSes['Usr_Pas'] = "SinUsr"
        YosSes['Usr_Nom'] = YosCfg.get("Apl_Nom", "SISTEMA YOS")
        YosSes['Usr_Niv'] = "99"
        return

    YosSes['Usr_Nik'] = ""
    YosSes['Usr_Pas'] = ""
    YosSes['Usr_Nom'] = ""
    YosSes['Usr_Niv'] = ""

################################# A REVISAR #################################################################

#
# Apl_UsrAcc_Txt - Control de Acceso
#
def Apl_UsrAcc_Txt(Fnc_Usr=None, Fnc_Pas=None, Fnc_Enc=None):
    '''
    Fnc_Usr -> Usuario
    Fnc_Pas -> Contraseña
    Fnc_Enc -> Encriptacion (md5)
               ""  - Fnc_Pas este en texto plano
               md5 - Fnc_Pas ya esta encriptado en md5
    Si Fnc_Usr=="" y Fnc_Pas|="" -> Solo pide la contraseña

    if not Apl_UsrAcc_Txt(YosSes["Usr_Nik"], YosSes['Usr_Pas'], "md5"): # Usuario y Contraseña en md5
        # Verifico que sea la misma persona
    '''

    Mem_SoloPas=""
    if not Fnc_Usr and Fnc_Pas:
        Mem_SoloPas="S"

    Fnc_Enc = Fnc_Enc.upper()

    import hashlib

    from prompt_toolkit.application import Application
    from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
    from prompt_toolkit.widgets import Frame, TextArea, Label
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.styles import Style as PtStyle

    # Control de Acceso (Variables internas para persistencia dentro del teclado)
    Mem_Cont = [0] # Usamos lista para mutabilidad
    Mem_Max = YosCfg.get("Usr_NumMaxAcc", 3)

    # 1. Estilo Yo: Marco Verde, Etiquetas Amarillas
    Frm_Style = PtStyle.from_dict({
        'frame.border': 'green',
        'frame.label':  'red',
        'label':        '#ffaf00', # Naranja
        'error_msg':    'red bold italic',
    })

    # 2. Configuración de Medidas
    Mem_WX = 60
    Mem_HY = 10

    # 3. Definición de Campos
    if not Mem_SoloPas: # Incluimos el Usuario
        usr_input = TextArea(multiline=False, focus_on_click=True)
    pwd_input = TextArea(multiline=False, password=True, focus_on_click=True)
    error_field = Label(text="", style='class:error_msg')

    # 4. Teclado: Validación unificada DENTRO de la ventana
    kb = KeyBindings()

    if not Mem_SoloPas: # Incluimos el Usuario
        @kb.add("enter")
        def _(event):
            if event.app.layout.has_focus(usr_input):
                event.app.layout.focus(pwd_input)
            else:
                # --- CORRECCIÓN DENTRO DE LA VENTANA ---
                Mem_Usr = usr_input.text
                Mem_Pas = pwd_input.text
                Mem_Ok = False

                # 1. Prioridad: Valores pasados por parámetro
                if Fnc_Usr and Fnc_Pas:
                    if Fnc_Enc=="MD5": # Fnc_Pas viene encriptada en Md5
                        Mem_Txt_encoded = Mem_Pas.encode('utf-8')
                        Mem_Txt_md5 = hashlib.md5()
                        Mem_Txt_md5.update(Mem_Txt_encoded)
                        Mem_Txt_Hex = Mem_Txt_md5.hexdigest()

                        Mem_Ok = (Mem_Usr == Fnc_Usr and Mem_Txt_Hex == Fnc_Pas)
                    else:
                        Mem_Ok = (Mem_Usr == Fnc_Usr and Mem_Pas == Fnc_Pas)
                # 2. Si no hay fijos, contra YosCfg / SQL
                else:
                    pass
                    # 3. Futuro: Aquí iría la consulta SQL
                    # Mem_Ok = Consultar_Bdt(Mem_Usr, Mem_Pas)
                    # Mem_Ok = (Mem_Usr == Sql_Usr and Mem_Pas == Sql_Pas)
                    # si Mem_Ok:
                    #     YosCfg["Usr_Nik"] = Mem_Usr
                    #     YosCfg["Usr_Pas"] = Mem_Pas

                if Mem_Ok:
                    event.app.exit(result=True)
                else:
                    Mem_Cont[0] += 1
                    if Mem_Cont[0] >= Mem_Max:
                        event.app.exit(result=False)
                    else:
                        # Actualizamos el error sin cerrar la ventana
                        error_field.text = f" ERROR: DATOS INCORRECTOS ({Mem_Cont[0]+1}/{Mem_Max}) "
                        usr_input.text = ""
                        pwd_input.text = ""
                        event.app.layout.focus(usr_input)

        @kb.add("tab")
        def _(event):
            if event.app.layout.has_focus(usr_input):
                event.app.layout.focus(pwd_input)
            else:
                event.app.layout.focus(usr_input)

    else:   # Sin el usuario
        @kb.add("enter")
        def _(event):
            Mem_Pas = pwd_input.text
            Mem_Ok = False

            # 1. Prioridad: Valores pasados por parámetro
            if Fnc_Pas:
                if Fnc_Enc=="MD5": # Fnc_Pas viene encriptada en Md5
                    Mem_Txt_encoded = Mem_Pas.encode('utf-8')
                    Mem_Txt_md5 = hashlib.md5()
                    Mem_Txt_md5.update(Mem_Txt_encoded)
                    Mem_Txt_Hex = Mem_Txt_md5.hexdigest()

                    Mem_Ok = (Mem_Txt_Hex == Fnc_Pas)
                else:
                    Mem_Ok = (Mem_Pas == Fnc_Pas)

                if Mem_Ok:
                    event.app.exit(result=True)
                else:
                    Mem_Cont[0] += 1
                    if Mem_Cont[0] >= Mem_Max:
                        event.app.exit(result=False)
                    else:
                        # Actualizamos el error sin cerrar la ventana
                        error_field.text = f" ERROR: DATOS INCORRECTOS ({Mem_Cont[0]+1}/{Mem_Max}) "
                        pwd_input.text = ""
                        event.app.layout.focus(pwd_input)

            @kb.add("tab")
            def _(event):
                event.app.layout.focus(usr_input)

    @kb.add("c-c")
    def _(event): event.app.exit(result=False)

    # 5. Diseño del Cuerpo
    if not Mem_SoloPas: # Incluimos el Usuario
        cuerpo = HSplit([
            Window(height=1),
            VSplit([Label(text=" Usuario    : ", width=14), usr_input]),
            Window(height=1),
            VSplit([Label(text=" Contraseña : ", width=14), pwd_input]),
            Window(height=1),
            error_field,
        ])
    else:
        cuerpo = HSplit([
            Window(height=1),
            VSplit([Label(text=" Contraseña : ", width=14), pwd_input]),
            Window(height=1),
            error_field,
        ])

    # 6. Contenedor Centrado
    root_container = HSplit([
        VSplit([
            Window(),
            Frame(
                body=cuerpo,
                title=' ACCESO RESTRINGIDO - POR FAVOR IDENTIFÍQUESE ',
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

    return application.run()
