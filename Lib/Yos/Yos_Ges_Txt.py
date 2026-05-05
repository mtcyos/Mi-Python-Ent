#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Miguel Tortosa

Yos_Ges_Txt.py  .Py donde estan todas las Def _Txt

Gestión Definiciones Txt, para el entorno Texto con base en prompt_toolkit

Estructura nombre Def

PREFIJO DESCRIPCION
Yos_    Def de uso General

SUFIJO
_Txt -> Modo Texto -> Terminal / Consola

"""

import os
################################################################### Inicio Def ##########################################################

################################# A REVISAR #################################################################
def Yos_EntDat_Txt(**Fnc_Dic):
    # Extraemos los valores del diccionario
    Mem_Dat = Fnc_Dic.get("Dat", "")
    Fnc_Vfy = Fnc_Dic.get("Vfy", "")
    Fnc_Rot = Fnc_Dic.get("Rot", "Dato")
    Fnc_Tip = Fnc_Dic.get("Tip", "C")
    Fnc_Lon = Fnc_Dic.get("Lon", 0)

    while True:
        # 1. Pedimos el dato (Si es Pas, ocultamos, si no, normal)
        if "Pas" in Fnc_Vfy:
            from Yos import Yos_Pas
            print(f"{Fnc_Rot}: ", end="", flush=True)
            Mem_Val = Yos_Pas()
        else:
            Mem_Val = input(f"{Fnc_Rot} [{Mem_Dat}]: ") or Mem_Dat

        # 2. Llamamos al verificador (El cerebro que ya hicimos)
        # Importante: El verificador nos devuelve el dato ya modificado (Myu, Cap, etc.)
        Mem_Val, Mem_Err = Yos_EntDat_Vfy(Mem_Val, Fnc_Vfy, Fnc_Rot, Fnc_Tip, Fnc_Lon)

        if not Mem_Err:
            return Mem_Val # Dato correcto, salimos
        else:
            print(f" >> {Mem_Err}") # Error, el bucle sigue


def Yos_FrmCls():

    os.system('cls' if os.name == 'nt' else 'clear')

def FrmWit(Fnc_Txt="",Fnc_Wit=0):
    from prompt_toolkit import print_formatted_text, HTML
    from pytimedinput import timedInput

    if Fnc_Txt:
        print_formatted_text(HTML(f"\n<ansigreen>{Fnc_Txt}</ansigreen>"))

    # Espera a que pulses Intro o que pase el Tiempo asignado
    Fnc_Txt = "<orange>\n  Pulse INTRO para continuar </orange>"
    # f"{Fore.YELLOW}\n Pulse INTRO para continuar"
    if Fnc_Wit==0:
        print_formatted_text(HTML(Fnc_Txt), end="")
        input("")
    else:
        Fnc_Txt = Fnc_Txt + f" <orange>({Fnc_Wit} Seg)</orange> " #f" ({Fnc_Wit} Seg) "
        print_formatted_text(HTML(Fnc_Txt), end="")
        timedInput(prompt="", timeout=Fnc_Wit)


def FrmLin(Fnc_Txt, Fnc_Pos=""): # Formatea un linea
#    print(f"{Fore.RED}{FrmLin('ACCESO RESTRINGIDO - POR FAVOR IDENTIFÍQUESE', '')}{Style.RESET_ALL}") # A la Izquierda
#    print(f"{Fore.RED}{FrmLin('ACCESO RESTRINGIDO - POR FAVOR IDENTIFÍQUESE', 'C')}{Style.RESET_ALL}") # Al Centro
#    print(f"{Fore.RED}{FrmLin('ACCESO RESTRINGIDO - POR FAVOR IDENTIFÍQUESE', 'D')}{Style.RESET_ALL}") # a la Derecha
#    print(f"{Fore.RED}{FrmLin('ACCESO RESTRINGIDO - POR FAVOR IDENTIFÍQUESE', 88)}{Style.RESET_ALL}") # a 88 espacion de la Derecha
#    input(f"\n{Fore.YELLOW}{FrmLin('Pulse INTRO para continuar', 8)}{Style.RESET_ALL}")
    match Fnc_Pos:
        case "C": # centro
                Fnc_Pos = YosCfg["Apl_Etn_Lon"]
                Fnc_Pos = int((Fnc_Pos -len(Fnc_Txt)) /2)
                return (" " * int(Fnc_Pos)) + Fnc_Txt
#                Mem_Txt=f"{Fnc_Txt:^{Mem_Cen}}"
#                return Mem_Txt
        case "D": # Derecha
#                Mem_Cen=YosCfg["Apl_Etn_Lon"]
#                Mem_Txt=f"{Fnc_Txt:>{int(Mem_Cen)}}"
#                return Mem_Txt
                Fnc_Pos = YosCfg["Apl_Etn_Lon"]
                Fnc_Pos = Fnc_Pos -len(Fnc_Txt)
                return (" " * int(Fnc_Pos)) + Fnc_Txt


        case n if str(Fnc_Pos).isdigit(): # Es numerico
            return (" " * int(Fnc_Pos)) + Fnc_Txt

        case _:
            return Fnc_Txt

def Frm_Cre_Rot_Cab():
    # Creamos en Rotulo y la Cabacera de la aplicacion

#    from Yos import MstFncLin
#    input(MstFncLin(FncNiv="All"))

    Mem_Cab = ""
    # Genero el Rotulo del nombre de la aplicacion
    import pyfiglet
    import shutil
    # 1. Generamos el banner y aplicamos el strip (tu parámetro -s)
    Rotulo = pyfiglet.figlet_format(YosCfg["Apl_Apl"],font = YosCfg["Apl_Etn_Let"]).strip()
    Rotulo = " " +Rotulo
    lineas = Rotulo.splitlines()
    ancho_dibujo = max(len(linea) for linea in lineas)

    # Añadimos un margen interno de seguridad (ej: 6 espacios)
    ancho_total = ancho_dibujo + 0

    borde_S = "╔" + "═" * (ancho_total + 2) + "╗"
    borde_I = "╚" + "═" * (ancho_total + 2) + "╝"
    contenido = [f"║ {linea.ljust(ancho_total)} ║" for linea in lineas]
    dibujo_ascii = [borde_S] + contenido + [borde_I]

    YosCfg["Apl_Rot"] = dibujo_ascii # Rotulo del nombre de la Aplicacion

#    return lineas
    #print_formatted_text(HTML(f"<ansiyellow>{FrmLin('CONFIGURACIÓN DEL ENTORNO DE LA APLICACION', 'C')}</ansiyellow>"))
    # 3. Centramos cada línea individualmente

#    print("\n".join(lineas))
    Mem_MaxLon = (max(len(l) for l in lineas) if lineas else 0)
#    print(f"Mem_MaxLon {Mem_MaxLon}")
    # ajustos a todos al mismo ancho
    lineas_v = dibujo_ascii
    lineas = []
    for l in lineas_v:
        espacios_izq = int(Mem_MaxLon - len(l))
#        print(f"Mem_MaxLon={Mem_MaxLon} espacios_izq={espacios_izq}")
        nueva_linea = ( l + " " * espacios_izq)
        lineas.append(nueva_linea)

    Mem_MaxFrm = YosCfg["Apl_Etn_Lon"]
#    print(f"Mem_MaxFrm={Mem_MaxFrm} Mem_MaxLon={Mem_MaxLon}")
#    print(len(lineas))
    lineas_v = lineas
    lineas = []
    for l in lineas_v:
#        print(f"Mem_MaxFrm = {Mem_MaxFrm} Len =  {(len(l) // 2)}")
        espacios_izq = int((Mem_MaxFrm - len(l)) // 2)
        nueva_linea = (" " * espacios_izq) + l
        lineas.append(nueva_linea)
    Rotulo_Final = "\n".join(lineas)
#    print("\n".join(lineas))
#    print()
#    print(lineas[1])

    # pongo en Usuario
    if YosCfg.get("Apl_UsrAcc") == "S":
        Mem_Ini = 5
        Mem_Txt =f"Usuario :  {YosSes['Usr_Nik']}"
        Mem_Fin = len(Mem_Txt)
        lineas[0] = lineas[0][:Mem_Ini] + Mem_Txt + lineas[0][Mem_Ini + Mem_Fin:]

#·    from prompt_toolkit import print_formatted_text, HTML
#    for linea in lineas:
#        print_formatted_text(HTML(f"<orange>{linea}</orange>"))
    YosCfg["Apl_Cab"] = lineas # Cabecera  Rotula + Datos de la apliccion

def FrmCab(Fnc_Dat=None):
    # Imprimimos la cabecero o el rotulo

    # Fnc_Dat = Rot -> Rotulo
    #         = Cab -> Cabecera

    match Fnc_Dat:
        case "Rot":
            lineas_cab_lista = YosCfg["Apl_Rot"]
        case "Cab":
            lineas_cab_lista = YosCfg["Apl_Cab"]
        case _:
            input("Entorno de la Aplicacion inexisente")


#    lineas_cab_lista.insert(0, " " * (YosCfg["Apl_Etn_Lon"] - 1))
    Mem_Cab_Final = '\n'.join(lineas_cab_lista)         # Convertimos la lista en un solo string para el control visual


    from prompt_toolkit import print_formatted_text, HTML
    for linea in lineas_cab_lista:
        print_formatted_text(HTML(f"<orange>{linea}</orange>"))

    # Creamos la Window que respetará tus espacios y el logo a la derecha
#    lbl_Cab = Window(
#        content=FormattedTextControl(
#            HTML(f"<orange>{Mem_Cab_Final}</orange>")
#        ),
#        height=len(lineas_cab_lista),
#        wrap_lines=False
#    )
####################################################################################################


