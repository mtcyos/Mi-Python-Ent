#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   Yos_Acd.py
   INFORMACION DE LA APLICACION Y MOTOR DE Mem_MsgS

   Copyright (c) 2026 Miguel Tortosa
   Licenciado bajo la Licencia MIT.
"""
# print("1. --- LISTADO DE PARAMETROS ---")
# print(dict(YosCfg))
# ... (Tus comentarios de depuración se mantienen intactos) ...


def Acd():
    import builtins
    from Yos import FrmMsg

    YosCfg = builtins.YosCfg
    Mem_Tab = "&nbsp;&nbsp;&nbsp;&nbsp;"

    Mem_Dat = f'<b>ENTORNO</b><br>{Mem_Tab}S.O. : {YosCfg["Etn"]} - {YosCfg["Etn_Des"]}<br><br>'
    Mem_Dat = Mem_Dat + f'<b>APLICACION</b><br>{Mem_Tab}{YosCfg["Apl_Apl"]}<br>{Mem_Tab}{Mem_Tab}{YosCfg["Apl_Nom"]}<br>{Mem_Tab}{Mem_Tab}Ver. {YosCfg["Apl_Vsn"]}<br>{Mem_Tab}{Mem_Tab}{YosCfg["Apl_Cpy"]}<br>{Mem_Tab}{Mem_Tab}email : {YosCfg["Apl_CpyEml"]}<br><br>'
    Mem_Dat = Mem_Dat + f'<b>LIBRERIAS</b><br>{Mem_Tab}{YosCfg["Yos_Apl"]} - {YosCfg["Yos_Nom"]} - Ver. {YosCfg["Yos_Vsn"]}<br>{Mem_Tab}{Mem_Tab}{YosCfg["Yos_Cpy"]}'

    FrmMsg(Fnc_Tit="ACERCA DE ...", Fnc_Msg=Mem_Dat, Fnc_Tip="Inf")

def AcdRes():
    import builtins
    from Yos import FrmMsg

    YosCfg = builtins.YosCfg
    Mem_Dat = f'{YosCfg["Apl_Apl"]}<br>{YosCfg["Apl_Nom"]}<br><br>Licenciado bajo la Licencia MIT.<br><br>Consulte el archivo LICENCIA en la raíz del proyecto para más información'

    FrmMsg(Fnc_Tit="AVISO DE DESCARGO DE RESPONSABILIDAD", Fnc_Msg=Mem_Dat, Fnc_Tip="Inf", Ancho="500px")

