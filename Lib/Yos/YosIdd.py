#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 16:12:06 2025
@author: mtcyos

yosLib_Idd - Libreria de Gestion de Base de Datos
"""
import sys
import sqlite3 as Sql

################################################################### Inicio Def ##########################################################

################################# A REVISAR #################################################################


# Función Universal de Unicidad
def Idd_Vfy_Unc(Fnc_Svr, Fnc_Tab, Fnc_Clm, Fnc_Dat):
    from Yos import Cnx, Sel, Cie

    Msg_Err = ""
    # Conexión estándar para cualquier motor
    Mem_Cnx = Cnx(Fnc_Svr, Fnc_Mod="ro")
    Mem_Cur = Mem_Cnx.cursor()

    # Buscamos si existe al menos un registro con ese valor
    # El LIMIT 1 funciona en SQLite, Postgres y MariaDB (en MSSQL se ignora o se adapta)
    Mem_Sql = f"SELECT {Fnc_Clm} FROM {Fnc_Tab} WHERE {Fnc_Clm} = ?"
    Mem_Par = (Fnc_Dat,)

    # Sel ejecuta el fetch
    Mem_Res = Sel(Mem_Cur, Mem_Sql, Mem_Par)

    # LÓGICA UNIVERSAL:
    # Si Mem_Res tiene CONTENIDO (sea Row, lista, tupla o int), significa que NO ES ÚNICO
    if Mem_Res:
        Msg_Err = f"VALOR '{Fnc_Dat}' YA EXISTE"

    Cie(Mem_Cnx)
    return Msg_Err
