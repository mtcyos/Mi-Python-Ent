#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import os

"""
   Idd_BdtSvr.py
   ACCESO AL SERVIDOR

   Copyright (c) 2026 Miguel Tortosa

   Licenciado bajo la Licencia MIT.

   Consulte el archivo LICENCIA en la raíz del proyecto para más información.
"""
"""
    | Motor de BD   | Librería Python   | Tipo          | Portabilidad
    | MariaDB/MySQL | pymysql           | Python Puro   | Excelente (Win, Linux, Mac)
    | PostgreSQL    | pg8000            | Python Puro   | Excelente (Win, Linux, Mac)
    | MsSQL         | pypyodbc          | Python Puro   | Buena (Requiere Driver ODBC)
    | Dbf           | dbfread           | Python Puro   | Excelente (Win, Linux, Mac)

    # Servidores
    | Sis | SISTEMA              | MODIFICA YosCtr
    | Msi | MAESTROS DEL SISTEMA | MODIFICA ADMINISTRADORES
    | Mrp | MAESTROS DEL GRUPO   | MODIFICA USUARIOS
    | Mae | MAESTROS             | MODIFICA USUARIOS
    | Dat | DATOS EMPRESA        | MODIFICA USUARIOS
    | Ach | ARCHIVOS             | MODIFICA AUTORIZADOS EN EL SERVIDOR
    | Tmp | TEMPORAL             | DIRECTORIO TEMPORAL %Tmp% del sistema
    | Ext | EXTERNO DEL SISTEMA  | MODIFICA USUARIOS

    | YosCfg["Apl_Bdt_Xxx_Tip"] | YosCfg["Apl_Bdt_Xxx_Dir"] | YosCfg["Apl_Bdt_Xxx_Usr"] | YosCfg["Apl_Bdt_Xxx_Pas"] | YosCfg["Apl_Bdt_Xxx_Dbt"]
    | SQLite                    | Direccion Local o Red     |                           |                           |
    | PostgreSQL                | Ip:Puerto                 | Usuario                   | Contraseña                |
    | MariaDB                   | Ip:Puerto                 | Usuario                   | Contraseña                |
    | MSSQL                     | Ip:Puerto                 | Usuario                   | Contraseña                | Registro
    | Ach                       | Direccion Local o Red     |                           |                           |

    | Xxx |
    | Sis | YosCfg["Apl_Bdt_Sis_Dbt"] | YosCfg["Apl_Bdt_Sis_Dir"] | YosCfg["Apl_Bdt_Sis_Usr"] | YosCfg["Apl_Bdt_Sis_Pas"] |
    | Msi | YosCfg["Apl_Bdt_Msi_Dbt"] | YosCfg["Apl_Bdt_Msi_Dir"] | YosCfg["Apl_Bdt_Msi_Usr"] | YosCfg["Apl_Bdt_Msi_Pas"] |
    | Mrp | YosCfg["Apl_Bdt_Mrp_Dbt"] | YosCfg["Apl_Bdt_Mrp_Dir"] | YosCfg["Apl_Bdt_Mrp_Usr"] | YosCfg["Apl_Bdt_Mrp_Pas"] |
    | Mae | YosCfg["Apl_Bdt_Mae_Dbt"] | YosCfg["Apl_Bdt_Mae_Dir"] | YosCfg["Apl_Bdt_Mae_Usr"] | YosCfg["Apl_Bdt_Mae_Pas"] |
    | Dat | YosCfg["Apl_Bdt_Dat_Dbt"] | YosCfg["Apl_Bdt_Dat_Dir"] | YosCfg["Apl_Bdt_Dat_Usr"] | YosCfg["Apl_Bdt_Dat_Pas"] |
    | Ach | YosCfg["Apl_Bdt_Ach_Dbt"] | YosCfg["Apl_Bdt_Ach_Dir"] | Direccion donde estan guardaddos varios archivos que usa la aplicacion
    | Tmp |                           | YosCfg["Ent_Tmp"]         | En el directorio Temporal de la Computadora
    | Ext | Pendiete de revision o ponerlo en la aplicación


    Base de Datos de Configuracion
    YosCfg esta en el directorio Bdt de la aplicacion y tiene dos tablas
        Apl - (1 solo Registro, se copiarande la YosSis.AplCfg ) Los Datos que definen a la Aplicacion
        Dat - Valores necesarios para la aplicacion que se definen durante la programacion

Ahora empezaremos con el script Idd_BdtSvr.py y tendrá las siguientes def
- Cnx - conexión a la base de datos
- Sel - Select único
- SelMul - Select de Transacción
- Cie - Cerrar la conexión

"""

