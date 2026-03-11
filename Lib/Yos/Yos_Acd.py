#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
   Yos_Acd.py
   INFORMACION DE LA APLICACION

   Copyright (c) 2026 Miguel Tortosa

   Licenciado bajo la Licencia MIT.

   Consulte el archivo LICENCIA en la raíz del proyecto para más información.
"""
# print("1. --- LISTADO DE PARAMETROS ---")
# print(dict(YosCfg))
# for i, (clave, valor) in enumerate(YosCfg.items(), 1):
#     print(f"{i:03d}. {clave:.<20}: {valor}")
# input("SEGUIR")
#print(dict(YosCfg))
#print("--------------------------------------------------")
#input({k: v for k, v in YosCfg.items() if k.startswith("Apl_Bdt_")})
#print("--------------------------------------------------")

from colorama import Fore, Back, Style

from Yos.Yos_Frm import FrmCls, FrmWit, FrmLin
from Yos.Yos_Ini import AplIni

def Acd():
    if YosCfg["Dbg"]=="S": print("******** Yos.Acd() ********")
    Acd=[]
    # Entorno
    Acd.append("ACERCA DE ...")
    Acd.append("")

    Acd.append("ENTORNO")
    Acd.append("   S.O. : " +YosCfg["Etn"]+" - "+YosCfg["Etn_Des"])
    Acd.append("")

    # Aplicacion
    Acd.append("APLICACION")
    Acd.append("    "+YosCfg["Apl_Apl"])
    Acd.append("        "+YosCfg["Apl_Nom"])
    Acd.append("        Ver. "+YosCfg["Apl_Vsn"])
    Acd.append("        "+YosCfg["Apl_Cpy"])
    Acd.append("        email : "+YosCfg["Apl_CpyEml"])
    Acd.append("")

    # YosLib
    Acd.append("LIBRERIAS")
    Acd.append("   "+YosCfg["Yos_Apl"]+" - "+YosCfg["Yos_Nom"]+" - Ver. "+YosCfg["Yos_Vsn"])
    Acd.append("        "+YosCfg["Yos_Cpy"])
    Acd.append("")

    if YosCfg["Apl_Etn"]=="Txt":
        FrmCls()
        AplIni()
        nLon=64
        Mem_nLon=nLon-4
        print(f"{'*' * nLon:^{YosCfg["Apl_Etn_Lon"]}}")
        for lin in Acd:
            Text=f"* {lin:<{Mem_nLon}} *"
            print(f"{Text:^{YosCfg["Apl_Etn_Lon"]}}")
        print(f"{'*' * nLon:^{YosCfg["Apl_Etn_Lon"]}}")
#        Acd_Res("Dir")
        FrmWit()
        FrmCls()

    return Acd

def AcdRes(Fnc_Dat=""):
    # Documento de DE RESPONSABILIDAD
    YosCfg["Apl_Res"]=[
        "         *** AVISO DE DESCARGO DE RESPONSABILIDAD ***",
        "",
        YosCfg["Apl_Apl"],
        YosCfg["Apl_Nom"],
        "",
        "Licenciado bajo la Licencia MIT.",
        "",
        "Consulte el archivo LICENCIA en la raíz del proyecto ",
        "para más información."
#        "Este software es de código abierto y se distribuye 'TAL CUAL'.",
#        "El autor no se hace responsable por daños o pérdida de datos.",
#        "Uso bajo su propio riesgo."
    ]
    if YosCfg["Apl_Etn"]=="Txt":
        if not Fnc_Dat=="Dir":
            FrmCls()
            AplIni()
        nLon=66
        Mem_nLon=nLon-4
        print(f"{'*' * nLon:^{YosCfg["Apl_Etn_Lon"]}}")
        for lin in YosCfg["Apl_Res"]:
            Text=f"* {lin:<{Mem_nLon}} *"
            print(f"{Text:^{YosCfg["Apl_Etn_Lon"]}}")
        print(f"{'*' * nLon:^{YosCfg["Apl_Etn_Lon"]}}")
        if not Fnc_Dat=="Dir":
            FrmWit()
            FrmCls()

    return YosCfg["Apl_Res"]
