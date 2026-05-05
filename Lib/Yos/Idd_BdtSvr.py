#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import os

from Yos import FrmWit

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
    if YosCfg["Dbg"] == "S": print(F"Cnx({Fnc_Svr}, {Fnc_Mod})")

    match Fnc_Mod:
        case "ro": # YosCfg SIEMPRE es SQLite y esta en YosCfg["Apl_Dir_Bdt"]
            pass
        case "rw":
            pass
        case _:
            Fnc_Mod="ro"

    # Opciones Especiales
    match Fnc_Svr:
        case "YosCfg":  # Configuracion de la aplicacion
            Mem_Cnx = {
                "Svr": Fnc_Svr,
                "Tip": "SQLite",
                "Dir": os.path.join(YosCfg["Apl_Dir_Bdt"], Fnc_Svr + ".Bdt"),
                "Usr": "",
                "Pas": "",
                "Bdt": "",
                "Obs": ""
            }

        case "YosLib":  # Configuracion de la Libreria Yos
            Mem_Cnx = {
                "Svr": Fnc_Svr,
                "Tip": "SQLite",
                "Dir": os.path.join(YosCfg["Yos_Dir"], "Bdt", Fnc_Svr + ".Bdt"),
                "Usr": "",
                "Pas": "",
                "Bdt": "",
                "Obs": ""
            }

        case _:
            match YosCfg[f"Apl_Bdt_{Fnc_Svr}_Tip"]:
                case "SQLite":
                    if not YosCfg[f"Apl_Bdt_{Fnc_Svr}_Dir"]: # Si esta vacio usa el directorio de la aplicacion
                        Mem_Dir = os.path.join(YosCfg["Apl_Dir_Bdt"], Fnc_Svr + ".Bdt")
                    else:
                        Mem_Dir = YosCfg[f"Apl_Bdt_{Fnc_Svr}_Dir"]
                        Mem_Dir = os.path.join(Mem_Dir, "Bdt", Fnc_Svr + ".Bdt")

                case _:
                    Mem_Dir = YosCfg[f"Apl_Bdt_{Fnc_Svr}_Dir"]
