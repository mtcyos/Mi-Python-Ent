#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Miguel Tortosa

Apl_Ges_Frm.py  .Py donde estan todas las Def _Frm


Gestión Definiciones Frm, para el entorno Gui con base en nicegui

Tanto para Local (Loc) como Web (Www)

Estructura nombre Def

PREFIJO DESCRIPCION
Apl_    Def de gestion de las Aplicación (Como contrl de Acceso)

SUFIJO
_Frm -> Modo Grafico -> GUI/Web

"""

################################################################### Inicio Def ##########################################################

from nicegui import ui, app
import builtins
import asyncio

async def Apl_UsrAcc_Frm(Fnc_Usr=None, Fnc_Pas=None, Fnc_Enc=None):
    # Dibuja la interfaz de login en NiceGUI"""
    from nicegui import context
    await ui.context.client.connected()

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

    Mem_Num = 1
    Mem_NumMax = YosCfg["Usr_NumMaxAcc"]

    # Solo contraseña
    Mem_PasSolo = False
    if not Fnc_Usr and Fnc_Pas:
        print("Mem_PasSolo")
        Mem_PasSolo = True

    # Solo ReVerificacion
    Mem_VfySolo = False
    if Fnc_Usr == YosSes["Usr_Nik"] and Fnc_Pas == YosSes['Usr_Pas']:
        print("Mem_VfySolo")
        Mem_VfySolo = True

    #with ui.dialog().props('persistent') as dialog: # persistent evita cerrar con ESC
#    with ui.dialog().props('persistent').style('background-color: white !important;') as dialog:
#        with ui.column().classes('items-center w-full bg-white q-pa-xl').style('min-width: 550px;'):
    with ui.dialog().props('persistent flat transition-none').style('background-color: transparent !important;') as dialog:

        with ui.column().classes('items-center bg-white q-pa-xl shadow-24 rounded-xl overflow-hidden').style('width: 600px; height: auto; overflow: hidden; margin: auto;'):

            # --- BLOQUE TÍTULO (Arriba) ---
            with ui.column().classes('items-center'):
                ui.label(YosCfg.get("Apl_Apl", "Control Central")).classes('text-h6 text-black-2')
                ui.label(YosCfg.get("Apl_Nom", "SISTEMA YOS")).classes('text-h6 text-black text-weight-bolder')

            # --- BLOQUE TARJETA (Abajo) ---
            with ui.card().classes('p-8 w-130 shadow-2xl border-[1px] border-gray-300 rounded-xl'):
                lbl_acceso = ui.label(f'ACCESO ({Mem_Num}/{Mem_NumMax})').classes('text-h6 mb-4 text-center')
                if not (Mem_PasSolo or Mem_VfySolo):
                    usuario = ui.input(label='Usuario').classes('w-full text-lg')
                password = ui.input(label='Contraseña', password=True).classes('w-full text-xl') #
                lbl_error = ui.label('').classes('text-red-600 text-sm font-bold w-full text-center mt-2')

                ui.button('ENTRAR', on_click=lambda: validar()).classes('w-full mt-6 text-white font-bold').style('height: 45px;')
                ui.keyboard(on_key=lambda e: validar() if e.key.enter and e.action.keydown else None)

            def validar():
                nonlocal Mem_Num
                nonlocal Mem_NumMax

                usuarios_db = {
                    "mtcyos":   {"cPas": Yos.Yos_Md5("mtcyos"),     "cNom": "MIGUEL TORTOSA",   "cNiv": "99"},
                    "julio":    {"cPas": Yos.Yos_Md5("julio"),      "cNom": "JULIO CERRATO", "  cNiv": "01"},
                    "ricardo":  {"cPas": Yos.Yos_Md5("ricardo"),    "cNom": "RICARDO LOPEZ",    "cNiv": "01"},
                    "marco":    {"cPas": Yos.Yos_Md5("marco"),      "cNom": "MARCO MEDINA",     "cNiv": "01"},
                }
                Mem_Pas = password.value.strip()
                if Fnc_Enc == "md5":
                    print("md5")
                    Mem_Pas = Yos.Yos_Md5(Mem_Pas)

                Mem_Ok = False
                if Mem_PasSolo:
                    print(f"{Fnc_Pas} == {Mem_Pas}")
                    if Fnc_Pas == Mem_Pas:
                        Mem_Ok = True

                elif Mem_VfySolo:
                    Mem_Nik = usuario.value.strip()
                    if Fnc_Usr== Mem_Nik and  Fnc_Pas == Mem_Pas:
                        Mem_Ok = True

                else: # LOGIN NORMAL Usr, Pas
                    Mem_Nik = usuario.value.strip()
                    Mem_Pas = password.value.strip()
                    Mem_Pas = Yos.Yos_Md5(Mem_Pas)

                    user_data = usuarios_db.get(Mem_Nik)
                    if user_data and user_data["cPas"] == Mem_Pas:
                        Mem_Ok = True
                        # --- AJUSTE BIN: Registramos autenticación y cerramos diálogo ---
                        app.storage.user.update({'autenticado': True})
                        dialog.submit(True)
                        ui.navigate.to('/')

                if Mem_Ok == False:
                    Mem_Num += 1
                    if Mem_Num <= Mem_NumMax:
                        lbl_acceso.set_text(f'ACCESO ({Mem_Num}/{Mem_NumMax})')
                        lbl_error.set_text(f'LOS DATOS SON INCORRECTOS')
                    else:
                        if Mem_PasSolo:
                            dialog.submit(False)
                        elif Mem_VfySolo:
                            dialog.submit(False)
                        else:
                            ui.navigate.to('https://www.google.com')

                else:   # Acceso correcto
                    print(f'{Yos.Yos_TimeStamp()} -> {YosSes["Usr_Ipd"]} : {Mem_Nik} - ACCESO CORRECTO')

                    if Mem_PasSolo:
                        dialog.submit(True)
                    elif Mem_VfySolo:
                        dialog.submit(True)
                    else:
                        # Mantenemos tus asignaciones intactas
                        YosSes['Usr_Nik'] = usuario.value
                        YosSes['Usr_Pas'] = password.value
                        YosSes['Usr_Nom'] = user_data["cNom"]
                        YosSes['Usr_Niv'] = user_data["cNiv"]
                        # --- AJUSTE BIN: Aseguramos el cierre del await ---
                        dialog.submit(True)
                        ui.navigate.to('/')

#            ui.button('ENTRAR', on_click=validar).classes('w-full mt-4')
#            ui.keyboard(on_key=lambda e: validar() if e.key.enter and e.action.keydown else None)

    dialog.open()
    return await dialog
################################# A REVISAR #################################################################
