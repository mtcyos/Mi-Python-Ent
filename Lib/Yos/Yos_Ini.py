#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesos de inicio de la Aplicacion

@author: Miguel Tortosa
"""

import os
import sys
import platform
import importlib.util
import builtins

import Yos

from Yos import FrmWit, Yos_FrmCls, FrmCab

def AplIni():
    if YosCfg.get("YosAplIni_Ini") == "Inicializado":
        return
    YosCfg["YosAplIni_Ini"]="Inicializado"
    YosCfg.sync()

    print("  Inicializando AplIni()")
    # Deteccion de sistema Operativo
    YosCfg["Etn"] = platform.system()

    # Definimos la ruta base de los scripts (donde cuelga el Main)
    script_path = os.path.join(os.getcwd(), 'Script')

    # Configurar sys.path según el sistema
    Mem_Tit = f'{YosCfg["Apl_Apl"]} - {YosCfg["Apl_Nom"]} - {YosCfg["Apl_Vsn"]}'
    match YosCfg["Etn"]:
        case "Windows":
            sys.path.append(script_path + "\\")
            # Obtener el handle de la ventana actual (CMD)
            import ctypes
            import time

            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                # Rotulo en el Cmd
                ctypes.windll.kernel32.SetConsoleTitleW(Mem_Tit)
                # 1. Intentar el método normal
                ctypes.windll.user32.ShowWindow(hwnd, 3)# Maximizar la pantalla

                # 2. Refuerzo: Simular Windows + Flecha Arriba
                time.sleep(0.1) # Pausa mínima para que el sistema reaccione
                ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0) # Presiona Windows
                ctypes.windll.user32.keybd_event(0x26, 0, 2, 0) # Suelta Flecha Arriba
                ctypes.windll.user32.keybd_event(0x26, 0, 0, 0) # Presiona Flecha Arriba
                ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0) # Suelta Windows

                # Bloquear el botón de cierre (X)
                # Primero obtenemos el menú del sistema de esa ventana
                hMenu = ctypes.windll.user32.GetSystemMenu(hwnd, False)
                if hMenu:
                    SC_MINIMIZE = 0xF020 # Boton Minimizar
                    SC_MAXIMIZE = 0xF030 # Bloquear Maximizar
                    SC_RESTORE  = 0xF120 # <--- Esta es la clave para que no se pueda achicar
#                    SC_CLOSE = 0xF060 # Botón de cierre (X)
#                    ctypes.windll.user32.DeleteMenu(hMenu, SC_MINIMIZE, 0x00000000) # Bloquear Minimizar
#                    ctypes.windll.user32.DeleteMenu(hMenu, SC_MAXIMIZE, 0x00000000) # Bloquear Maximizar
#                    ctypes.windll.user32.DeleteMenu(hMenu, SC_RESTORE, 0x0) # Bloquea el "volver a tamaño normal"
#                    ctypes.windll.user32.DeleteMenu(hMenu, SC_CLOSE, 0x00000000)  # Bloquear el botón de cierre (X)

        case "Linux":
            sys.path.append(script_path + "/")
            os.system("echo -ne '\033]0;YosCtr - Linux\007'") # Cambiar título en Linux

        case "Darwin":  # MAC
            sys.path.append(script_path + "/")
            # En Mac se usa AppleScript o secuencias de escape para el título
            os.system("echo -n -e '\033]0;YosCtr - macOS\007'")

            try:
                # Intentamos maximizar, pero si falla, no rompemos el programa
                sys.stdout.write("\x1b[9;1t")
                sys.stdout.flush()
            except Exception:
                # Si falla, simplemente limpiamos pantalla y seguimos
                os.system("clear")

#       case "Darwin": # macOS
#           pass
#       case "iOS": # iOS or iPadOS
#           pass
        case _:
            print("Yos_Ini.AplIni()")
            print(f"Sistema Operativo {platform.system()} no implementado.")
            sys.exit(0)

    # Intentamos obtener el ancho de la terminal, por defecto 80
    try:
        import shutil
        YosCfg["Apl_Etn_Lon"] = shutil.get_terminal_size().columns
        YosCfg["Apl_Etn_Alt"] = shutil.get_terminal_size().lines
    except:
        YosCfg["Apl_Etn_Lon"] = 80
        YosCfg["Apl_Etn_Alt"] = 25

    # Definimos el Rotulo y la CABECERA
    from Yos import Frm_Cre_Rot_Cab
#    Frm_Cre_Rot_Cab()

    # Importo TODOS los .py de ./Script
    # 1. VALIDACIÓN INICIAL: ¿Existe la carpeta?
    if not os.path.exists(script_path):
        print(f"Error: No se encuentra la carpeta {script_path}")
        input("Pulse INTRO para salir...")
        sys.exit(0)

    # 2. Bucle de carga inteligente
    for filename in os.listdir(script_path):
        if filename.endswith('.py') and '_' in filename:
            module_name = filename[:-3]
            app_name = module_name.split('_')[0]

            spec = importlib.util.spec_from_file_location(module_name, os.path.join(script_path, filename))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 3. Creación/Recuperación del contenedor (YosCtr, YosGes, etc.)
                if not hasattr(builtins, app_name):
                    class AppContainer: pass
                    setattr(builtins, app_name, AppContainer())

                target_app = getattr(builtins, app_name)

                # 4. Registro de funciones (Solo las propias del archivo)
                for atributo in dir(module):
                    if not atributo.startswith("__"):
                        obj = getattr(module, atributo)
                        # Verificamos que sea ejecutable y que se haya definido EN ESTE archivo
                        if callable(obj) and getattr(obj, '__module__', None) == module_name:
                            setattr(target_app, atributo, obj)
                            #print(f"Cargado : {app_name}.{atributo}()")
                            YosCfg["Apl_Def"] += f"{app_name}.{atributo}()\n"

    # Nuevo formato para llamar los def
    # Archivo físico /Script | Función dentro del .py | Llamada desde Main.py
    # YosCtr_Abv.py           | def Abv_VfyDat():      | YosCtr.Abv_VfyDat()
    # YosCtr_Abv.py           | def Abv_Save():        | YosCtr.Abv_Save()
    # YosDfp_Clm.py           | def Clm_Calculo():     | YosDfp.Clm_Calculo()

    # ATENCION ESTO NO PUEDE EXISTIR YosCtr_Abv.py def Ipt(): y YosCtr_Clm.py def Ipt(): los del tienen que tener el prefijo de la aplicacion Abv_Ipt() y Clm_Ipt()

async def Apl_Frm_Fin(Fnc_Pgt=""):

    import builtins
    import os
    import sys
#    import asyncio
#    from nicegui import app, ui
    if YosCfg.get("Apl_Etn") != "Txt":
        from nicegui import app, ui

    # Mensaje de Confirmacion
    if Fnc_Pgt == "Si":
        if YosCfg.get("Apl_Etn") =="Www": # Web
            Mem_Txt = "¿ CERRAR SESIÓN ?"
        else:
            Mem_Txt = "¿ SALIR DEL SISTEMA ?"
        respuesta = await Yos.Yos_MsgPgt_Frm(Fnc_Tit="ATENCIÓN", Fnc_Msg = Mem_Txt)
        if not respuesta:
            return

    # Modo Terminal
    if YosCfg.get("Apl_Etn") =="Txt":
        print(f'{Yos.Yos_TimeStamp()} -> {YosSes["Usr_Ipd"]} - {YosSes.get("Usr_Nik")} : APLICACION FINALIZADA ({YosCfg.get("Apl_Etn")})')

        # Control de usuarios
        if YosCfg.get("Apl_UsrAcc") == "S":

            # Eliminar YosSes
            if hasattr(builtins, 'YosSes'): del builtins.YosSes

        # Eliminar YosCfg
        if "YosCfg_Ach" in YosCfg:
            NomAch = YosCfg["YosCfg_Ach"]
            try:
                YosCfg.close()
                for ext in [".dat", ".bak", ".dir"]:
                    if os.path.exists(NomAch + ext):
                        os.remove(NomAch + ext)
            except: pass
        if hasattr(builtins, 'YosCfg'): del builtins.YosCfg

        # Salir de la Aplicacion
        sys.exit(0)

    # MODO LOCAL
    elif YosCfg.get("Apl_Etn") =="Loc":
        print(f'{Yos.Yos_TimeStamp()} -> {YosSes["Usr_Ipd"]} - {YosSes.get("Usr_Nik")} : APLICACION FINALIZADA ({YosCfg.get("Apl_Etn")})')

        # Control de usuarios
        if YosCfg.get("Apl_UsrAcc") == "S":

            # Eliminar YosSes
            app.storage.user.clear()
            if hasattr(builtins, 'YosSes'): del builtins.YosSes

        # Eliminar YosCfg
        if "YosCfg_Ach" in YosCfg:
            NomAch = YosCfg["YosCfg_Ach"]
            try:
                YosCfg.close()
                for ext in [".dat", ".bak", ".dir"]:
                    if os.path.exists(NomAch + ext):
                        os.remove(NomAch + ext)
            except: pass
        if hasattr(builtins, 'YosCfg'):
            del builtins.YosCfg

        # Salir de la Aplicacion
        app.shutdown()

    # MODO WEB (Www)
    elif YosCfg.get("Apl_Etn") =="Www":
        print(f'{Yos.Yos_TimeStamp()} -> {YosSes["Usr_Ipd"]} - {YosSes.get("Usr_Nik")} : SESION FINALIZADA ({YosCfg.get("Apl_Etn")})')

        # Eliminar YosSes
        app.storage.user.clear()
        Yos.Apl_UsrAcc_UsrEliDat()

        # Control de usuarios
        if YosCfg.get("Apl_UsrAcc") == "S":
            ui.navigate.to('/login')
        else:
            ui.navigate.to('https://dfpges.upnfm.edu.hn/')

    else: # SIN Control de usuarios
        # salir sin hace nada
        pass

def Apl_Txt_Fin(Fnc_Msg="",Fnc_Pgt="" ):
    if not Fnc_Pgt:
        from prompt_toolkit import prompt, HTML
        Mem_Pgt = prompt(HTML('<orange>  ¿ Desea salir de la aplicación ? (S/N) : </orange>')).strip().upper()

        if Mem_Pgt == 'N':
            return

    if Fnc_Msg=="Msg":
        print(f'{Yos.Yos_TimeStamp()} -> {YosSes["Usr_Ipd"]} - {YosSes["Usr_Nik"]} : CERRO SESION')

    NomAch=YosCfg["YosCfg_Ach"]
    YosCfg.close()
    # Lista de las 3 extensiones que crea shelve en Windows
    for ext in [".dat", ".bak", ".dir"]:
        ach_a_borrar = NomAch + ext
        try:
            if os.path.exists(ach_a_borrar):
                os.remove(ach_a_borrar)
        except:
            # Si no puede borrarlo (o no existe), no hace nada
            pass

    import sys
    sys.exit(0)
    return

def Yos_MnuRec(Fnc_Mnu, Fnc_Tipo=""):
    if not Fnc_Mnu:
        Fnc_Mnu = YosCfg["Apl_Apl"]

    from Yos.Idd_BdtSvr import Cnx, SelTot, Cie, Sel
    Mem_Cnx = Cnx("YosCfg")
    Mem_Cur = Mem_Cnx.cursor()

    Mem_Sql = """
        SELECT * FROM Mnu
        WHERE cMnu = ?
            AND (cNul IS NULL OR cNul <> 'S')               -- 1. Salta los anulados
            AND (cEtn = ? OR cEtn = '' OR cEtn IS NULL)     -- 2. Filtra por Win, Linux o Mac
        ORDER BY cMnu, cNumOrd ASC;
    """
    Mem_Dat = SelTot(Mem_Cur, Mem_Sql, pParams=(Fnc_Mnu, YosCfg["Etn"]))
    if not Mem_Dat:
        print(f"ERROR: NO EXISTEN DATOS DE {Fnc_Mnu} en ./Bdt/YosCfg.Bdt")
        input("PULSE INTRO PARA CONTINUAR")
        sys.exit(1)

    # Construimos el diccionario con cNum como clave para mantener orden
    Mem_Dic_Tmp = {}

    # 2. La 'Pila' nos indica en qué nivel estamos trabajando
    # Empezamos en la raíz [Mem_Dic_Tmp]
    Pila = [Mem_Dic_Tmp]

    for row in Mem_Dat:
        # Ignorar si está anulado (aunque ya venga filtrado por SQL)
        if row["cNul"] == "S":
            continue

        # Extraemos datos básicos
        cOrd = str(row["cNumOrd"])
        cCod = row["cMnuCod"]
        cDes = row["cDes"] if row["cDes"] else ""
        cFnc = row["cFnc"] if row["cFnc"] else ""

        # A. INICIO DE NIVEL (Submenú)
        if cCod == "IniPop":
            # Creamos el nodo con su propio diccionario 'Sub'
            Nuevo_Sub = {"Txt": cDes, "Sub": {}}
            # Lo colgamos en el nivel actual de la pila
            Pila[-1][cOrd] = Nuevo_Sub
            # 'Entramos' en este nuevo diccionario para los siguientes registros
            Pila.append(Nuevo_Sub["Sub"])

        # B. FIN DE NIVEL (Cierre de submenú)
        elif cCod == "EndPop":
            if len(Pila) > 1:
                Pila.pop() # Volvemos al nivel anterior

        # C. SEPARADOR
        elif cCod == "Sep":
            Pila[-1][cOrd] = {"Txt": "", "Fnc": ""}

        # D. ITEM NORMAL O INYECCIÓN DE OTRO MENÚ
        else:
            if cCod == "MnuSub":
                # RECURSIVIDAD: Buscamos el submenú (ej: 'YosMnuEtn')
                Sub_Dic_Inyectado = Yos_MnuRec(Fnc_Mnu=cFnc, Fnc_Tipo="SubApp")

                # REGLA DE ORO: Si hay Texto en la celda 'TEXTO MENU'
                # lo convertimos en un grupo desplegable (PopUp)
                if cDes:
                    # Creamos el nivel "Padre" y le colgamos lo inyectado
                    Nuevo_Sub = {"Txt": cDes, "Sub": Sub_Dic_Inyectado}
                    Pila[-1][cOrd] = Nuevo_Sub
                else:
                    # Si no hay texto (como lo tienes ahora), se mezcla con la raíz
                    Pila[-1].update(Sub_Dic_Inyectado)
            else:
                # Item normal
                Pila[-1][cOrd] = {
                    "Txt": cDes,
                    "Fnc": cFnc,
                    "Cod": cCod
                }

    # Al finalizar el bucle, Mem_Dic_Tmp contiene todo el árbol jerárquico.

    Cie(Mem_Cnx)
    if Fnc_Tipo == "MnuGen":
        YosCfg["Apl_Mnu"] = Mem_Dic_Tmp
        YosCfg.sync()
    else:
        return Mem_Dic_Tmp
