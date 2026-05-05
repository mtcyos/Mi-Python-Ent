#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
   YosMnu_Frm.py
   Yos Menú en entrono Gráfico

   Copyright (c) 2026 Miguel Tortosa

   Licenciado bajo la Licencia MIT.

   Consulte el archivo LICENCIA en la raíz del proyecto para más información.
"""

def IniMain():

    class UserStorageProxy:
        def __getitem__(self, key):
            return app.storage.user.get(key)

        def __setitem__(self, key, value):
            app.storage.user[key] = value

        def get(self, key, default=None):
            return app.storage.user.get(key, default)
    import builtins
    builtins.YosSes = UserStorageProxy()

    # Añado Directorio de YosLib
    import platform
    import sys
    import os

    match platform.system():
        case "Windows":
            sys.path.append(os.path.abspath("..")+"\\Lib\\")
        case "Linux":
            sys.path.append(os.path.abspath("../Lib"))
        case "Darwin": # Soporte para Mac
            sys.path.append(os.path.abspath("../Lib"))
        case _:
            sys.exit(0)

    # Nombre de la Aplicacion
    import builtins
    builtins.Mem_Ini_AplCod = "YosMnu"                 # ES el nombre  REAL de la Aplicacion, NO LO CAMBIE, use cNom="Apl_Apl" en YosCfg.Dat
    builtins.Mem_Ini_AplNom = "MENU DE APLICACIONES"   # ES el nombre  REAL de la Aplicacion, NO LO CAMBIE, use cNom="Apl_Nom" en YosCfg.Dat
    builtins.Mem_Ini_AplEtn = "Gui"                    # ES el entorno REAL de la Aplicacion, NO LO CAMBIE, Gui = NiceGui, use cNom="Apl_Etn"={'Loc/Www} en YosCfg.Dat

    import Yos
    builtins.Yos = Yos

    Yos.Yos_Cfg()
    Yos.AplIni()

    if YosCfg["Apl_Etn"] not in ("Loc", "Www"):

        builtins.YosSes = YosCfg
        Yos.Apl_UsrAcc_UsrEliDat(Fnc_Cmd="SinUsr")
        YosSes['Usr_Ipd'] = "127.0.0.1".ljust(15)
        from prompt_toolkit import print_formatted_text, HTML
        print()
        ruta_completa = os.path.basename(YosCfg["Apl_Dir"].rstrip("\\"))
        nombre_app = os.path.basename(ruta_completa)
        print_formatted_text(HTML(f"<b>  ******** ATENCION ********</b>"))
        print_formatted_text(HTML(f"  APLICACION : <b>{nombre_app}</b>"))
        print()
        print_formatted_text(HTML(f"<ansired>  Entorno [{YosCfg.get('Apl_Etn')}] no soportado.</ansired>"))
        Yos.FrmWit(Fnc_Wit=8)
        asyncio.run(Yos.Apl_Frm_Fin(Fnc_Pgt="No"))

    YosCfg["Dbg"]="" # MODO DEPURACION S="Completo" X=Para NiceGUI en local

    #if not Yos.Yos_AplCre("Yos_DfpGes", Fnc_Tip="YosMnu_Frm"):
    #    input("errro")

    ######################################## NO TOCAR LO DE ARRIBA NUNCA ##################### si se necesita me avisas y yo lo modifico

    # PÁGINA DE LOGIN
    @ui.page('/login')
    async def login_page():
        if app.storage.user.get('autenticado', False) or YosCfg.get("Apl_UsrAcc") != "S":
            ui.navigate.to('/')
            return

        await Yos.Apl_UsrAcc()

    # PÁGINA PRINCIPAL PROTEGIDA
    @ui.page('/')
    async def index_page():

        # Verifico que si tienen control de Acceso y no se a identificado no lo deje entrar
        if YosCfg.get("Apl_UsrAcc") == "S":
            if not app.storage.user.get('autenticado', False):
                ui.run_javascript('window.location.href = "/login"')
                return

        if YosCfg.get("Apl_Etn") == "Loc" and YosCfg.get("Apl_UsrAcc") != "S" and not YosSes['Usr_Nik']:
            Yos.Apl_UsrAcc_UsrEliDat("SinUsr")

        YosSes["Apl_Def"] = YosCfg["Apl_Apl"]

        Mem_FncDefLib = ui.column().classes('w-full')

        async def al_seleccionar(MnuFnc):
            if not MnuFnc:
                return

            try:
                # CASOS ESPECIALES
                if MnuFnc == "YosAppSld": # CERRAR SESIÓN
                    await Yos.Apl_Frm_Fin(Fnc_Pgt="Si")
                    return

                if MnuFnc == "YosMnuCag":   # Recargo El menu
                    Yos.Yos_MnuRec(YosCfg["Apl_Apl"], "MnuGen")
                    # Refrescamos usando el objeto vivo
                    Mem_Yos_DefFrm_Btn.clear()
                    Mem_Yos_DefFrm_Btn.refrescar(YosCfg["Apl_Mnu"])
                    return

                if MnuFnc[:7] == "YosCmd:": # YosCmd: se pone ANTES del comando que queramos ejecutar
                    MnuFnc = MnuFnc.replace("YosCmd:", "").strip()

                    if not os.path.exists(MnuFnc):
                        ui.notify(f'Aplicacion no encontrada : {MnuFnc}', type='negative')
                        print(f'Aplicacion no encontrada : {MnuFnc}')
                        return

                    print(f'{Yos.Yos_TimeStamp()} -> {YosSes["Usr_Ipd"]} - {YosSes["Usr_Nik"]} : EJECUTA {MnuFnc}')

                    print(f'La aplicación {MnuFnc} se ejecutará en breve.')
                    ui.notify(f'La aplicación {MnuFnc} se ejecutará en breve.', type='info')

                    try:
                        if platform.system() == "Windows":
                            os.startfile(MnuFnc)
                        elif platform.system() == "Darwin":
                            subprocess.Popen(['open', MnuFnc]) # MacOs
                        else:
                            subprocess.Popen(['xdg-open', MnuFnc]) # Linux

                    except Exception as e:
                        # Si el comando falla (ej: no existe word.exe), avisamos por consola
                        print(f"Error al ejecutar comando externo: {e}")

                    return # Salimos para que no intente ejecutar el texto como función de Python

                if MnuFnc[:10] == "YosCmdWit:": # YosCmd: se pone ANTES del comando que queramos ejecutar
                    import subprocess
                    MnuFnc = MnuFnc.replace("YosCmdWit:", "").strip()

                    if not os.path.exists(MnuFnc):
                        ui.notify(f'Aplicacion no encontrada : {MnuFnc}', type='negative')
                        print(f'Aplicacion no encontrada : {MnuFnc}')
                        return

                    print(f'{Yos.Yos_TimeStamp()} -> {YosSes["Usr_Ipd"]} - {YosSes["Usr_Nik"]} : EJECUTA {MnuFnc}')

                    print(f'La aplicación {MnuFnc} se ejecutará en breve.')
                    ui.notify(f'La aplicación {MnuFnc} se ejecutará en breve.', type='info')

                    await asyncio.sleep(0.1)

                    try:
                        if platform.system() == "Windows":
                            proceso = subprocess.Popen(MnuFnc, shell=True)
                            proceso.wait()
                        elif platform.system() == "Darwin":
                            subprocess.run(['open', '-W', MnuFnc])
                        else:  # Linux
                            subprocess.run([MnuFnc], shell=True)

                        print('Su aplicación terminó')
                        ui.notify('Proceso finalizado.', type='positive')

                    except Exception as e:
                        # Si el comando falla (ej: no existe word.exe), avisamos por consola
                        print(f"Error al ejecutar comando externo: {e}")

                    return # Salimos para que no intente ejecutar el texto como función de Python

#               Mem_Yos_DefLib = MnuFnc.replace("()", "").strip()
                Mem_Yos_DefLib = MnuFnc.strip()
                print(f'Mem_Yos_DefLib = {Mem_Yos_DefLib} 171')

                # 1. FORZAR RECARGA: Borramos de la memoria builtins
                if hasattr(builtins, Mem_Yos_DefLib):
                    delattr(builtins, Mem_Yos_DefLib)

                # 2. CARGA DINÁMICA: No buscamos en 'Yos', vamos directo a la DB
                # Esto evita el "AttributeError: module 'Yos' has no attribute"
                await Yos.Yos_DefLib(Mem_Yos_DefLib)

                # 3. RECUPERACIÓN: Buscamos qué nos ha dejado Yos.Yos_DefLib en builtins
                func = getattr(builtins, Mem_Yos_DefLib, None)

                YosSes["Apl_Def"] = Mem_Yos_DefLib
                print(f'{Yos.Yos_TimeStamp()} -> {YosSes["Usr_Ipd"]} - {YosSes["Usr_Nik"]} : EJECUTA {YosSes["Apl_Def"]}')

                # 4. EJECUCIÓN ÚNICA
                if callable(func):

                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()

                else:
                    # --- AQUÍ ESTABA EL PROBLEMA ---
                    # Si el comando es un string como "Yos.Yos_AplCre()"
                    # evaluamos si el resultado de esa ejecución es algo que hay que esperar
                    try:
                        # Si el comando tiene un "=", solo evaluamos lo que hay a la derecha
                        if "=" in MnuFnc:
                            comando_limpio = MnuFnc.split("=")[1].strip()
                        else:
                            comando_limpio = MnuFnc.strip()

                        # Evaluamos la función para ver si es async
                        resultado = eval(comando_limpio, globals())

                        if asyncio.iscoroutine(resultado):
                            # Si es async, la ejecutamos de verdad con await
                            # Y si había una asignación, la hacemos manualmente
                            res_final = await resultado
                            if "=" in MnuFnc:
                                var_name = MnuFnc.split("=")[0].strip()
                                globals()[var_name] = res_final

                    except Exception:
                        # Si no es una función simple, vamos por el camino viejo
                        exec(MnuFnc, globals())

                YosSes["Apl_Def"] = YosCfg["Apl_Apl"]

            except Exception as e:
                ui.notify(f"Error: {e}", color='negative')

        Mem_Yos_DefFrm_Btn = Yos.Yos_DefFrm_Frm(YosCfg["Apl_Mnu"], al_seleccionar)
        Yos.Yos_DefFrm_BarEst_Frm()

# --- 3. LANZAMIENTO (Único bloque ui.run permitido) ---
if __name__ in {"__main__", "__mp_main__"}:
    import os
    from nicegui import app, ui
    import asyncio

    if not 'YosCfg' in globals():
        IniMain()

    # Silenciamos los errores de consola aquí
    import logging
    # Silenciamos uvicorn para evitar el ruido del WinError 10054
    logging.getLogger('uvicorn.error').setLevel(logging.CRITICAL)
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)
    # Cámbialo así para investigar:
#    logging.getLogger('asyncio').setLevel(logging.DEBUG)
#    logging.getLogger('uvicorn.error').setLevel(logging.DEBUG)

    secret = "yos_secret_2026_mtcyos"
#    secret = Yos.GenNomAch(16, "Yos_")
    puerto = int(YosCfg.get("Prt", 8080))

    mi_favicon = os.path.normpath(YosCfg["Apl_Dir"] + "//Img//favicon.ico")

    if YosCfg.get("Apl_Etn") == "Loc": # Modo Ventana (App local)
        app.on_connect(lambda: app.native.main_window.maximize())
        ui.run(
            native = True,
            reload = False,
            title = f'{YosCfg["Apl_Apl"]} - {YosCfg["Apl_Nom"]} - {YosCfg["Apl_Vsn"]}',
            storage_secret = secret,
            favicon = mi_favicon,
            reconnect_timeout = 10.0
        )

    elif YosCfg.get("Apl_Etn") == "Www": # Modo Web
        # Https
        cert = os.path.normpath(YosCfg["Apl_Dir"] + "//Cfg//www.pem")
        key = os.path.normpath(YosCfg["Apl_Dir"] + "//Cfg//www.key")

        ui.run(
            host = '0.0.0.0',
            port = puerto,
            reload = False,
            show =False,
            favicon = mi_favicon,
            title = f'{YosCfg["Apl_Apl"]} - {YosCfg["Apl_Nom"]} - {YosCfg["Apl_Vsn"]}',
            storage_secret=secret,
#            ssl_certfile=cert,
#            ssl_keyfile=key,
            reconnect_timeout=3.0
        )
