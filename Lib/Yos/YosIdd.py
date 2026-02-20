# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 16:12:06 2025
@author: mtcyos

yosLib_Idd - Libreria de Gestion de Base de Datos
"""
import sys
import sqlite3 as Sql

# Agrega el directorio deseado a sys.path
# sys.path.append(os.path.abspath("../YosLib/"))

#import YosCtrApl
#import Yos

print("YosIdd")


def Bdt_Cnx():
    # Conecto al Servidor de los datos
    # PostgreSql
    # Sqlite
    try:
        with Sql.connect("YosSis.Bdt") as Mem_CnxDbt:
            Mem_CnxDbt_cur = Mem_CnxDbt.cursor()

            # Verifico si existe la Tabla Usr
            Mem_SqlTxt = 'SELECT name FROM sqlite_master '
            Mem_SqlTxt = Mem_SqlTxt + 'WHERE name="Usr"'
            Mem_CnxDbt_res = Mem_CnxDbt_cur.execute(Mem_SqlTxt)
            Mem_CnxDbt_Sql = Mem_CnxDbt_res.fetchone()
            print("24",Mem_CnxDbt_Sql)

            # No existe la Tabla
            if Mem_CnxDbt_Sql is None:
                Bdt_Cnx_CreTab()

    except Sql.Error as e:
        print(f"Error: {e}")
        sys.exit(1)

    Mem_Sal = "Ok"
#    print("Mem_Sal",Mem_Sal)

    return Mem_Sal


def Bdt_Cnx_Sql(Fnc_Sql):
#   print("Bdt_Cnx_Sql-"+Fnc_Sql)
    try:
        with Sql.connect("YosSis.Bdt") as Mem_CnxDbt:
            Mem_CnxDbt_cur = Mem_CnxDbt.cursor()
#            print("Fnc_Sql",Fnc_Sql)
            Mem_CnxDbt_res = Mem_CnxDbt_cur.execute(Fnc_Sql)
            Mem_CnxDbt_Sql = Mem_CnxDbt_res.fetchone()
#            print("58",Mem_CnxDbt_Sql)

    except Sql.Error as e:
        print(f"Error: {e}")
        sys.exit(1)

    return Mem_CnxDbt_Sql


def Bdt_Cnx_CreTab():
#   print("CREANDO TABLA Usr")
    try:
        with Sql.connect("YosSis.Bdt") as Mem_CnxDbt:
            Mem_CnxDbt_cur = Mem_CnxDbt.cursor()
            Mem_SqlTxt = ' CREATE TABLE "Usr" ('
            Mem_SqlTxt = Mem_SqlTxt+'"cNik"	VARCHAR(20) NOT NULL UNIQUE,'
            Mem_SqlTxt = Mem_SqlTxt+'"cNom"	VARCHAR(100) NOT NULL,'
            Mem_SqlTxt = Mem_SqlTxt+'"cPasMd5"	VARCHAR(32) NOT NULL,'
            Mem_SqlTxt = Mem_SqlTxt+'PRIMARY KEY("cNik")'
            Mem_SqlTxt = Mem_SqlTxt+');'
#           print("52",Mem_SqlTxt)
            Mem_CnxDbt_res = Mem_CnxDbt_cur.execute(Mem_SqlTxt)
            Mem_CnxDbt_Sql = Mem_CnxDbt_res.fetchone()
#           print("58",Mem_CnxDbt_Sql)

            # Admin
            Mem_SqlTxt = 'INSERT INTO Usr VALUES("Admin", "ADMINISTRADOR", "'
            Mem_SqlTxt = Mem_SqlTxt+Yos.Md5("mariSSa19661967")+'")'
#           print(Mem_SqlTxt)
            Mem_CnxDbt_res = Mem_CnxDbt_cur.execute(Mem_SqlTxt)
            Mem_CnxDbt_Sql = Mem_CnxDbt_res.fetchone()

            # mtcyos
            Mem_SqlTxt = 'INSERT INTO Usr VALUES("mtcyos", "MIGUEL TORTOSA", "'
            Mem_SqlTxt = Mem_SqlTxt+Yos.Md5("mariSSa274834")+'")'
#            print(vSqlTxt)
            Mem_CnxDbt_res = Mem_CnxDbt_cur.execute(Mem_SqlTxt)
            Mem_CnxDbt_Sql = Mem_CnxDbt_res.fetchone()
#           print("TABLA Usr CREADA")

    except Sql.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
