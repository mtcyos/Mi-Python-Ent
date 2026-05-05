#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
   YosLib.py

   LIBRERIA DE PROPOSITO GENERAL>

   Copyright (c) 2026 Miguel Tortosa

   Licenciado bajo la Licencia MIT.

   Consulte el archivo LICENCIA en la raíz del proyecto para más información.
"""

import os
import sys
import inspect
import shutil
import builtins
import asyncio

import Yos

################################################################### Inicio Def ##########################################################
async def Yos_DefLib(Fnc_Def):
    # Carga y actualiza dinámicamente una definición desde la base de datos YosLib
    import builtins

    # --- MODIFICACIÓN BIN: EXTRAEMOS NOMBRE PARA BÚSQUEDA ---
    # De "Hola('Miguel')" sacamos "Hola"
    Mem_Fnc = Fnc_Def.split('(')[0].strip().split('.')[-1]

    # BÚSQUEDA EN MEMORIA (Evitamos consultar la DB si ya está cargada)
    Mem_FncVfy = getattr(builtins, Mem_Fnc, None) or globals().get(Mem_Fnc) or getattr(Yos, Mem_Fnc, None)

#·    if callable(Mem_FncVfy):    # Ya existe la funcion en memoria
#        print(f"EXISTE {Mem_FncVfy}")
#        return

    # CONSULTA A SQLITE (Buscamos por Mem_Fnc, no por el comando completo)
    Mem_Cnx_YosCfg = Yos.Cnx("YosLib")
    Mem_Cur_YosCfg = Mem_Cnx_YosCfg.cursor()
    Mem_Sql = f"SELECT cCmd FROM Def WHERE cDef ='{Mem_Fnc}'"
    Mem_Dat = Yos.Sel(Mem_Cur_YosCfg, Mem_Sql)
    Yos.Cie(Mem_Cnx_YosCfg)

    # --- MODIFICACIÓN BIN: SI NO ESTÁ EN DB, NO DAMOS ERROR, DEJAMOS SEGUIR ---
    if not Mem_Dat:
        # Quitamos el print de error y el return seco
        return Fnc_Def

    Mem_Cmd = Mem_Dat[0]
    Mem_Cmd = str(Mem_Cmd).replace('\r\n', '\n').replace('\r', '\n').replace('\xa0', ' ')

    # INYECCIÓN Y EJECUCIÓN
    try:
        # Registramos el 'def' en el diccionario global real
        exec(Mem_Cmd, globals())

        # Buscamos la función inyectada por su nombre base
        func_inyectada = globals().get(Mem_Fnc)

        if callable(func_inyectada):
            # LA CLAVE: Registramos la función en builtins para que Main.py la vea
            setattr(builtins, Mem_Fnc, func_inyectada)

        return Fnc_Def # Devolvemos el comando original para que se ejecute

    except Exception as e:
        # print(f"Error crítico al ejecutar código dinámico de {Fnc_Def}: {e}")
        return Fnc_Def

async def Yos_EntDat(**Fnc_Dic):
    # Solicita informacion directa

    if not Fnc_Dic:
        return

    """
    Tit -> Titulo
    Des -> Descripcion de los datoa a introducir
    Acn -> Cre, Ver, Mod, Eli , mision Ver
    Columnas a pedir
        {
            "Clm": "AplNue",
            "Rot": "Nombre aplicación",
            "ClmTip": "C",
            # Aplicamos: No_Nul (Obligatorio) y No_Pto (Sin puntos/signos para carpetas)
            "Vfy": "No_Nul, No_Pto",
            "Lon": 20, # Añadimos longitud para que Vfy Lon funcione Si es ClmTip=N 3.1  3 espacios 2 decimales 1.2  ( minimo 1 entero + . + decimales)
            "Opc": ""
        },
    Tipo    Funcion VERIFICACIONES DE DATOS
    Mod     Cap     .capitalize()   "Hola mundo" (Solo la primera letra de la frase)
    Mod     Min     .lower()        "hola mundo"
    Mod     Myu     .upper()        "HOLA MUNDO"
    Mod     Tit     .title()        "Hola Mundo" (La primera de cada palabra)
    Mod     NoEsp   Quita espacio de izquierda y derecha
    Mod     NoEsp_D Quita espacio de derecha
    Mod     NoEsp_I Quita espacio de izquierda

    Ver     Pas     contraseña (se mostrara *) y pondrá otro campo para verificacion
    Vfy     Lon     Longitud
    Vfy     No_Nul  (/NoNul) en campo cNul (S/N)    Tiene que estar lleno
    Vfy     No_Pto  No permite signos de puntuación (ideal para nombres de archivos).
    Vfy     Opc     Opciones (a,b,c,d,e)
    Vfy     Ran     Ran:Ini-Fin
    Vfy     UncLet  Solo permite A-Z y espacios.
    Vfy     UncNum  Solo permite 0-9.

    Rel     OpcTab  Opc:Tab:Clm:Des (Browse de selección)
    Rel     Unc     Unico Unc:Tab:Clm:Des

    DEVUELVE
    {
        "Clm": "AplNue",    # Columna
        "Dato": ""   # Dato devuelto
    },
    SI HAY ERRORES -> return


    EJEMPLO


    """


    # **Fnc_Dic es un diccionario con todo lo que envíes por nombre
    Mem_Tit = Fnc_Dic.get("Tit", "INTRODUCCIÓN DE DATOS") # Titulo
    Mem_Des = Fnc_Dic.get("Des", "INTRODUZCA LA INFORMACIÓN REQUERIDA.")    # Descripcion de los datoa a introducir
    Fnc_Dic["Tit"] = Mem_Tit
    Fnc_Dic["Des"] = Mem_Des

    import builtins
    if builtins.Mem_Ini_AplEtn == "Txt":    # Entorno Txt
        return yos.Yos_EntDat_Txt(**Fnc_Dic)
    else:
        return await Yos.Yos_EntDat_Frm(**Fnc_Dic)

from datetime import datetime
import string

def Yos_EntDat_Vfy(Fnc_Dat, Fnc_Vfy, Fnc_Rot, Fnc_Tip, Fnc_Lon):
    Mem_Err = ""
    Mem_Dat = Fnc_Dat
    reglas = [r.strip() for r in Fnc_Vfy.split(",") if r.strip()]

    for regla in reglas:
        # Mod - MODIFICADORES (Cambian el dato) ---
        if regla == "Cap":  # capitalize() : Convierte solo el primer carácter de toda la cadena a mayúscula y cambia todos los demás caracteres a minúscula
            Mem_Dat = Mem_Dat.capitalize()

        if regla == "Min":  # lower() : Convierte una cadena a minúsculas
            Mem_Dat = Mem_Dat.lower()

        if regla == "Myu":  # upper() : Convierte una cadena a mayúsculas
            Mem_Dat = Mem_Dat.upper()

        if regla == "NoEsp":  # strip() : Elimina caracteres de ambos extremos, izquierdo y derecho.
            Mem_Dat = Mem_Dat.strip()

        if regla == "NoEsp_D":  # rstrip() : Elimina caracteres solo desde la derecha (extremo).
            Mem_Dat = Mem_Dat.rstrip()

        if regla == "NoEsp_I":  # lstrip() : Elimina los caracteres solo desde la izquierda (inicio).
            Mem_Dat = Mem_Dat.lstrip()

        if regla == "Tit":  # title() : Convierte una cadena donde el primer carácter de cada palabra está en mayúscula y el resto en minúscula.
            Mem_Dat = Mem_Dat.title()

        # Vfy - VERIFICADORES (Lanzan errores) ---

        # Lon - Longitud
        if Fnc_Tip == "N":
            Nun_Limpio = str(Mem_Dat).replace(',', '') if Mem_Dat is not None else ""
            if Fnc_Lon > 0 and len(Nun_Limpio) > Fnc_Lon:
                Mem_Err = f"Error : {Fnc_Rot} excede al maximo definido {len(Nun_Limpio)}/{Fnc_Lon}."
                break
        else:
            # Aqui trunca por la derecha
            if Fnc_Lon > 0 and len(Mem_Dat) > Fnc_Lon:
                Mem_Dat = Mem_Dat[:Fnc_Lon]


        # No_Nul - Tiene que estar lleno
        if regla == "No_Nul":
            if Fnc_Tip == "D" and Fnc_Dat==None:    # para fechas
                Mem_Err = f"Error : Campo '{Fnc_Rot}' no puede estar vacío."
                break

            elif not Mem_Dat.strip():
                Mem_Err = f"Error : Campo '{Fnc_Rot}' no puede estar vacío."
                break

        # Opc - Opciones (a,b,c,d,e)
        if regla.startswith("Opc:") and not regla.startswith("OpcTab:"):
            lista_opc = [o.strip() for o in regla.split(":")[1].split(",")]
            if Mem_Dat not in lista_opc:
                opciones_str = ", ".join(lista_opc)
                Mem_Err = f"Error en '{Fnc_Rot}': Debe elegir entre ({opciones_str})."
                break

        # Ran - Ran:Ini-Fin
        if regla.startswith("Ran:"):
            try:
                val_ini, val_fin = regla.split(":")[1].split("-")
                val_ini, val_fin = val_ini.strip(), val_fin.strip()

                # --- Caso N (Números) ---
                if Fnc_Tip == "N":
                    if not (float(val_ini) <= float(Mem_Dat) <= float(val_fin)):
                        Mem_Err = f"Error : {Fnc_Rot} fuera de rango ({val_ini}-{val_fin})"
                        break

                # --- Caso D (Fechas) ---
                elif Fnc_Tip == "D":
                    f = Mem_Dat.strip()
                    dt_obj = None
                    try:
                        if "/" in f: dt_obj = datetime.strptime(f, "%d/%m/%Y")
                        elif "-" in f: dt_obj = datetime.strptime(f, "%Y-%m-%d")
                        elif len(f) == 8: dt_obj = datetime.strptime(f, "%Y%m%d")
                    except: pass

                    if not dt_obj:
                        Mem_Err = f"Error : Fecha '{Fnc_Rot}' no reconocida."
                        break
                    else:
                        if not (val_ini <= dt_obj.strftime("%Y%m%d") <= val_fin):
                            Mem_Err = f"Error : {Fnc_Rot} fuera de fecha ({val_ini}-{val_fin})."
                            break

                # --- Caso C (Texto) ---
                elif Fnc_Tip == "C":
                    if not (val_ini.upper() <= Mem_Dat.upper() <= val_fin.upper()):
                        Mem_Err = f"Error : {Fnc_Rot} fuera de secuencia alfabética."
                        break
            except:
                Mem_Err = f"Error de sintaxis en Rango para {Fnc_Rot}."
                break

        # Validaciones de caracteres
        # No_Pto - No permite signos de puntuación (Ideal para archivos)
        if regla == "No_Pto" and Mem_Dat:
            import string
            # !"#$%&'()*+,-./:;<=>?@[\]^_{|}~`
            signos_prohibidos = string.punctuation.replace("_", "") # le digo qiue el _ es permitido

            if any(char in signos_prohibidos for char in Mem_Dat):
                Mem_Err = f"Error : {Fnc_Rot} contiene signos no permitidos."
                break

        # UncLet - Solo permite A-Z y espacios.
        if regla == "UncLet" and Mem_Dat:
            if not all(x.isalpha() or x.isspace() for x in Mem_Dat):
                Mem_Err = f"Error : {Fnc_Rot} solo admite letras."
                break

        # UncNum - Solo permite 0-9.
        if regla == "UncNum" and Mem_Dat:
            if not Mem_Dat.isdigit():
                Mem_Err = f"Error : {Fnc_Rot} solo admite números."
                break

    return Mem_Dat, Mem_Err

async def Yos_AplCre(**Fnc_Dic):
    # Crea la estructura básica necesaria de una nueva aplicación Yos.
    import builtins
    import Yos

    # Aplicaciones
    Mem_Apl_Dir = {
        "YosMnu_Txt": ["Bat", "Bdt", "Script", "Sql"],
        "YosMnu_Frm": ["Bat", "Bdt", "Cfg", "Img", "Script", "Sql"]
    }


    # Definimos los campos que necesitamos
    if not Fnc_Dic:
        # Si entra aquí, es porque Fnc_Dic está VACÍO {}
        Mem_Campos = [
            {
                "Clm": "AplNue",
                "Rot": "Nombre aplicación",
                "Tip": "C",
                "Lon": 20,
                "Dat" : "Yos_KK",   # Dato por Omision
                "Mod" : "Cre",   # En que momento se puede Modificar Cre=Creacion , Mod=Modificacion
                "Vfy": "No_Nul, No_Pto",    # Aplicamos: No_Nul (Obligatorio) y No_Pto (Sin puntos/signos para carpetas)
                "Opc": ""
            },

            {
                "Clm": "AplOri",
                "Rot": "Origen (Plantilla)",
                "Tip": "C",
                "Lon": 0, # Añadimos longitud para que Vfy Lon funcione
                "Dat" : "YosMnu_Frm",
                "Mod" : "Cre",   # En que momento se puede Modificar Cre=Creacion , Mod=Modificacion
                "Vfy": "Opc",
                "Opc": list(Mem_Apl_Dir.keys()) # Aplicamos: Opc (Valida contra la lista de opciones)
            }
        ]
        '''
        TIPO = C - ui.input
            label:                  -> Rot : etiqueta, etiqueta mostrada para la entrada de texto
            placeholder:            -> : marcador de posición, Texto que se mostrará si no se ha introducido ningún valor.
            value:                  -> Dat : valor,  el valor actual de la entrada de texto
            password:               -> : contraseña, o si se debe ocultar la entrada (predeterminado: Falso)
            password_toggle_button: -> : botón_alternador_de_contraseña, Indica si se debe mostrar un botón para alternar la visibilidad de la contraseña (predeterminado: Falso).
            prefix:                 -> : prefijo,    un prefijo para anteponer al valor mostrado ( añadido en la versión 3.5.0 )
            suffix:                 -> : sufijo, un sufijo para agregar al valor mostrado ( añadido en la versión 3.5.0 )
            on_change:              -> : on_change;  Función de devolución de llamada que se ejecutará cuando cambie el valor.
            autocomplete:           -> : autocompletar,  Lista opcional de cadenas para autocompletar
            validation:             -> : validación, Diccionario de reglas de validación o una función que devuelve un mensaje de error opcional (predeterminado: None para ninguna validación).


        TIPO = N (C) - ui.input
            label:                  -> Rot : etiqueta, etiqueta mostrada para la entrada de texto
            placeholder:            -> : marcador de posición, Texto que se mostrará si no se ha introducido ningún valor.
            value:                  -> Dat : valor,  el valor actual de la entrada de texto
            password:               -> : contraseña, o si se debe ocultar la entrada (predeterminado: Falso)
            password_toggle_button: -> : botón_alternador_de_contraseña, Indica si se debe mostrar un botón para alternar la visibilidad de la contraseña (predeterminado: Falso).
            prefix:                 -> : prefijo,    un prefijo para anteponer al valor mostrado ( añadido en la versión 3.5.0 )
            suffix:                 -> : sufijo, un sufijo para agregar al valor mostrado ( añadido en la versión 3.5.0 )
            on_change:              -> : on_change;  Función de devolución de llamada que se ejecutará cuando cambie el valor.
            autocomplete:           -> : autocompletar,  Lista opcional de cadenas para autocompletar
            validation:             -> : validación, Diccionario de reglas de validación o una función que devuelve un mensaje de error opcional (predeterminado: None para ninguna validación).

        TIPO = D - ui.date_input
            label:       -> Rot : etiqueta, etiqueta mostrada para la entrada de fecha
            range_input: -> : rango_entrada, Si es True, permite seleccionar un rango de fechas (el valor será un diccionario con las claves "desde" y "hasta").
            placeholder: -> : marcador de posición, Texto que se mostrará si no se selecciona ninguna fecha.
            value:       -> Dat  : valor, el valor de la fecha actual
            on_change:   -> : on_change, Función de devolución de llamada que se ejecutará cuando cambie el valor.
        '''
        Mem_Campos = [
#            {   "Clm": "SaltoDeLinea"},
            {
                "Clm": "TIPO_C",            # Nombre de la Columna
                "Rot": "TIPO_C",            # Rotulo
                "Tip": "C",                 # Tipo de la Columna C=Caracteres, N = Numerico, D = Fecha
                "Mod" : "Cre",              # En que momento se puede Modificar Cre=Creacion , Mod=Modificacion
                "Lon": 20,                  # Longitud MAXIMA
                "Dat" : "Volor_Inicial",           # Dato por Omision
                "Vfy": "No_Nul, No_Pto",    # Aplicamos: No_Nul (Obligatorio) y No_Pto (Sin puntos/signos para carpetas)
                "Opc": ""
            },
            {   "Clm": "SaltoDeLinea"},
            {
                "Clm": "AplOri",
                "Rot": "Origen (Plantilla)",
                "Tip": "C",
                "Mod" : "Cre",   # En que momento se puede Modificar Cre=Creacion , Mod=Modificacion
                "Lon": 0, # Añadimos longitud para que Vfy Lon funcione
                "Dat" : "YosMnu_Frm",
                "Vfy": "Opc",
                "Opc": list(Mem_Apl_Dir.keys()) # Aplicamos: Opc (Valida contra la lista de opciones)
            },
            {   "Clm": "SaltoDeLinea"},
            {
                "Clm": "TIPO_Cz",            # Nombre de la Columna
                "Rot": "TIPO_Cz",            # Rotulo
                "Tip": "C",                 # Tipo de la Columna C=Caracteres, N = Numerico, D = Fecha
                "Mod" : "Cre",              # En que momento se puede Modificar Cre=Creacion , Mod=Modificacion
                "Lon": 20,                  # Longitud MAXIMA
                "Dat" : "Volor_Inicial",           # Dato por Omision
                "Vfy": "No_Nul, No_Pto",    # Aplicamos: No_Nul (Obligatorio) y No_Pto (Sin puntos/signos para carpetas)
                "Opc": ""
            },
            {
                "Clm": "nSla",
                "Rot": "Sueldo",
                "Tip": "N",
                "Mod" : "Cre",   # En que momento se puede Modificar Cre=Creacion , Mod=Modificacion
                "Lon": 15, # longitud Maxima en N=15
                "Dec": 2, # Decimales (Maximo Lon -2)
                "Dat" : 12345678.45,   # Dato por Omision
                "Vfy": "No_Nul",    # Aplicamos: No_Nul (Obligatorio)
                "Opc": ""
            },
            {   "Clm": "SaltoDeLinea"},
            {
                "Clm": "FecIni",            # Nombre de la Columna
                "Rot": "Fecha Inicial",            # Rotulo
                "Tip": "D",                 # Tipo de la Columna C=Caracteres, N = Numerico, D = Fecha
                "Mod" : "Cre",              # En que momento se puede Modificar Cre=Creacion , Mod=Modificacion
                "Dat" : "21/01/1967",           # Dato por Omision

                "Lon": 0,                  # Longitud MAXIMA


                "Vfy": "No_Nul",    # Aplicamos: No_Nul (Obligatorio) y No_Pto (Sin puntos/signos para carpetas)
                "Opc": ""
            },
        ]

        Fnc_Dic = {
            "Tit": "CREAR UNA NUEVA APLICACIÓN",
            "Des": 'Va a crear el entorno de una nueva aplicación. Por favor ponga los datos necesarios.', # <br>
            "Acn": 'Cre',
            "Frm": 'Max', # Max=Pantalla al maximo
            "Campos": Mem_Campos
        }

    # 2. Llamamos al "Cerebro" de entrada de datos
    # Él se encargará de llamar a Yos_EntDat_Txt o Yos_EntDat_Frm
    Mem_Dat = await Yos_EntDat(**Fnc_Dic)
    # 3. Si el usuario cancela o hay error, salimos
    if not Mem_Dat:
        print(f'{Yos.Yos_TimeStamp()} -> {YosSes["Usr_Ipd"]} - {YosSes["Usr_Nik"]} : SE CANCELA Yos.Yos_AplCre()')
        return

    # **Fnc_Dic es un diccionario con todo lo que envíes por nombre
    print(f"NUESTO DATOS  - {inspect.currentframe().f_lineno}")
    print(Mem_Dat)
    Mem_AplNue  = Mem_Dat.get("AplNue", "") # Nombre de la Nueva Aplicacion
    Mem_AplOri  = Mem_Dat.get("AplOri", "")    # Nombre de la Aplicacion de Origen, esta en Mem_Apl_Dir


    """
    Crea la estructura de una nueva aplicación Yos.
    Ubicación de plantillas: Lib/Yos/AplCre/
    """
    if not Mem_AplNue:
        print("Aviso: No se ha especificado nombre de aplicación.")
        return

    if not Mem_AplOri:
        print("Aviso: No se ha especificado Mem_AplOri de aplicación.")
        return

    print(f'GENERANDO aplicacion {Mem_AplNue} aplicacion maestra {Mem_AplOri}')
    Mem_Sal = ""

    # VALIDACIÓN SOLICITADA [cite: 2026-04-20]
    if Mem_AplOri not in Mem_Apl_Dir:
        Mem_Sal = f"\n  ATENCIÓN : La Aplicación '{Mem_AplOri}' no esta definida."
        Mem_Sal += f"      Aplicaciones definidas : {list(Mem_Apl_Dir.keys())}"

        if builtins.Mem_Ini_AplEtn == "Txt":    # Entorno Txt
            print(Mem_Sal)
            Yos.FrmWit()
        else:
            Yos.Yos_Msg_Frm(Fnc_Tit="ATENCIÓN", Fnc_Msg=Mem_Sal, Mem_AplOri="Err", Ancho="500px")
        return False

    Mem_Inf = []
    Mem_SubPla = "Frm" if "Frm" in Mem_AplOri else "Txt"

    # 1. RUTAS
    ruta_raiz = os.path.abspath(os.path.join(os.getcwd(), ".."))
    ruta_apl = os.path.join(ruta_raiz, Mem_AplNue)
    ruta_yos_lib = os.path.join(ruta_raiz, "Lib", "Yos")
    ruta_apl_cre = os.path.join(ruta_yos_lib, "AplCre") # Nueva base

    es_nueva = not os.path.exists(ruta_apl)

    # 2. DIRECTORIOS
    if es_nueva:
        os.makedirs(ruta_apl, exist_ok=True)
        Mem_Inf.append(f"Carpeta Raíz Creada : {Mem_AplNue}")

    for sub in Mem_Apl_Dir[Mem_AplOri]:
        camino = os.path.join(ruta_apl, sub)
        os.makedirs(camino, exist_ok=True)
        Mem_Inf.append(f"  Subdirectorio creado : {sub}")

    # 3. COPIA DE LICENCIA (Lib/Yos/AplCre/LICENCIA)
    orig_lic = os.path.join(ruta_apl_cre, "LICENCIA")
    dest_lic = os.path.join(ruta_apl, "LICENCIA")
    if os.path.exists(orig_lic) and not os.path.exists(dest_lic):
        shutil.copy2(orig_lic, dest_lic)
        Mem_Inf.append("LICENCIA : Archivo copiado")

    # 4. COPIA DE MAIN (Lib/Yos/AplCre/Frm o Txt/Main.py)
    orig_main = os.path.join(ruta_apl_cre, Mem_SubPla, "Main.py")
    dest_main = os.path.join(ruta_apl, "main.py")
    if os.path.exists(orig_main) and not os.path.exists(dest_main):
        shutil.copy2(orig_main, dest_main)
        Mem_Inf.append(f"main.py : Generado desde entorno {Mem_SubPla}")

    # 5. COPIA DE GRÁFICOS (Solo si existe carpeta Img y es modo Frm)
    if Mem_SubPla == "Frm":
        ruta_orig_img = os.path.join(ruta_apl_cre, "Frm", "Img")
        ruta_dest_img = os.path.join(ruta_apl, "Img")
        if os.path.exists(ruta_orig_img):
            recursos = ["favicon", "Log_01", "Log_02"]
            for rec in recursos:
                for f in os.listdir(ruta_orig_img):
                    if f.startswith(rec):
                        orig_f = os.path.join(ruta_orig_img, f)
                        dest_f = os.path.join(ruta_dest_img, f)
                        if not os.path.exists(dest_f):
                            shutil.copy2(orig_f, dest_f)
                            Mem_Inf.append(f"  Gráfico : {f} copiado")

    # 6. GENERACIÓN DEL .BAT
    Mem_YosMnu_Txt_Bat = (
        "@echo off\n"
        "\n"
        f"Set AplNom={Mem_AplNue}\n"
        ":: AplNom es el nombre de la Aplicacion y del Directorio que la contiene\n"
        "Set AplDir=%~dp0\n"
        "\n"
        ":: Pongo os Path temporales\n"
        "call %AplDir%Lib\\Yos\\YosAccDirPth.bat %AplDir%\n"
        "\n"
        ":: Accedo a disco/directorio\n"
        f"cd /d %AplDir%%AplNom%\\\n"
        "\n"
        ":: Ejecuto Python\n"
        "echo Python - %AplNom%\n"
        "python main.py\n"
        "\n"
        "echo.\n"
        "echo Python - %AplNom%.py - Script Finalizado\n"
        "timeout /t 8\n"
        "exit"
    )

    bat_ruta = os.path.join(ruta_raiz, f"{Mem_AplNue}.bat")
    with open(bat_ruta, "w", encoding="utf-8") as f:
        f.write(Mem_YosMnu_Txt_Bat)
    Mem_Inf.append(f"Lanzador : {Mem_AplNue}.bat generado")


    if builtins.Mem_Ini_AplEtn == "Txt":    # Entorno Txt
        # INFORME FINAL
        print("\n  " + "═"*55)
        print(f"  GENERANDO APLICACION : {Mem_AplNue}")
        for linea in Mem_Inf: print(f"    {linea}")
        print("  "+"═"*55 + "\n")
    else:
        Mem_Inf_Str = "\n".join(Mem_Inf)
        Mem_Inf_Str = Mem_Inf_Str.replace("\n", "<br>")
        Mem_Inf_Str = Mem_Inf_Str.replace(" ", "&nbsp;")

        return Yos.Yos_Msg_Frm(
            Fnc_Tit=f'GENERANDO APLICACION : {Mem_AplNue}',
            Fnc_Msg=Mem_Inf_Str,
            Fnc_Tip="Inf",
            Ancho="450px",
            Alto="auto"
        )

    return True
################################# A REVISAR #################################################################

#############################################################################################################
def MstFncLin(FncNiv="Act"):
    # Mustra la Funcion que llamo a la Funcion ACTUAL (Act/Ant)
    #    from Yos import MstFncLin
    #    input(MstFncLin(FncNiv="All"))

    if YosCfg["Dbg"]=="S": print("******** Yos.MstFncLin() ********")
    if YosCfg["Dbg"]=="S": print(f"FncNiv={FncNiv}")

    match FncNiv:
        case "Ant": # Anterior
            marco_llamador = sys._getframe(2)
        case "All":
            lineas = []
            actual = sys._getframe(1)
            nivel = 0
            while actual:
                nombre = actual.f_code.co_filename
                fnc = actual.f_code.co_name
                lin = actual.f_lineno
                lineas.append(f"[{nivel:02d}] {nombre} -> {fnc} (L{lin})")
                actual = actual.f_back
                nivel += 1
            return "\n".join(lineas)
        case _:
            print("Actual")
            marco_llamador = sys._getframe(1)

    nombre_archivo = marco_llamador.f_code.co_filename
    numero_linea = marco_llamador.f_lineno
    return f"- {nombre_archivo} - {numero_linea}"

def YosCfg_Rcu(**FncDic):
    # Busca dentro de YosCfg las Clm del prefijo indicado Yos.YosCfg_Rcu(CodBus='_Prefijo_')
    if YosCfg["Dbg"]=="S": print("******** Yos.YosCfg_Rcu() ********")
    if YosCfg["Dbg"]=="S": print(f"FncDic={FncDic}")
    Fnc_Txt="Yos.YosCfg_Rcu(CodBus='_Prefijo_')"

    if not 'CodBus' in FncDic:
       FrmWit(Fnc_Wit=8, Fnc_Txt=f"{Fnc_Txt} La clave 'CodBus' no existe."+ MstFncLin("Ant"))
       return {}

    SalDat={k: v for k, v in YosCfg.items() if k.startswith(FncDic["CodBus"])}
    print(SalDat)
    #for key in YosCfg: # O for key in shelf.keys():
    #    print(f"Clave: {key} -> Valor: {YosCfg[key]}")

def EmlEnv(Destinatario=None, Asunto="", Cuerpo=""):
    # Envia un Email
    #Yos.EmlEnv("mmedina@upnfm.edu.hn", "Contacto desde YosCtr", "Desde Python con amor.")
    # Caso A (Un solo amigo): EmlEnv("mtcyos@yahoo.es", "Aviso", "Hola Bin")
    # Caso B (Varios socios): EmlEnv(["mtcyos@yahoo.es", "socio@gmail.com"], "Reporte", "Adjunto datos")

    from prompt_toolkit.application import Application
    from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
    from prompt_toolkit.widgets import TextArea, Button, Label, Frame
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.styles import Style as PtStyle
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.layout.containers import FloatContainer, Float, ConditionalContainer
    from prompt_toolkit.filters import Condition
    from prompt_toolkit.shortcuts import message_dialog
    from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard

    import smtplib
    from email.message import EmailMessage
    from colorama import Fore, Back, Style

    from Yos import FrmCls, FrmWit, FrmLin, AplIni

    if not YosCfg.get("Eml_Svr", "").strip():
        FrmWit(f'\n{Fore.RED} [ ERROR ] El servidor de (YosCfg."Eml_Svr") correo no está configurado la tabla Dat.' ,8)
        return False

    Mem_EmlDst = "N"
    if Destinatario == "Eml_EmlDst":
        if "Eml_EmlDst" in YosCfg:
            Destinatario = YosCfg["Eml_EmlDst"]
            Mem_EmlDst = "S"
        else:
            Mem_MsgErr = '[ ERROR ] No se ha definido el destinatario Eml_EmlDst en la tabla Dat.'
            FrmWit(Mem_MsgErr, 8)
            return False

    FrmCls()
#    print()
#    print(f"{Fore.YELLOW}{FrmLin('ENVÍO DE EMAIL', 'C')}{Style.RESET_ALL}")
    print()

    # 2. Configuración de Medidas
    Mem_Tit = "*** ENVÍO DE EMAIL *** (F2 - Ayuda)"
    Mem_F2 = """Destinatario :
    Un solo email : nombre@yahoo.es
    Varios emails : uno@yahoo.es, dos@gmail.com

