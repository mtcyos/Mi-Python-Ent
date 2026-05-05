#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
Datos de Configuraacion de la Aplicacion

@author: Miguel Tortosa
"""
import os
import string
import random
import shelve
import builtins # Lo usamos para poder usar una VARIABLES GLOBAL
import platform
from datetime import datetime
import tempfile

import Yos

def GenNomAch(longitud=10, Prefijo="YosCfg_"):
    """Genera un nombre de archivo aleatorio con letras y números."""
    caracteres = string.ascii_letters + string.digits # Letras (mayús/minús) y números
    nombre_base = ''.join(random.choice(caracteres) for i in range(longitud))
    return f"{Prefijo}{nombre_base}"

def obtener_id_unico():
    import psutil # Librería estándar para procesos
    p = psutil.Process(os.getpid())
    while p.parent() and "python" in p.parent().name().lower():
        p = p.parent()
    return p.pid

#NomAch = os.path.join(tempfile.gettempdir(), f"YosCfg_P{obtener_id_unico()}")
#builtins.YosCfg = shelve.open(NomAch)
#YosCfg["YosCfg_Ach"] = NomAch

def Yos_Cfg():
    if 'YosCfg' in globals() or 'YosCfg' in locals():
        return

    print("  Inicializando Yos_Cfg()")

    # Creo el archivo de la Configuracion
    NomAch = os.path.join(tempfile.gettempdir(), GenNomAch(24, "YosCfg_Python_"))
    builtins.YosCfg = shelve.open(NomAch)
    YosCfg["YosCfg_Ach"]=NomAch

    YosCfg["YosCfg_Ini"]="Inicializado"
    YosCfg.sync()

    # DEJAMOS LAS RUTAS FUERA PARA EVITAR EL KEYERROR
#    YosCfg["Apl_Dir"] = os.getcwd() + "\\"
#    YosCfg["Yos_Dir"] = os.path.abspath(YosCfg["Apl_Dir"] + "../Lib/Yos/")
#    YosCfg.sync()


    YosCfg["Dbg"]="" # MODO DEPURACION S="Completo"

    # Entorno de la Aplicacion
    YosCfg["Etn"]       = platform.system() # "Windows", "Linux", "Darwin"
    YosCfg["Etn_Des"]   = platform.platform()

    YosCfg["Etn_Tmp"]   = tempfile.gettempdir()

    # Aplicacion
    YosCfg["Apl_Apl"]       = os.path.basename(os.getcwd())
    # YosCfg["Apl_Tit"]       ="" # TITULO de la Aplicacion ****  Se usa YosCfg["Apl_Nom"]       ="" # Nombre EXTENDIDO de la aplicacion

    YosCfg["Apl_Etn"]       ="" # Entorno de la Aplicacion Txt=Texto, Www=Web
    YosCfg["Apl_Etn_Lon"]   = 0 # Si el Entorno es Txt, Ancho de la pantalla (WX) (Width)(Longitud), no poner nada, se calcula
    YosCfg["Apl_Etn_Alt"]   = 0 # Si el Entorno es Txt, Alto de la pantalla (HY) (Height) (Longitud), no poner nada, se calcula

    YosCfg["Apl_Rot"]       = "" # Rotulo del nombre de la Aplicacion
    YosCfg["Apl_Cab"]       = "" # Cabecera  Rotula + Datos de la apliccion

    YosCfg["Apl_Etn_Let"]   ="" #"dos_rebel","banner3"# Si el Entorno es Txt, Tipo de letra para el Rotulo, Modulo pyfiglet
    YosCfg["Apl_Nom"]       ="" # Nombre EXTENDIDO de la aplicacion
    YosCfg["Apl_Vsn"]       ="" # Version de la Aplicacion
    YosCfg["Apl_Dir"]       = os.getcwd()  +"\\" # Directorio de la Aplicacion
    YosCfg["Apl_Dir_Bdt"]   = YosCfg["Apl_Dir"] +"Bdt\\"
    YosCfg["Apl_Cpy"]       ="" # Copyright de la aplicacion
    YosCfg["Apl_CpyEml"]    ="" # Email del Autor de la Aplicacion
    YosCfg["Apl_Res"]       ="" # Documento de DE RESPONSABILIDAD
    YosCfg["Apl_Mnu"]       ="" # Menu de la Aplicacion Mnu.py

    YosCfg['Apl_TitSub'] = "" # Es para el menu , Muestra TITUTLO DEL SCRIPT , nombre del Script, no poner nada, se modifica  en los script

    YosCfg["Apl_Def"] = "" # Guarda la lista de las Def del .py cargadas


    # YosLib
    YosCfg["Yos_Apl"]="YosLib"
    YosCfg["Yos_Nom"]="LIBRERIA DE PROPOSITO GENERAL"
    YosCfg["Yos_Vsn"]="2026.04"
    YosCfg["Yos_CpyEml"]="mtcyos@yahoo.es"
    YosCfg["Yos_Cpy"]=YosCfg["Yos_Vsn"][:4]+" © Miguel Tortosa"

    YosCfg["Yos_Dir"] = os.path.abspath(YosCfg["Apl_Dir"]+"../Lib/Yos/")
    # Bases de Datos "Bdt"
    # Imagenes "Img/"
    # Sql "Sql"
    # Usuario
#     import getpass
#     YosCfg["Usr_Nik"] = getpass.getuser() # Usuario # **************************************************************** Modificar cuando halla MultiUsuario
#     YosCfg["Usr_Nom"] = "" # Nombre
#     YosCfg["Usr_Pas"] = "" # Contraseña en md5
#     YosCfg["Usr_Niv"] = "" # Nivel del Usuario
#     YosCfg["Usr_Ipd"] = "" # Direccion Ip del usuario
    YosCfg["Usr_NumMaxAcc"] = 3 # Numero de intentos de Acceso

    from Yos.Idd_BdtSvr import Cnx, Sel, SelTot, Cie

    ################################### RECURERAMOS YosLib.bdt
    #YosCfg["Dbg"]="S"
    Mem_Cnx_YosCfg = Cnx("YosLib")
    Mem_Cur_YosCfg = Mem_Cnx_YosCfg.cursor()

    ############################## Recuperamos los datos de las bases de datos YosCfg.Bdt
    Mem_Sql = "SELECT * FROM Bdt"
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql, pParams=())

    if Mem_Dat is None:
        print("El SELECT no devolvió resultados (está vacío).")

    for Mem_Uni in Mem_Dat:
        # Acceso por nombre de columna
        Mem_Svr = str(Mem_Uni["cSvr"]).strip()

        if Mem_Uni["cDir"] == "«YosLib»":
    #        Mem_Dir = os.path.abspath(os.path.join(YosCfg["Yos_Dir"], "_Bdt"))
            Mem_Dir = YosCfg["Yos_Dir"]
        else:
            Mem_Dir = Mem_Uni["cDir"]

        YosCfg[f"Apl_Bdt_{Mem_Svr}_Tip"] = Mem_Uni["cSvrTip"]
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Dir"] = Mem_Dir
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Usr"] = Mem_Uni["cUsr"]
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Pas"] = Mem_Uni["cPas"]
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Bdt"] = Mem_Uni["cBdt"]
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Obs"] = Mem_Uni["cObs"]

    ############################## Recuperamos los datos de las bases de datos YosCfg.Dat
    Mem_Sql = "SELECT * FROM Dat"
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql, pParams=())

    if Mem_Dat is None:
        print("El SELECT no devolvió resultados (está vacío).")

    for Mem_Uni in Mem_Dat:
        YosCfg[f"{Mem_Uni['cNom']}"] = Mem_Uni["cVal"]
        YosCfg[f"{Mem_Uni['cNom']+'_Tip'}"] = Mem_Uni["cTipClm"]
        YosCfg[f"{Mem_Uni['cNom']+'_Lon'}"] = Mem_Uni["cLonClm"]

    Cie(Mem_Cnx_YosCfg)

    ############################## Ponemos los datos de la Aplicacion YosCfg.Apl
    #input("recuperamos YosCfg dESDE Yos_Cfg")

    Mem_Cnx_YosCfg = Cnx("YosCfg")
    Mem_Cur_YosCfg = Mem_Cnx_YosCfg.cursor()

    import sys
    #YosCfg["Apl_Apl"], Mem_Dat = os.path.splitext(os.path.basename(sys.argv[0])) # Recupero el nombre del Script Inicial
    YosCfg["Apl_Apl"]=Mem_Ini_AplCod

    Mem_Sql = "SELECT * FROM Apl LIMIT 1"
    Mem_Dat = Sel(Mem_Cur_YosCfg, Mem_Sql)

    if Mem_Dat is None:
        print(f"ERROR: NO EXISTEN INFORMACION DE LA APLICACION {YosCfg["Apl_Apl"]} EN YosCfg")
        input("PULSE INTRO PARA FINALIZAR")
        sys.exit(1)

    YosCfg["Apl_Etn"]       = Mem_Dat["cEtnApl"] # "Txt" # "Txt"=Texto Modo Terminal, "Www"=Web
    YosCfg["Apl_Etn_Let"]   = Mem_Dat["cEtnAplLet"] # "dos_rebel" #"banner3"# Si el Entorno es Txt, Tipo de letra para el Rotulo, Modulo pyfiglet
    YosCfg["Apl_Nom"]       = Mem_Dat["cNom"] # Control central entorno Yos" # Nombre EXTENDIDO de la aplicacion
    YosCfg["Apl_Vsn"]       = Mem_Dat["cVsn"] # "2026.01" # Version de la Aplicacion
    YosCfg["Apl_Cpy"]       = Mem_Dat["cCpy"] # YosCfg["Apl_Vsn"][:4]+" © Miguel Tortosa - "+YosCfg["Apl_CpyEml"] # Copyright de la aplicacion
    YosCfg["Apl_CpyEml"]    = Mem_Dat["cCpyEml"] # "mtcyos@yahoo.es" # Email del Autor de la Aplicacion

    ############################## Recuperamos los datos de las bases de datos YosCfg.Bdt
    Mem_Sql = "SELECT * FROM Bdt"
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql, pParams=())

    if Mem_Dat is None:
        print("El SELECT no devolvió resultados (está vacío).")

    for Mem_Uni in Mem_Dat:
        # Acceso por nombre de columna
        Mem_Svr=Mem_Uni["cSvr"] #Mem_Uni["cSvr"][3:]
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Tip"]= Mem_Uni["cSvrTip"]
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Dir"]= Mem_Uni["cDir"]
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Usr"]= Mem_Uni["cUsr"]
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Pas"]= Mem_Uni["cPas"]
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Bdt"]= Mem_Uni["cBdt"]
        YosCfg[f"Apl_Bdt_{Mem_Svr}_Obs"]= Mem_Uni["cObs"]

    ############################## Recuperamos los datos de las bases de datos YosCfg.Dat
    Mem_Sql = "SELECT * FROM Dat"
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql, pParams=())

    if Mem_Dat is None:
        print("El SELECT no devolvió resultados (está vacío).")

    for Mem_Uni in Mem_Dat:
        # Acceso por nombre de columna

        """
        "cNom"  VARCHAR(60),
        "cDes"  VARCHAR(100),
        "cTipClm"   VARCHAR(1),
        "cVal"  VARCHAR(253),
        "cValPmd"   VARCHAR(100),
        "cLonClm"   VARCHAR(3),
        "cAli"  VARCHAR(1),
        "cObs"  VARCHAR(100),
        "cObsSis"   VARCHAR(100),
        """

        YosCfg[f"{Mem_Uni['cNom']}"]= Mem_Uni["cVal"]
        YosCfg[f"{Mem_Uni['cNom']+'_Tip'}"]= Mem_Uni["cClmTip"]
        YosCfg[f"{Mem_Uni['cNom']+'_Lon'}"]= Mem_Uni["cClmLon"]

    Cie(Mem_Cnx_YosCfg)

    ############################## Recuperamos el menu YosCfg.Mnu
    Yos.Yos_MnuRec(YosCfg["Apl_Apl"],"MnuGen")  # Menu General ("Nombre_de_la_Aplciacion" ,"MnuGen" lo guarda en YosCfg["Apl_Mnu"] , si no lo debuelve en return

    #input(dict(YosCfg))
    #Mem_Sub="Apl_"
    """
    Mem_Sub=""
    print("--------------------------------------------------")
    print(f"{Mem_Sub}")
    print("--------------------------------------------------")
    print({k: v for k, v in YosCfg.items() if k.startswith("Apl_Bdt_")})
    print("\n".join([f"{k}: {v}" for k, v in YosCfg.items() if k.startswith(Mem_Sub)]))
    print("--------------------------------------------------")
    input("Fin")
    """
    YosCfg.sync()
