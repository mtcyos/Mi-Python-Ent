# -*- coding: utf-8 -*-
"""
Control Pantallas/Ventanas

@author: Miguel Tortosa
"""
import os
from pytimedinput import timedInput

def FrmCls():

    match YosCfg["Apl_Etn"]:
        case "Txt" | "Gui":
            match YosCfg["Etn"]:
                case "Windows":
                    pass
                    os.system('cls')

                case "Linux":
                    pass
                    os.system('clear')

                case _:
                    pass

        case _:
            input("Entorno de la Aplicacion inexisente")

def FrmWit(Fnc_Txt="",Fnc_Wit=0):
    from colorama import Fore, Back, Style

    if Fnc_Txt:
        print(f'\n{Fnc_Txt}')
    # Espera a que pulses Intro o que pase el Tiempo asignado
    Fnc_Txt = f"{Fore.YELLOW}\n Pulse INTRO para continuar"
    if Fnc_Wit==0:
        input(f"{Fnc_Txt}{Style.RESET_ALL}")
    else:
        Fnc_Txt = Fnc_Txt + f" ({Fnc_Wit} Seg) "
        timedInput(prompt=f"{Fnc_Txt}", timeout=Fnc_Wit)

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