Su Nombre    :
Su Email     :
    Son campos optativos

Asunto       : Asunto del email
Mensaje      : mensaje del email, puede añadir líneas pulsando INTRO al final de la línea"""
    Mem_F2_WX = 95
    Mem_F2_HY = 10

    Mem_WX = 95
    Mem_HY = 20

    if not Destinatario or not Asunto or not Cuerpo:
        if Mem_EmlDst == "S":
            txt_dest = TextArea(
                text=Destinatario if Destinatario else "",
                multiline=False,
                read_only=True  # 🔒 Esto bloquea la edición del usuario
            )
        else:
            txt_dest = TextArea(text=Destinatario if Destinatario else "", multiline=False)

        txt_nom = TextArea(multiline=False)
        txt_eml = TextArea(multiline=False)
        txt_asun = TextArea(text=Asunto if Asunto else "", multiline=False)
        txt_cuerpo = TextArea(text=Cuerpo if Cuerpo else "")
        lbl_error = Label("", style="fg:ansired bold")

        def aceptar_handler():
            if not txt_dest.text.strip():
                lbl_error.text = "✖ Error : DEBE INDICAR EL DESTINATARIO"
                app.layout.focus(txt_dest)
                return
            if not txt_asun.text.strip():
                lbl_error.text = "✖ Error : DEBE INDICAR EL ASUNTO"
                app.layout.focus(txt_asun)
                return
            if not txt_cuerpo.text.strip():
                lbl_error.text = "✖ Error : DEBE ESCRIBIR UN MENSAJE"
                app.layout.focus(txt_cuerpo)
                return
            app.exit(result=True)

        def cancelar_handler():
            app.exit(result=False)

        btn_enviar = Button(" ENVIAR ", handler=aceptar_handler)
        btn_enviar.left_symbol = ""; btn_enviar.right_symbol = ""
        btn_cancelar = Button(" CANCELAR ", handler=cancelar_handler)
        btn_cancelar.left_symbol = ""; btn_cancelar.right_symbol = ""

        kb = KeyBindings()

        # ---------------- VARIABLES Y LÓGICA DEL POPUP DE AYUDA F2 ----------------
        estado_ayuda = {"visible": False}

        @Condition
        def is_help_visible():
            return estado_ayuda["visible"]

        def ocultar_ayuda():
            estado_ayuda["visible"] = False
            # Recuperamos foco al cuerpo o al botón
            app.layout.focus(txt_cuerpo)

        txt_cuerpo_ayuda = TextArea(
            text=Mem_F2,
            multiline=True,
            read_only=True,   # Solo lectura
            scrollbar=True,   # Activa la barra lateral
            focusable=True,   # Importante para que las flechas funcionen
            width=Mem_F2_WX,         # Ancho estándar para el cuadro de ayuda
            height=Mem_F2_HY,        # Alto estándar (ajusta según necesites)
            style="fg:ansiwhite bg:black"
        )

        btn_cerrar_ayuda = Button(" CERRAR ", handler=ocultar_ayuda)
        btn_cerrar_ayuda.left_symbol = ""; btn_cerrar_ayuda.right_symbol = ""

        marco_ayuda = Frame(
            body=HSplit([
                Window(height=1),
                txt_cuerpo_ayuda, # Reemplazamos el Label por el TextArea
                Window(height=1),
                VSplit([Window(), btn_cerrar_ayuda, Window()])
            ]),
            title=HTML("<b><ansiyellow>*** AYUDA ***</ansiyellow></b>"),
            style="fg:ansicyan bg:black"
        )

        ayuda_float = Float(
            content=ConditionalContainer(content=marco_ayuda, filter=is_help_visible),
            transparent=False
        )

        @kb.add('f2')   # Ayuda Flotante
        def _(event):
            estado_ayuda["visible"] = True
            event.app.layout.focus(txt_cuerpo_ayuda) #btn_cerrar_ayuda)

        @kb.add('escape')
        def _(event):
            if estado_ayuda["visible"]:
                ocultar_ayuda()
            else:
                event.app.exit(result=False)

        @kb.add('c-v', eager=True)    # Ctrl + V Pegar del portapapeles
        def _(event):
            """Fuerza el pegado limpio desde el portapapeles de Windows"""
            data = event.app.clipboard.get_data()
            event.current_buffer.insert_text(data.text)

        @kb.add('c-c')    # CTRL + C (Copiar o Salida de emergencia)
        def _(event):
            buffer = event.current_buffer
            if buffer.selection_state:
                data = buffer.copy_selection()
                event.app.clipboard.set_data(data)
            else:
                if AccReg == "Ver":
                    do_copy_clipboard()
                else:
                    event.app.exit(result=False)

#        @kb.add('c-c')
#        def _(event):
#            event.app.exit(result=False)

        @kb.add('tab', filter=is_help_visible)
        def _(event):
            # Ciclo cerrado dentro de la ayuda
            if event.app.layout.has_focus(txt_cuerpo_ayuda):
                event.app.layout.focus(btn_cerrar_ayuda)
            else:
                event.app.layout.focus(txt_cuerpo_ayuda)

        # --- TAB: Para cuando la ayuda está CERRADA (Email normal) ---
        @kb.add('tab', filter=~is_help_visible) # El símbolo ~ significa "NO"
        def _(event):
            event.app.layout.focus_next()

        @kb.add('s-tab', filter=is_help_visible)
        def _(event):
            if event.app.layout.has_focus(btn_cerrar_ayuda):
                event.app.layout.focus(txt_cuerpo_ayuda)
            else:
                event.app.layout.focus(btn_cerrar_ayuda)

        # --- SHIFT-TAB: Para cuando la ayuda está CERRADA (Email normal) ---
        @kb.add('s-tab', filter=~is_help_visible)
        def _(event):
            event.app.layout.focus_previous()

        @kb.add('pageup', filter=is_help_visible)
        def _(event):
            # Desplaza el cursor 10 líneas hacia arriba
            for _ in range(10):
                txt_cuerpo_ayuda.buffer.cursor_up()

        @kb.add('pagedown', filter=is_help_visible)
        def _(event):
            # Desplaza el cursor 10 líneas hacia abajo
            for _ in range(10):
                txt_cuerpo_ayuda.buffer.cursor_down()


        cuerpo_frame = HSplit([
            Label(""),
            VSplit([Label(HTML("  <ansiyellow>Destinatario : </ansiyellow>"), width=18), txt_dest]),
            Label(""),
            VSplit([Label(HTML("  <ansiyellow>Su Nombre    : </ansiyellow>"), width=18), txt_nom]),
            Label(""),
            VSplit([Label(HTML("  <ansiyellow>Su Email     : </ansiyellow>"), width=18), txt_eml]),
            Label(""),
            VSplit([Label(HTML("  <ansiyellow>Asunto       : </ansiyellow>"), width=18), txt_asun]),
            Label(""),
            VSplit([Label(HTML("  <ansiyellow>Mensaje      : </ansiyellow>"), width=18), txt_cuerpo]),
            Label(""),
            lbl_error,
            Label(""),
            VSplit([Window(), btn_enviar, Label("    "), btn_cancelar, Window()])
        ])

        marco = Frame(
            body=cuerpo_frame,
            title=HTML(f"<b><ansigreen>{Mem_Tit}</ansigreen></b>"),
            width=Mem_WX,
            height=Mem_HY
        )

#        layout_formulario = HSplit([
#            VSplit([Window(), marco, Window()]),
#            Window()
#        ])
        layout_base = HSplit([
            VSplit([Window(), marco, Window()]), # El marco ahora está al tope
            Window()                             # Este empuja todo desde abajo hacia arriba
        ])

        layout_formulario = FloatContainer(
            content=layout_base,
            floats=[ayuda_float]
        )

        estilo_eml = PtStyle([
            ("button", "fg:white bg:#0000aa"),
            ("button.focused", "fg:white bg:#00aa00 bold"),
            ("text-area", "bg:#333333 fg:white"),
            ("frame.border", "fg:ansigreen"),
            ("frame.label", "fg:ansigreen"),
        ])

        app = Application(
            layout=Layout(layout_formulario),
            key_bindings=kb,
            style=estilo_eml,
            clipboard=PyperclipClipboard(),
            mouse_support=True,
            full_screen=False,
            erase_when_done=True
        )

        # Foco inicial inteligente
        if not Destinatario: app.layout.focus(txt_dest)
        elif not Asunto: app.layout.focus(txt_asun)
        else: app.layout.focus(txt_cuerpo)

        if not app.run():
            FrmWit(f"\n [ ATENCION ] Envío de email cancelado por el usuario." ,8)
            return False

        Destinatario = txt_dest.text.strip()
        Asunto = txt_asun.text.strip()
        Cuerpo_Final = txt_cuerpo.text.strip()
        Mem_Nom = txt_nom.text.strip()
        Mem_Eml = txt_eml.text.strip()

        MemCab = ""
        if Mem_Nom:
            MemCab += f"{Mem_Nom}\n"
        if Mem_Eml:
            MemCab += f"Correo Electrónico : {Mem_Eml}\n"
        if MemCab:
            MemCab += "*****************************************\n"
        Cuerpo = MemCab + Cuerpo_Final

    Cuerpo = YosCfg["Eml_MsgCab"].replace("\\n", "\n") +Cuerpo + YosCfg["Eml_MsgPie"].replace("\\n", "\n")

    # 1. Normalización: Si es un string, lo convertimos en lista de un elemento
    if isinstance(Destinatario, str):
        Lista_Dest = [Destinatario]
    else:
        Lista_Dest = Destinatario

    # 3. Construcción del mensaje
    Msg = EmailMessage()
    Msg['Subject'] = Asunto
    Msg['From'] = f'{YosCfg["Eml_EmlEnv"]} <{YosCfg["Eml_EmlEnv"]}>'
    Msg['To'] = ", ".join(Lista_Dest)
    Msg.set_content(Cuerpo)

    try:
        with smtplib.SMTP(YosCfg["Eml_Svr"], YosCfg["Eml_Puo"]) as server:
            server.starttls()
            server.login(YosCfg["Eml_Usr"], YosCfg["Eml_Pas"])
            # Enviamos a la lista completa
            server.send_message(Msg)
        FrmWit(f' [ OK ] SISTEMA: Correo enviado a {len(Lista_Dest)} destinatario(s).' ,8)
        return True
    except Exception as e:
        error_seguro = str(e).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        FrmWit(f' [ ERROR ] {error_seguro}.' ,8)
        print(f"ERROR EmlEnv: {e}")
        return False

def Yos_TxtMulLin(Fnc_Esp=0):
    # Introduce los datos en un Texto Multilinea
    from colorama import Fore, Back, Style

    try:
        # Convertimos a entero. Si es "8", se vuelve 8.
        Fnc_Esp = int(Fnc_Esp)
    except (ValueError, TypeError):
        # Si mandan algo que no es número (ej: "hola"), volvemos a 0
        Fnc_Esp = 0

    print(f"{Style.BRIGHT}{Fore.BLUE}{FrmLin('Ingrese el texto (Deje una línea en blanco y presione Enter para finalizar.', Fnc_Esp)}")
    lineas = []

    # Iniciamos el conteo según tu regla de numeración [cite: 2026-01-20]
    while True:
#       linea = input(f"{len(lineas) + 1}-> ")
        linea = input(f"{Fore.YELLOW}{FrmLin(f'{len(lineas) + 1}-> ', 8)}{Style.RESET_ALL}")
        if linea == "": # Si la línea está vacía, terminamos
            break
        lineas.append(linea)

    texto_final = "\n".join(lineas)
    return texto_final

def Yos_ClipCopy(texto):
    # Manda el texto a PortaPapeles
    import pyperclip
    """
    Copia cualquier cadena al portapapeles del sistema operativo actual.
    """
    try:
        # 1. Limpiamos espacios laterales para evitar errores de pegado
        cadena = str(texto).strip()

        # 2. Comando universal
        pyperclip.copy(cadena)

        return True
    except Exception as e:
        input(f"Error Portapapeles: {e}")
        return False

def Yos_Pas(prompt=""):
    # Entrada de datos tipo Password
    import msvcrt
    import sys

    print(prompt, end='', flush=True)
    pw = ""
    while True:
        # Capturamos una tecla sin que se vea en pantalla
        char = msvcrt.getch()

        # Si es Enter (CR o LF)
        if char in (b'\r', b'\n'):
            print() # Salto de línea al terminar
            break

        # Si es Backspace (Borrar)
        elif char == b'\x08':
            if len(pw) > 0:
                pw = pw[:-1]
                # Truco para borrar el asterisco en la consola:
                # Retroceder (\b), Espacio (borra), Retroceder (\b)
                sys.stdout.write('\b \b')
                sys.stdout.flush()

        # Si es cualquier otro carácter (evitamos teclas de función)
        elif len(char) == 1 and char >= b' ':
            try:
                pw += char.decode('utf-8')
                sys.stdout.write('*')
                sys.stdout.flush()
            except:
                pass # Ignorar caracteres extraños

    return pw

def Yos_TimeStamp(Fnc_Nue=""):
    # Devuelve el formato TimeStamp , Fnc_Nue =="Cre" añado la marca de registro nuevo +"*"
    from datetime import datetime

    Mem_TimeStamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if Fnc_Nue =="Cre":
        Mem_TimeStamp = Mem_TimeStamp +"*"
    else:
        Mem_TimeStamp = Mem_TimeStamp +" "

    return Mem_TimeStamp

def Yos_SutTxt(Fnc_Txt=""):
    # Sustituye comando definidos por sus datos
    # Se usan para guardar el Bases de datos o en algun sitio que no se pueda guardar el valor real porque puede variar

    if not Fnc_Txt:
        return Fnc_Txt
    Mem_Txt = Fnc_Txt

    # «YosLib_Dir» -> Direccion de la Libreria Yos
    Fnc_Txt = Fnc_Txt.replace("«YosLib_Dir»", YosCfg["Yos_Dir"])

    return Fnc_Txt

# PARA REVISION *********************************************************************
def Dic_Rcu(Fnc_Pre, Fnc_Dic="gcAplDat"):
    # Devuelve un Dicccionario Segun el Prefijo de los datos "Yos_"
    if YosCfg["Dbg"]=="S": print("******** Yos.Dic_Rcu() ********")
    print("YosCfg="+YosCfg)

    if isinstance(Fnc_Dic, dict):
        if gcAplDat["Dbg"]=="S": print("Es un diccionario Reg."+str(len(Fnc_Dic))+" Fnc_Pre="+Fnc_Pre)
        if gcAplDat["Dbg"]=="S": print(Fnc_Dic)
        SalDat={k: v for k, v in Fnc_Dic.items() if k.startswith(Fnc_Pre)}
    else:
        if gcAplDat["Dbg"]=="S": print("No es un diccionario")
        SalDat={}

    return SalDat

def Yos_Md5(Fnc_Txt):
    # Convierte Texto a Md5
    import hashlib
    md5_hash = hashlib.md5()
    Fnc_Txt = Fnc_Txt.encode('utf-8')
#    print(Fnc_Txt)
    md5_hash.update(Fnc_Txt)
    Fnc_Txt = md5_hash.hexdigest()
 #   print(Fnc_Txt)
    return Fnc_Txt

def Yos_Otp(Fnc_Txt):
    #def GenOtp()

    # Generate a secure random secret key (store this securely!)
    # It should be base32 encoded for compatibility with pyotp
    secret = base64.b32encode(pyotp.random_base32().encode()).decode()

    # Create a TOTP object
    totp = pyotp.TOTP(secret)

    # Generate a current OTP
    current_otp = totp.now()
    print(f"CODIGO TOTP: {current_otp}")

    # Verify an OTP (e.g., entered by the user)B
    user_entered_otp = input("Enter the OTP: ")
    if totp.verify(user_entered_otp):
        print("OTP verified successfully!")
    else:
            print("Invalid OTP.")

    # To generate a provisioning URI for QR code generation (e.g., for Google Authenticator)
    # Replace 'YourAppName' and 'user@example.com' with your actual values
    provisioning_uri = totp.provisioning_uri(name='user@example.com', issuer_name='YourAppName')
    print(f"Provisioning URI: {provisioning_uri}")

######################################################################
"""
def Yos_Frm_Acd():
    import builtins
    from Yos import FrmMsg

    YosCfg = builtins.YosCfg
    Mem_Tab = "&nbsp;&nbsp;&nbsp;&nbsp;"

    Mem_Dat = f'<b>ENTORNO</b><br>{Mem_Tab}S.O. : {YosCfg["Etn"]} - {YosCfg["Etn_Des"]}<br><br>'
    Mem_Dat = Mem_Dat + f'<b>APLICACION</b><br>{Mem_Tab}{YosCfg["Apl_Apl"]}<br>{Mem_Tab}{Mem_Tab}{YosCfg["Apl_Nom"]}<br>{Mem_Tab}{Mem_Tab}Ver. {YosCfg["Apl_Vsn"]}<br>{Mem_Tab}{Mem_Tab}{YosCfg["Apl_Cpy"]}<br>{Mem_Tab}{Mem_Tab}email : {YosCfg["Apl_CpyEml"]}<br><br>'
    Mem_Dat = Mem_Dat + f'<b>LIBRERIAS</b><br>{Mem_Tab}{YosCfg["Yos_Apl"]} - {YosCfg["Yos_Nom"]} - Ver. {YosCfg["Yos_Vsn"]}<br>{Mem_Tab}{Mem_Tab}{YosCfg["Yos_Cpy"]}'

    FrmMsg(Fnc_Tit="ACERCA DE ...", Fnc_Msg=Mem_Dat, Mem_AplOri="Inf")