def Cnx(Fnc_Svr, Fnc_Mod="ro"):
    # Conexion

    match Fnc_Mod:
        case "ro": # YosCfg SIMPRE es SQLite y esta en YosCfg["Apl_Dir_Bdt"]
            pass
        case "rw":
            pass
        case _:
            Fnc_Mod="ro"

    if Fnc_Svr=="YosCfg":
        Mem_Tip = "SQLite"
        Mem_Dir = os.path.join(YosCfg["Apl_Dir_Bdt"], Fnc_Svr + ".Bdt")
        Mem_Usr = ""
        Mem_Pas = ""
        Mem_Bdt = ""
        Mem_Obs = ""
    else:
        Mem_Tip = YosCfg[f"Apl_Bdt_{Fnc_Svr}_Tip"]
        Mem_Dir = YosCfg[f"Apl_Bdt_{Fnc_Svr}_Dir"]
        Mem_Usr = YosCfg[f"Apl_Bdt_{Fnc_Svr}_Usr"]
        Mem_Pas = YosCfg[f"Apl_Bdt_{Fnc_Svr}_Pas"]
        Mem_Bdt = YosCfg[f"Apl_Bdt_{Fnc_Svr}_Bdt"]
        Mem_Obs = YosCfg[f"Apl_Bdt_{Fnc_Svr}_Obs"]

    if YosCfg["Dbg"]=="S":
        Mem_Txt=f"""
            Fnc_Svr = {Fnc_Svr}
            Mem_Tip = {Mem_Tip}
            Mem_Dir = {Mem_Dir}
            Mem_Usr = {Mem_Usr}
            Mem_Pas = {Mem_Pas}
            Mem_Bdt = {Mem_Bdt}
            Mem_Obs = {Mem_Obs}
            """
        print(Mem_Txt)
        input("Pulse intro")

    try:
        match Mem_Tip:
            case "SQLite":
                # Validamos existencia física
                SvrDir = os.path.join(YosCfg["Apl_Dir_Bdt"], Fnc_Svr + ".Bdt")
                if not os.path.exists(SvrDir):
                    print(f"ERROR: NO EXISTE LA BASE DE DATOS : ./Bdt/{Fnc_Svr}.Bdt")
                    # Verifico que EXISTAN las tablas de SQLite.Yos.cfg
                    YosCfg_Vfy()
                    SvrDir = os.path.join(YosCfg["Apl_Dir_Bdt"], Fnc_Svr + ".Bdt")
                    print(f"SE HA CREADO LA BASE DE DATOS : ./Bdt/{Fnc_Svr}.Bdt")
                    print("DEBE ACTUALIZAR LOS DATOS DE LA APLICACION")
                    input("PULSE INTRO PARA CONTINUAR")
                    #sys.exit(1)
                    #return None

                uri_path = f"file:{SvrDir}?mode={Fnc_Mod}"

                import sqlite3
                conn = sqlite3.connect(SvrDir)
                conn.row_factory = sqlite3.Row
                return conn

                try:
                    # uri=True es obligatorio para que SQLite interprete el modo
                    conn = sqlite3.connect(uri_path, uri=True)
                    conn.row_factory = sqlite3.Row
                    return conn

                except sqlite3.Error as e:
                    print(f"Error al conectar en modo {'Lectura' if pSoloLectura else 'Escritura'}: {e}")
                    input("PULSE INTRO PARA FINALIZAR")
                    sys.exit(1)
                    return None

            case "PostgreSQL":
                print("PostgreSQL")

            case "MsSQL":
                import pypyodbc as pyodbc
                SvrDir = (
                    "DRIVER={ODBC Driver 18 for SQL Server};"
                    f"SERVER={Mem_Dir};"
                    f"DATABASE={Mem_Bdt};"
                    f"UID={Mem_Usr};"
                    f"PWD={Mem_Pas};"
                    "Encrypt=yes;"
                    "TrustServerCertificate=yes;"
                )

                try:
                    conn = pyodbc.connect(SvrDir)
                except pyodbc.Error as e:
                    # Extraemos el código de error y el mensaje
                    sqlstate = e.args[0]
                    # Imprimimos con honor: Bin >
                    print(f"001. ERROR DE SQL (Estado {sqlstate}):")
                    print(f"     Detalle: {e.args[1]}")
                    conn = None  # Aseguramos que la variable no quede con basura

                return conn

            case "MariaDB":
                print("MariaDB")

            case _:
                print(f"SERVIDOR {Fnc_Svr} TIPO {Mem_Tip} NO IMPLEMENTADO")
                input("Pulse intro para finalizar")
                sys.exit(1)
                return None

    except Exception as Err:
        print(f"Error de CONEXION A {Fnc_Svr} TIPO {Mem_Tip} : {Err}")
        input("Pulse intro para finalizar")
        sys.exit(1)
        return None

