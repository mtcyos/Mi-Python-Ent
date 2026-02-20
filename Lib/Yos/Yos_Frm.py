# -*- coding: utf-8 -*-
"""
Control Pantallas/Ventanas

@author: Miguel Tortosa
"""
import os
from pytimedinput import timedInput

def FrmCls():

    match YosCfg["Apl_Etn"]:
        case "Txt":
            match YosCfg["Etn"]:
                case "Windows":
                    pass
                    os.system('cls')

                case "Linux":
                    pass
                    os.system('clear')

                case _:
                    pass

        case "Www":
            print("BORRO pantalla  WEB")
        case _:
            input("Entorno de la Aplicacion inexisente")

def FrmWit(Fnc_Txt="",Fnc_Wit=0):
    if Fnc_Txt:
        Fnc_Txt=f"{Fnc_Txt}\nPulse INTRO para continuar "
    else:
        Fnc_Txt=f"Pulse INTRO para continuar "

    # Espera a que pulses Intro o que pase el yiempo asignado
    if Fnc_Wit==0:
        input(Fnc_Txt)
    else:
        Fnc_Txt=Fnc_Txt+f"({Fnc_Wit} Seg) "
        timedInput(prompt=Fnc_Txt, timeout=Fnc_Wit)