def Yos_Frm_AcdRes():
    import builtins
    from Yos import FrmMsg

    YosCfg = builtins.YosCfg
    Mem_Dat = f'{YosCfg["Apl_Apl"]}<br>{YosCfg["Apl_Nom"]}<br><br>Licenciado bajo la Licencia MIT.<br><br>Consulte el archivo LICENCIA en la raíz del proyecto para más información'

    FrmMsg(Fnc_Tit="AVISO DE DESCARGO DE RESPONSABILIDAD", Fnc_Msg=Mem_Dat, Mem_AplOri="Inf", Ancho="500px")


def Yos_Frm_Acd():
    import builtins
    from Yos import FrmMsg

    YosCfg = getattr(builtins, 'YosCfg', getattr(builtins, 'Cfg', {}))
    if not YosCfg: return

    Mem_Tab = "&nbsp;" * 4

# Bloque de Entorno con auto-detección de errores
    Mem_Dat = f"<b>ENTORNO</b><br>{Mem_Tab}S.O. : {YosCfg.get('Ent', 'Err : Ent')} - {YosCfg.get('Etn_Des', 'Err : Etn_Des')}<br><br>"

    # Bloque de Aplicación
    Mem_Dat += f"<b>APLICACION</b><br>{Mem_Tab}{YosCfg.get('Apl_Apl', 'Err : Apl_Apl')}<br>"
    Mem_Dat += f"{Mem_Tab}{Mem_Tab}{YosCfg.get('Apl_Nom', 'Err : Apl_Nom')}<br>"
    Mem_Dat += f"{Mem_Tab}{Mem_Tab}Ver. {YosCfg.get('Apl_Vsn', 'Err : Apl_Vsn')}<br>"
    Mem_Dat += f"{Mem_Tab}{Mem_Tab}{YosCfg.get('Apl_Cpy', 'Err : Apl_Cpy')}<br>"
    Mem_Dat += f"{Mem_Tab}{Mem_Tab}email : {YosCfg.get('Apl_CpyEml', 'Err : Apl_CpyEml')}<br><br>"

    # Bloque de Librerías
    Mem_Dat += f"<b>LIBRERIAS</b><br>{Mem_Tab}{YosCfg.get('Yos_Apl', 'Err : Yos_Apl')} - Ver. {YosCfg.get('Yos_Vsn', 'Err : Yos_Vsn')}<br>"
    Mem_Dat += f"{Mem_Tab}{Mem_Tab}{YosCfg.get('Yos_Cpy', 'Err : Yos_Cpy')}"

    FrmMsg(Fnc_Tit="ACERCA DE ...", Fnc_Msg=Mem_Dat, Mem_AplOri="Inf")
"""