#def Sel(Fnc_Cur, Fnc_Sel):
#    # Fnc_Sel ahora es el SQL que mandas desde afuera
#    # Cuando Sql solo devuelve un registro o mensaje
#    try:
#        Fnc_Cur.execute(Fnc_Sel)
#        return Fnc_Cur.fetchone()

#    except Exception as Err:
#        print(f"Error en Sel: {Err}")
#        return None

def Sel(Fnc_Cur, Fnc_Sql, pParams=()):
    # 1. Convertimos a mayúsculas para buscar palabras clave
    sql_upper = Fnc_Sql.strip().upper()

    try:
        Fnc_Cur.execute(Fnc_Sql, pParams)

        # 2. Verificamos si es un comando de acción
        es_accion = any(sql_upper.startswith(word) for word in ["INSERT", "UPDATE", "DELETE", "CREATE", "DROP"])

        if es_accion:
            # Si tu conexión no tiene autocommit, lo forzamos aquí
            # Nota: Necesitarías acceso al objeto conexión o ejecutar COMMIT directamente
            Fnc_Cur.execute("COMMIT;")
            print(f"1. [SQL] Acción ejecutada y confirmada (COMMIT).")
            return True
        else:
            # Si es un SELECT, devolvemos el registro único
            return Fnc_Cur.fetchone()

    except Exception as Err:
        print(f"2. [Error en Sel]: {Err}")
        return None

def SelTot(Fnc_Cur, Fnc_Sql, pParams=()):
    # Cuando Sql solo devuelve VARIOS registros
    """
    Lee TODOS los registros de una consulta.
    Fnc_Cur: El cursor activo.
    Fnc_Sql: La sentencia SQL (ej. "SELECT * FROM MiTabla").
    """
    try:
        Fnc_Cur.execute(Fnc_Sql, pParams)
        # fetchall() devuelve una lista con todas las filas
        return Fnc_Cur.fetchall()

    except Exception as e:
        print(f"Error en SelTodo: {e}")
        return []

def SelMul():
    # Transaccion
    pass

def Cie(Fnc_Cnx):
    """
    Cierra la conexión de forma segura.
    Fnc_Cnx: El objeto de conexión que recibiste de Cnx().
    """
    if Fnc_Cnx:
        try:
            # Cerramos la conexión
            Fnc_Cnx.close()
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")

def YosCfg_Vfy():
    print("Idd_BdtSvr.YosCfg_Vfy() - 250")
    import sqlite3
    Mem_Cnx_YosCfg = sqlite3.connect(os.path.join(YosCfg["Apl_Dir_Bdt"], "YosCfg.Bdt"))
    Mem_Cnx_YosCfg.row_factory = sqlite3.Row