#            print(Mem_Dir)

            Mem_Cnx = {
                "Svr": Fnc_Svr,
                "Tip": YosCfg[f"Apl_Bdt_{Fnc_Svr}_Tip"],
                "Dir": Mem_Dir,
                "Usr": YosCfg[f"Apl_Bdt_{Fnc_Svr}_Usr"],
                "Pas": YosCfg[f"Apl_Bdt_{Fnc_Svr}_Pas"],
                "Bdt": YosCfg[f"Apl_Bdt_{Fnc_Svr}_Bdt"],
                "Obs": YosCfg[f"Apl_Bdt_{Fnc_Svr}_Obs"]
            }

    if YosCfg["Dbg"]=="S":
        print("Mem_Cnx")
        print("--------------------------------------------------")
        print("\n".join([f"{k}: {v}" for k, v in Mem_Cnx.items()]))
        print("--------------------------------------------------")
        FrmWit()

    try:
        match Mem_Cnx['Tip']:
            case "SQLite":
                # Validamos existencia física
                if not os.path.exists(Mem_Cnx['Dir']):
                    print(f"ATENCION: NO EXISTE LA BASE DE DATOS : {Mem_Cnx['Dir']}")
                    Idd_BdtSvr_Cre(Mem_Cnx)
                    print(f"SE HA CREADO LA BASE DE DATOS : {Fnc_Svr}")
                    print("REVISE LOS DATOS DE LA APLICACION")
                    FrmWit()
                    #sys.exit(1)
                    #return None

                uri_path = f"file:{Mem_Cnx['Dir']}?mode={Fnc_Mod}"

                import sqlite3
                conn = sqlite3.connect(Mem_Cnx['Dir'])
                conn.row_factory = sqlite3.Row
                return conn

                try:
                    # uri=True es obligatorio para que SQLite interprete el modo
                    conn = sqlite3.connect(uri_path, uri=True)
                    conn.row_factory = sqlite3.Row
                    return conn

                except sqlite3.Error as e:
                    print(f"Error al conectar en modo {'Lectura' if pSoloLectura else 'Escritura'}: {e}")
                    FrmWit()
                    sys.exit(1)
                    return None

            case "PostgreSQL":
                print("PostgreSQL")

            case "MsSQL":
                import pypyodbc as pyodbc
                SvrDir = (
                    "DRIVER={ODBC Driver 18 for SQL Server};"
                    f"SERVER={Mem_Cnx['Dir']};"
                    f"DATABASE={Mem_Cnx['Bdt']};"
                    f"UID={Mem_Cnx['Usr']};"
                    f"PWD={Mem_Cnx['Pas']};"
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
                print(f"SERVIDOR {Fnc_Svr} TIPO {Mem_Cnx['Tip']} NO IMPLEMENTADO")
                FrmWit()
                sys.exit(1)
                return None

    except Exception as Err:
        print(f"Error de CONEXION A {Fnc_Svr} TIPO {Mem_Cnx['Tip']} : {Err}")
        FrmWit()
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

def IptSql(Fnc_Ach, Fnc_Cnx, Fnc_Dat=None):
    """
    Lee un archivo .sql desde el directorio Yos/Sql
    """
    Mem_Dat = os.path.join(YosCfg["Yos_Dir"], "Sql", Fnc_Ach + ".sql")
    Mem_Sql = os.path.abspath(Mem_Dat)

    try:
        with open(Mem_Sql, 'r', encoding='utf-8') as archivo:
            Mem_Contenido = archivo.read()

            # Si enviamos un diccionario de datos, aplicamos el formato (la "f")
            if Fnc_Dat:
                return Mem_Contenido.format(**Fnc_Dat)

            return Mem_Contenido

    except FileNotFoundError:
        input(f"ERROR: No se encontró el archivo SQL en: {Mem_Sql}")
        Cie(Fnc_Cnx)
        Mem_Sql = os.path.join(YosCfg["Apl_Dir_Bdt"], "YosCfg.Bdt")
        os.remove(Mem_Sql)
        import sys
        sys.exit(0)
        return "Err"

def Idd_BdtSvr_Cre(Fnc_Cnx):
    # Crea las tablas NECESARIOS de el servidor y sus datos iniciales
    # Servidor, Tabla (Vacio=todas)
    """
                Mem_Cnx = {
                "Svr": Fnc_Svr,
                "Tip": "SQLite",
                "Dir": os.path.join(YosCfg["Yos_Dir"], "_Bdt", Fnc_Svr + ".Bdt"),
                "Usr": "",
                "Pas": "",
                "Bdt": "",
                "Obs": ""
            }
    """
    # De momento Solo YosCfg, YosLib
    match Fnc_Cnx['Svr']:
        case "YosCfg":
            pass
        case "YosLib":
            pass
        case _:
            return "Err"

    print("Fnc_Cnx")
    print("--------------------------------------------------")
    print("\n".join([f"{k}: {v}" for k, v in Fnc_Cnx.items()]))
    print("--------------------------------------------------")
    FrmWit()

    # FrmWit(Fnc_Txt="",Fnc_Wit=0):
    import sqlite3
    Mem_Cnx_YosCfg = sqlite3.connect(Fnc_Cnx['Dir'])
    Mem_Cnx_YosCfg.row_factory = sqlite3.Row

#    Mem_Cnx_YosCfg = Cnx("YosCfg")
    Mem_Cur_YosCfg = Mem_Cnx_YosCfg.cursor()


    # Verifico que las tablas de Yos.cfg SQLite

    # De momento Solo YosCfg, YosLib
    match Fnc_Cnx['Svr']:
        case "YosCfg":
            Idd_BdtSvr_Cre_Tab("Apl", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            Idd_BdtSvr_Cre_Reg("Apl", "YosCfg", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)

            Idd_BdtSvr_Cre_Tab("Bdt", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
#            Idd_BdtSvr_Cre_Reg("Bdt", "YosCfg", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)

            Idd_BdtSvr_Cre_Tab("Dat", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            Idd_BdtSvr_Cre_Reg("Dat", "YosCfg", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)

            Idd_BdtSvr_Cre_Tab("Mnu", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            Idd_BdtSvr_Cre_Reg("Mnu", "YosCfg", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)

            Idd_BdtSvr_Cre_Tab("Ord", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            Idd_BdtSvr_Cre_Reg("Ord", "YosCfg", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)

            Idd_BdtSvr_Cre_Tab("Brw", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            Idd_BdtSvr_Cre_Reg("Brw", "YosCfg", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)

            Idd_BdtSvr_Cre_Tab("ClmMod", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            Idd_BdtSvr_Cre_Reg("ClmMod", "YosCfg", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            print("CONTRASEÑA DEL ADMINISTRADOR = Admin1967")

        case "YosLib":
            Idd_BdtSvr_Cre_Tab("Bdt", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            Idd_BdtSvr_Cre_Reg("Bdt", "YosLib", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)

            Idd_BdtSvr_Cre_Tab("Dat", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
#            Idd_BdtSvr_Cre_Reg("Dat", "YosLib", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)

            Idd_BdtSvr_Cre_Tab("Ord", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            Idd_BdtSvr_Cre_Reg("Ord", "YosCfg", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)


            Idd_BdtSvr_Cre_Tab("Brw", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            Idd_BdtSvr_Cre_Reg("Brw", "YosCfg", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)

            Idd_BdtSvr_Cre_Tab("ClmMod", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)
            Idd_BdtSvr_Cre_Reg("ClmMod", "YosCfg", Mem_Cnx_YosCfg, Mem_Cur_YosCfg)


def Idd_BdtSvr_Cre_Tab(Mem_Tab, Mem_Cnx_YosCfg, Mem_Cur_YosCfg):
    print(f"Creando {Mem_Tab}")
    Mem_Sql = IptSql(f"{Mem_Tab}_Cre", Mem_Cnx_YosCfg)
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql)
    Mem_Cnx_YosCfg.commit()

def Idd_BdtSvr_Cre_Reg(Mem_Tab, Mem_Svr, Mem_Cnx_YosCfg, Mem_Cur_YosCfg):
    from datetime import datetime
    # Creo un diccionario para las sustituciones del .sql
    input(YosCfg["Apl_Apl"])
    Mem_Dic = {
        "Mem_Ini_AplNom": Mem_Ini_AplNom,
        "Mem_Vsn": datetime.now().strftime("%Y.%m"),
        "Mem_Cpy": datetime.now().strftime("%Y")+" © Miguel Tortosa",
        "Usr": "YosCfg",
        "DateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "«Apl_Apl»": YosCfg["Apl_Apl"],
        "«Apl_Etn»": Mem_Ini_AplEtn,
    }
    Mem_Sql = IptSql(f"{Mem_Tab}_{Mem_Svr}", Mem_Cnx_YosCfg, Mem_Dic)
    print(Mem_Sql)
    Mem_Dat = SelTot(Mem_Cur_YosCfg, Mem_Sql)
    Mem_Cnx_YosCfg.commit()