#    Mem_Cnx_YosCfg = Cnx("YosCfg")
    Mem_Cur_YosCfg = Mem_Cnx_YosCfg.cursor()

    from datetime import datetime
    # Verifico que las tablas de Yos.cfg SQLite
    # Creo Apl
    Mem_Sql = """
                CREATE TABLE IF NOT EXISTS "Apl" (
                    "cNom"          TEXT(60),
                    "cEtnApl"       TEXT(3),
                    "cEtnAplLet"    TEXT(25),
                    "cVsn"          TEXT(8),
                    "cCpy"          TEXT(50),
                    "cCpyEml"       TEXT(50),
                    "cObs"          TEXT(100),
                    "cModRegNik"    TEXT(20),
                    "cModRegTim"    TEXT(20))
                """
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql)
    Mem_Cnx_YosCfg.commit()
    DateTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Mem_Vsn=datetime.now().strftime("%Y.%m")
    Mem_Cpy=datetime.now().strftime("%Y")+" © Miguel Tortosa"
    Mem_Sql = f"""INSERT INTO "Apl" VALUES ('{Mem_Ini_AplNom}','Txt','dos_rebel','{Mem_Vsn}','{Mem_Cpy}','mtcyos@yahoo.es','','YosCfg','{DateTime}')"""
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql)
    Mem_Cnx_YosCfg.commit()

    # Creo Bdt
    Mem_Sql = """
                CREATE TABLE IF NOT EXISTS "Bdt" (
                    "cSvr"  VARCHAR(9),
                    "cSvrTip"   VARCHAR(10),
                    "cDir"  VARCHAR(100),
                    "cUsr"  VARCHAR(25),
                    "cPas"  VARCHAR(25),
                    "cBdt"  Text(20),
                    "cObs"  VARCHAR(100),
                    "cModRegNik"    TEXT(20),
                    "cModRegTim"    TEXT(20))
                """
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql)
    Mem_Cnx_YosCfg.commit()

    # Creo Dat
    Mem_Sql = """
                CREATE TABLE IF NOT EXISTS "Dat" (
                    "cNom"  VARCHAR(60),
                    "cDes"  VARCHAR(100),
                    "cTipClm"   VARCHAR(1),
                    "cVal"  VARCHAR(253),
                    "cValPmd"   VARCHAR(100),
                    "cLonClm"   VARCHAR(3),
                    "cAli"  VARCHAR(1),
                    "cObs"  VARCHAR(100),
                    "cObsSis"   VARCHAR(100),
                    "cModRegNik"    TEXT(20),
                    "cModRegTim"    TEXT(20))
                """
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql)
    Mem_Cnx_YosCfg.commit()
    DateTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Mem_Sql = f"""INSERT INTO "Dat" VALUES ('Apl_AdmPas','CONTRASEÑA DEL ADMINISTRADOS EN md5','C','d71572b884515cac7538f4f93fa16275','','','','MODIFIQUELA PARA PONER LA SUYA','PARA MODIFCACIONES SIN CONTROL DE USUARIOS','YosCfg','{DateTime}')"""
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql)
    Mem_Cnx_YosCfg.commit()

    # Creo Mnu
    Mem_Sql = """
                CREATE TABLE IF NOT EXISTS "Mnu" (
                    "cMnu"          TEXT(25),
                    "cNum"          TEXT(3),
                    "cTip"          TEXT(3),
                    "cEtn"          TEXT(10),
                    "cTxt"          TEXT(50),
                    "cFnc"          TEXT(200),
                    "cObs"          TEXT(100),
                    "cModRegNik"    TEXT(20),
                    "cModRegTim"    TEXT(20))
                """
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql)
    Mem_Cnx_YosCfg.commit()
    DateTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Mem_Sql = (f"""
                INSERT INTO 'Mnu' VALUES
                    ('Main', "00", 'Cab', NULL, 'ENTORNO',            NULL,                             '', 'YosCfg', '{DateTime}'),
                    ('Main', "01", 'Opc', NULL, 'RECARGAR MENU',      'YosMnuCag',                      '', 'YosCfg', '{DateTime}'),
                    ('Main', "05", 'Opc', NULL, 'CONTACTENOS',        'Yos.EmlEnv("mtcyos@yahoo.es")',  '', 'YosCfg', '{DateTime}'),
                    ('Main', "06", 'Opc', NULL, 'LICENCIA',           'Yos.AcdRes()',                   '', 'YosCfg', '{DateTime}'),
                    ('Main', "07", 'Opc', NULL, 'ACERCA DE ...',      'Yos.Acd()',                      '', 'YosCfg', '{DateTime}'),
                    ('Main', "08", 'Opc', NULL, 'MODIFICAR ENTORNO',  'Yos.AcdEtn()',                   '', 'YosCfg', '{DateTime}'),
                    ('Main', "09", 'Opc', NULL, 'SALIR',              'Yos.Apl_Fin()',                  '', 'YosCfg', '{DateTime}');
            """)
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql)
    Mem_Cnx_YosCfg.commit()

    Cie(Mem_Cnx_YosCfg)
