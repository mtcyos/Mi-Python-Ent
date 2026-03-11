# -*- coding: utf-8 -*-
import inspect
#import sqlite3
import os
import re
import sys
import ctypes
import locale
import msvcrt

from colorama import init, Fore, Style, Back
init(autoreset=True)

from Yos import FrmCls, FrmWit, FrmLin, AplIni, Yos_TimeStamp
# 1. Configurar locale
try:
    locale.setlocale(locale.LC_TIME, "")
except:
    pass

# =============================================================================
# FUNCIONES DE APOYO
# =============================================================================
def maximizar_consola():
    if os.name == 'nt':
        try:
            kernel32 = ctypes.WinDLL('kernel32')
            user32 = ctypes.WinDLL('user32')
            hWnd = kernel32.GetConsoleWindow()
            if hWnd:
                user32.ShowWindow(hWnd, 3)
                hOut = kernel32.GetStdHandle(-11)
                kernel32.SetConsoleDisplayMode(hOut, 1, ctypes.byref(ctypes.c_long()))
        except: pass

def obtener_anchos_reales():
    try:
        Mem_Ancho = os.get_terminal_size().columns - (len(Mem_Tab_Brw) * 3)
    except:
        Mem_Ancho = 118
    anchos_finales = [0] * len(Mem_Tab_Brw)
    espacio_restante = Mem_Ancho
    indices_con_porcentaje = []
    for i, col in enumerate(Mem_Tab_Brw):
        ancho_config = str(col[1])
        if "%" not in ancho_config:
            valor_fijo = int(ancho_config)
            anchos_finales[i] = valor_fijo
            espacio_restante -= valor_fijo
        else:
            indices_con_porcentaje.append(i)
    if indices_con_porcentaje:
        total_slots = len(indices_con_porcentaje)
        for i, idx in enumerate(indices_con_porcentaje):
            if i == total_slots - 1:
                anchos_finales[idx] = max(0, espacio_restante)
            else:
                porcentaje_valor = int(str(Mem_Tab_Brw[idx][1]).replace("%", ""))
                ancho_calculado = int((porcentaje_valor / 100) * espacio_restante)
                anchos_finales[idx] = ancho_calculado
                espacio_restante -= ancho_calculado
    return anchos_finales

# =============================================================================
# BUSCAR
# =============================================================================
def busqueda_incremental_dinamica(conn, db_col_names, anchos):
    global offset, fila_resaltada, nLin, order_by_col, Mem_Ftr
    bus = ""
    pad = " " * MARGEN
    where_ftr = f"WHERE {order_by_col} LIKE ?" if Mem_Ftr else ""

    while True:
        os.system('cls')
        cur = conn.cursor()
        op_and = "AND" if where_ftr else "WHERE"
        params_bus = (f"%{Mem_Ftr}%", bus) if Mem_Ftr else (bus,)
        cur.execute(f"SELECT COUNT(*) FROM {Mem_Tab_Nom} {where_ftr} {op_and} {order_by_col} < ? COLLATE NOCASE", params_bus)
        posicion_real = Mem_Cur_YosCfg.fetchone()[0]
        mitad = nLin // 2
        offset_temp = max(0, posicion_real - mitad)

        cur.execute(f"SELECT {order_by_col} FROM {Mem_Tab_Nom} {where_ftr} {op_and} {order_by_col} >= ? COLLATE NOCASE ORDER BY {order_by_col} COLLATE NOCASE LIMIT 1", params_bus)
        res = Mem_Cur_YosCfg.fetchone()
        fila_resaltada = res[0] if res else None

        etiqueta_orden = next((o[0] for o in Mem_Tab_Ord if o[1] == order_by_col), order_by_col)

        print(f"{Back.GREEN}{Fore.BLACK} Buscar en {etiqueta_orden} : {bus.ljust(20)} {Style.RESET_ALL}")
        print(f"{Fore.WHITE} [Letras]: Buscar | [Enter]: Aceptar | [Esc]: Cancelar\n")

        params_sel = (f"%{Mem_Ftr}%",) if Mem_Ftr else ()
        cur.execute(f"SELECT rowid, *, ({order_by_col}) as ord_val FROM {Mem_Tab_Nom} {where_ftr} ORDER BY {order_by_col} COLLATE NOCASE LIMIT {nLin} OFFSET {offset_temp}", params_sel)
        regs = Mem_Cur_YosCfg.fetchall()

        for idx, r in enumerate(regs):
            n_fila = str(idx + 1).zfill(2)
            val_comparar = str(r[-1])
            es_esta_fila = (fila_resaltada is not None and val_comparar.upper() == str(fila_resaltada).upper())
            bg = Back.YELLOW if es_esta_fila else ""
            fg = Fore.BLACK if es_esta_fila else Fore.CYAN
            linea = f"{bg}{Fore.YELLOW if not bg else Fore.BLACK}{pad}{n_fila.ljust(anchos[0])}{pad}{Style.RESET_ALL}{Fore.BLUE}|"
            for i in range(1, len(Mem_Tab_Brw)):
                idx_bd = db_col_names.index(Mem_Tab_Brw[i][2]) + 1 if Mem_Tab_Brw[i][2] else 0
                valor = str(r[idx_bd] if idx_bd > 0 and r[idx_bd] is not None else "")[:anchos[i]].ljust(anchos[i])
                linea += f"{bg}{fg}{pad}{valor}{pad}{Style.RESET_ALL}{Fore.BLUE}|"
            print(linea)

        for _ in range(nLin - len(regs)): print("")
        print(Fore.BLUE + "═" * (sum(anchos) + len(anchos) * 3))

        char = msvcrt.getch()
        if char == b'\r':
            offset = offset_temp
            break
        elif char == b'\x1b':
            fila_resaltada = None
            break
        elif char == b'\x08':
            bus = bus[:-1]
        else:
            try:
                if len(bus) < 20: bus += char.decode('utf-8')
            except: pass

# =============================================================================
# FORMULARIO YOS
# =============================================================================
def formulario_yos(db_col_names, registro=None, solo_lectura=False, eliminar=False):
    global usuario_actual
    os.system('cls')

    datos_temp = {}
    for f in Mem_Tab_ClmMod:
        nom_col = f[0]  # cClm
        if registro:
            idx_bd = db_col_names.index(nom_col) + 1
            datos_temp[nom_col] = str(registro[idx_bd] if registro[idx_bd] is not None else "")
        else:
            datos_temp[nom_col] = ""
    if registro:
        reg_dict = dict(registro)
        datos_temp['cModRegNik'] = reg_dict.get('cModRegNik', usuario_actual)
        datos_temp['cModRegTim'] = reg_dict.get('cModRegTim', Yos_TimeStamp())
    else:
        datos_temp['cModRegNik'] = usuario_actual
        datos_temp['cModRegTim'] = Yos_TimeStamp(Fnc_Nue="Cre")

    Mem_Lon_Cab = max(len(str(f[1])) for f in Mem_Tab_ClmMod)   # cCab

    while True:
        os.system('cls')

        if eliminar: titulo = " ELIMINAR "
        elif solo_lectura: titulo = " CONSULTAR "
        else: titulo = " MODIFICAR " if registro else " NUEVO "

        print(f"\n{Back.CYAN}{Fore.BLACK} {titulo} {Style.RESET_ALL}\n")

        contador_opc = 1
        mapeo_opciones = {}

        for i, f in enumerate(Mem_Tab_ClmMod):
            t = Mem_Tab_ClmMod_Def[i]
            # cClm
            nom_col = f[0]
            # cCab
            etiqueta = f[1]
            # cMod
            permiso = str(f[2]).strip()
            if eliminar or solo_lectura:
                es_modificable = False
            else:
                if registro: # Estamos en modo MODIFICAR
                    es_modificable = (permiso == "Mod")
                else:        # Estamos en modo NUEVO (CREAR)
                    es_modificable = (permiso in ["Cre", "Mod"])
            # cNul
            es_not_nul = (f[3] == "N")

            if es_modificable:
                n_campo = str(contador_opc).zfill(2)
                mapeo_opciones[n_campo] = (f, t)
                prefix = f"{Fore.GREEN}{n_campo}"
                asterisco = f"{Fore.RED}*" if es_not_nul else " "
                contador_opc += 1
            else:
                prefix = "  "
                asterisco =" "

            valor_actual = datos_temp[nom_col]
            ancho_real = t[1]
            guiones = "_" * max(0, ancho_real - len(valor_actual))

            print(f"{prefix}{asterisco}{Fore.YELLOW}{etiqueta.ljust(Mem_Lon_Cab)} : {Fore.WHITE}{valor_actual}")#{Fore.LIGHTBLACK_EX}{guiones}")

        print(f"\n   {Fore.CYAN}{'USUARIO'.ljust(Mem_Lon_Cab)} : {Fore.YELLOW}{datos_temp.get('cModRegNik','')}")
        print(f"   {Fore.CYAN}{'MODIFICADO'.ljust(Mem_Lon_Cab)} : {Fore.YELLOW}{datos_temp.get('cModRegTim','')}")

        if eliminar:
            return None

        elif solo_lectura:
            print(f"\n {Fore.WHITE}ENTER -> Volver | {Fore.YELLOW}C -> Copiar al Clipboard | {Fore.CYAN}E -> Envial Email{Style.RESET_ALL}")
            opc_ver = input(f"\n {Fore.YELLOW}OPCIÓN > {Style.RESET_ALL}").strip().upper()

            if opc_ver in [ 'C', 'E']:
                ancho_max = len("CAMPO")
                for f in Mem_Tab_ClmMod:
                    if len(f[1]) > ancho_max:
                        ancho_max = len(f[1])

                bloque_md = f"**** TABLA: {globals().get('Mem_Tab_Nom')} - CONSULTA DE REGISTRO****\n"
                bloque_md += f"| {'CAMPO'.ljust(ancho_max)} | Valor |\n"
                bloque_md += "|------------------------------------------\n"

                for f in Mem_Tab_ClmMod:
                    titular = f[1].ljust(ancho_max) # Rellena con espacios hasta el máximo
                    campo = f[0]
                    valor = datos_temp.get(campo, "")
                    val_limpio = str(valor).replace("|", "-") if valor else ""

                    bloque_md += f"| {titular} : {val_limpio} \n"

                if opc_ver=="C":
                    from Yos import Yos_ClipCopy
                    if Yos_ClipCopy(bloque_md):
                        print(f'\n{Style.BRIGHT}{Fore.BLUE} [ OK ] Datos enviados al Portapapeles.')
                    else:
                        print(f'\n{Fore.RED} [ ERROR ] Los datos no se pudieron enviar al Portapapeles.')
                    FrmWit()
                else:
                    from Yos import EmlEnv
                    EmlEnv("", "", bloque_md)

            return None

        print(f"\n {Fore.WHITE}Nº -> Modificar | {Fore.CYAN}9999 -> En secuencia | {Fore.GREEN}G-Grabar | {Fore.RED}S-Salir")
        opc = input(f"\n{Fore.YELLOW} OPCIÓN > {Fore.RESET}").strip().upper()

        if opc == '9999':
            pasos = sorted(mapeo_opciones.keys())
            for n_paso in pasos:
                f, t = mapeo_opciones[n_paso]
                nom_col = f[0]
                Pre_valor = datos_temp[nom_col]
                Pre_LonTot = t[1]
                es_obligatorio = (f[3] == "N")
                opciones_validas = f[4]  # Aquí están tus 'Cab,Opc' o ',Windows,Linux'

                txt_obligatorio = f"{Back.RED}{Fore.WHITE} OBLIGATORIO {Style.RESET_ALL}" if f[3] == 'N' else ""

                print(f"\n {Back.YELLOW}{Fore.BLACK} PASO {n_paso}/{len(pasos)}: {f[1]} {Style.RESET_ALL} {txt_obligatorio}")

                # Si existen opciones, las mostramos como ayuda
                if opciones_validas:
                    print(f" {Fore.CYAN}Opciones: {Fore.WHITE}{opciones_validas}")

                val_str = str(Pre_valor) if Pre_valor is not None else ""
                guiones = "_" * max(0, Pre_LonTot - len(val_str))
                print(f" {Fore.WHITE}Valor Actual: {Pre_valor}{Fore.LIGHTBLACK_EX}{guiones}")
                while True: # Bucle de validación por campo
                    nuevo_val = input(f" {Fore.YELLOW}Nuevo Valor > {Fore.WHITE}").strip()

                    # Si es ENTER, mantenemos el actual (si no es nulo obligatorio)
                    if not nuevo_val:
                        if es_obligatorio and not Pre_valor:
                            print(f" {Fore.RED}ERROR: Campo obligatorio.")
                            continue
                        nuevo_val = Pre_valor
                        break

                    # Validaciones (Longitud y Opciones)
                    if len(nuevo_val) > Pre_LonTot:
                        print(f" {Fore.RED}ERROR: Máximo {Pre_LonTot} caracteres.")
                        continue

                    if opciones_validas:
                        Mem_OpcVal = tuple(x.strip() for x in opciones_validas.split(','))
                        if nuevo_val not in Mem_OpcVal:
                            print(f" {Fore.RED}ERROR: Valor no permitido.")
                            continue

                    break # Todo bien, pasamos al siguiente campo

                datos_temp[nom_col] = nuevo_val

        elif opc == 'G':
            error_nn = False
            for i, f in enumerate(Mem_Tab_ClmMod):
                t = Mem_Tab_ClmMod_Def[i]

                es_obligatorio = (f[3] == 1)
                opciones_validas = f[4] # El cuarto elemento de Mem_Tab_ClmMod
                Mem_val =datos_temp[f[0]].strip()
                Pre_LonTot=t[1]

#                print(es_obligatorio)
#                print(Pre_LonTot)
#                print(opciones_validas)
#                input(Mem_val)

                # 1. Verificación de OBLIGATORIO Mem_Tab_Clm.cNul="N"
                if es_obligatorio and not Mem_val:
                    print(f"{Fore.RED}ERROR: El campo {f[1]} es obligatorio (*).")
                    error_nn = True
                    msvcrt.getch()
                    break

                # 2. Verificación de LONGITUD
                if len(Mem_val) > Pre_LonTot:
                    print(f"{Fore.RED}ERROR: El campo {f[1]} supera longitud máxima superada ({Pre_LonTot}).")
                    error_nn = True
                    msvcrt.getch()
                    break

                # 3. Verificación de OPCIÓN
                if opciones_validas:
                    # Convertimos la cadena plana en tupla, limpiando espacios accidentales
                    Mem_OpcVal = tuple(x.strip() for x in opciones_validas.split(',')) #tuple(opciones_validas.split(','))
                    #input(Mem_OpcVal)
                    if Mem_val not in Mem_OpcVal:
                        print(f"{Fore.RED}ERROR: Valor '{Mem_val}' no permitido. Opciones válidas: {opciones_validas}")
                        msvcrt.getch()
                        break

            if error_nn: continue
            if input(f"{Fore.CYAN}¿Grabar cambios? (S/N): ").upper() == 'S': return datos_temp

        elif opc == 'S':
            if input(f"{Fore.RED}¿Salir sin grabar? (S/N): ").upper() == 'S': return None

        elif opc.zfill(2) in mapeo_opciones:
            f, t = mapeo_opciones[opc.zfill(2)]
            Pre_valor=datos_temp[f[0]]
            Pre_LonTot=t[1]
            es_obligatorio = (f[3] == "N")
            opciones_validas = f[4]

            asterisco = f"{Fore.RED}OBLIGATORIO" if es_obligatorio else " "

            guiones = "_" * max(0, Pre_LonTot - len(str(Pre_valor)))
            print(f"\n  {Fore.YELLOW}Modificar {f[1]} {f[4]} {asterisco}")
#            print(f"\n  {Fore.YELLOW}Modificar {f[1]} {f[4] if f[4] else ''} {asterisco}")
            print(f"   {Fore.WHITE}{Pre_valor}{Fore.LIGHTBLACK_EX}{guiones}")

            nuevo_val = input(f"{Fore.WHITE} > ").strip()


            # 1. Verificación de OBLIGATORIO
            if es_obligatorio and not nuevo_val:
                print(f"{Fore.RED}ERROR: Este campo es obligatorio.")
                msvcrt.getch()
                continue

            # 2. Verificación de LONGITUD
            if len(nuevo_val) > Pre_LonTot:
                print(f"{Fore.RED}ERROR: Longitud máxima superada ({Pre_LonTot}).")
                msvcrt.getch()
                continue

            # 3. Verificación de OPCIÓN
            if opciones_validas:
                # Convertimos la cadena plana en tupla, limpiando espacios accidentales
                Mem_OpcVal = tuple(x.strip() for x in opciones_validas.split(',')) #tuple(opciones_validas.split(','))
                #input(Mem_OpcVal)
                if nuevo_val not in Mem_OpcVal:
                    print(f"{Fore.RED}ERROR: Valor '{nuevo_val}' no permitido. Opciones válidas: {opciones_validas}")
                    msvcrt.getch()
                    continue

            datos_temp[f[0]] = nuevo_val


# =============================================================================
# FUNCION PRINCIPAL
# =============================================================================
def Idd_TabMod_Txt(Fnc_Svr, Fnc_Tab,Fnc_Ord=None, Fnc_Brw=None,  Fnc_ClmMod=None):
    global usuario_actual, nLin, offset, fila_resaltada, MARGEN
    global Mem_Dbt_Svr, Mem_Tab_Nom, Mem_Tab_Brw, Mem_Tab_Ord, Mem_Tab_ClmMod, Mem_Tab_ClmMod_Def, order_by_col, Mem_Ftr

    #Obtenemos el "frame" anterior (quien llamó a esta función)
    Err_CalFra = inspect.stack()[1]
    # Extraemos la información
    Err_Ach = os.path.basename(Err_CalFra.filename) # Solo el nombre del .py
    Err_Lin = Err_CalFra.lineno
    Err_Fnc = Err_CalFra.function
    if Err_Fnc == '<module>':
        Err_Fnc = "Nivel Principal (Main)"

    if not Fnc_Svr:
        print(f"{Fore.RED}Idd_Tab_Dat(Fnc_Svr, Fnc_Tab) Fnc_Svr=Servidor es Obligatorio ({Err_Fnc} {Err_Ach} - {Err_Lin})")
        input(f"{Fore.GREEN}Cualquier tecla para salir...{Fore.RESET}")
        return None

    if not Fnc_Tab:
        print(f"{Fore.RED}Idd_Tab_Dat(Fnc_Svr, Fnc_Tab) Fnc_Tab=Tabla es Obligatoria ({Err_Fnc} {Err_Ach} - {Err_Lin})")
        input(f"{Fore.GREEN}Cualquier tecla para salir...{Fore.RESET}")
        return None

    Mem_Tab_Nom=Fnc_Tab

    if not Fnc_Ord:
        Fnc_Ord="Main"

    if not Fnc_Brw:
        Fnc_Brw="Main"

    if not Fnc_ClmMod:
        Fnc_ClmMod="Main"

    import getpass
    usuario_actual = getpass.getuser() # **************************************************************** Modificar cuando halla MultiUsuario
    nLin = 30
    offset = 0
    fila_resaltada = None
    MARGEN = 1
    Mem_Ftr = ""

    maximizar_consola()
    Mem_Dbt_Svr = Fnc_Svr
    Mem_Tab_Nom = Fnc_Tab

    from Yos.Idd_BdtSvr import Cnx, Sel, SelTot, Cie, YosCfg_Vfy
    Mem_Cnx_YosCfg = Cnx(Fnc_Svr)
    Mem_Cur_YosCfg = Mem_Cnx_YosCfg.cursor()

#    conn_cfg = sqlite3.connect(Fnc_Svr)
#    cur_cfg = conn_cfg.cursor()

    if isinstance(Fnc_Ord, list):
        Mem_Tab_Ord = Fnc_Ord
    else:
        # El Orden es UNICO por Tab
        Mem_Cur_YosCfg.execute("SELECT cTxt, cCmd FROM Ord WHERE cTab = ? ORDER BY cNum", (Mem_Tab_Nom,))
        Mem_Tab_Ord = [(r['cTxt'], r['cCmd']) for r in Mem_Cur_YosCfg.fetchall()]

    if isinstance(Fnc_Brw, list):
        Mem_Tab_Brw = Fnc_Brw
    else:
        # El Brwse
        Mem_Cur_YosCfg.execute("SELECT cCab, cLon, cClm FROM Brw WHERE cTab = ? AND cCod = ? ORDER BY cNum", (Mem_Tab_Nom, Fnc_Brw))
        Mem_Tab_Brw = [(r['cCab'], r['cLon'], r['cClm']) for r in Mem_Cur_YosCfg.fetchall()]

    if isinstance(Fnc_ClmMod, list):
        Mem_Tab_ClmMod = Fnc_ClmMod
    else:
        # Las Columnas a Modificar
        Mem_Cur_YosCfg.execute("SELECT cClm, cCab, cMod, cNul, cOpc FROM ClmMod WHERE cTab = ? AND cCod = ? ORDER BY cNum", (Mem_Tab_Nom, Fnc_ClmMod))
        Mem_Tab_ClmMod = [(r['cClm'], r['cCab'], r['cMod'], r['cNul'], r['cOpc']) for r in Mem_Cur_YosCfg.fetchall()]


    # Creo Mem_Tab_ClmMod_Def los datos de la Estructura de la Tabla en Sql
    Mem_Cur_YosCfg.execute(f"PRAGMA table_info({Mem_Tab_Nom})")
    estruc_sql = {r[1]: r for r in Mem_Cur_YosCfg.fetchall()}

    Mem_Tab_ClmMod_Def = []
    for col_local in Mem_Tab_ClmMod:
        nom_col = col_local[0]

        if nom_col in estruc_sql:
            info = estruc_sql[nom_col]
            tipo_raw = str(info[2]).upper() # info[2] es el tipo que viene del motor

            # 1. Extraer Longitud
            m = re.search(r'\((\d+)\)', tipo_raw)
            if m:
                lon = int(m.group(1))
            else:
                # Longitudes inteligentes por defecto si no hay (n)
                if tipo_yos == "C": lon = 255  # Para un TEXT o VARCHAR sin tamaño
                elif tipo_yos == "N": lon = 10   # Un INT estándar
                elif tipo_yos == "D": lon = 10   # AAAA-MM-DD
                elif tipo_yos == "M": lon = 15   # 999,999,999.99
                else: lon = 20

            # 2. Determinar Tipo de Dato Yos (Universal)
            # CARÁCTER: VARCHAR, TEXT, CHAR, NCHAR, CLOB, BPCHAR...
            if any(x in tipo_raw for x in ["CHAR", "TEXT", "CLOB", "STR"]):
                tipo_yos = "C"

            # NUMÉRICO (Enteros): INT, SERIAL, SMALLINT, BIGINT, TINYINT...
            elif any(x in tipo_raw for x in ["INT", "SERIAL", "BIT"]):
                tipo_yos = "N"

            # FECHAS: DATE, TIME, TIMESTAMP, INTERVAL, DATETIME...
            elif any(x in tipo_raw for x in ["DATE", "TIME"]):
                tipo_yos = "D"

            # MONEDA/DECIMAL: DECIMAL, NUMERIC, DOUBLE, FLOAT, REAL, MONEY...
            elif any(x in tipo_raw for x in ["DECIMAL", "NUMERIC", "DOUBLE", "FLOAT", "REAL", "MONEY"]):
                tipo_yos = "M"

            else:
                tipo_yos = "C"  # Por defecto siempre Carácter para no fallar

            Mem_Tab_ClmMod_Def.append((tipo_yos, lon))
        else:
            Mem_Tab_ClmMod_Def.append(("C", 20))

#    print("512")
#    print("Mem_Tab_Ord")
#    print(Mem_Tab_Ord)
#    print("Mem_Tab_Brw")
#    print(Mem_Tab_Brw)
#    print("512 Mem_Tab_ClmMod")
#    print(Mem_Tab_ClmMod)
#    print(Mem_Tab_ClmMod_Def)
#    input("Fin")

    if Mem_Tab_Brw[0][0] != "ID": Mem_Tab_Brw.insert(0, ("ID", "2", None))
    idx_ord = 0; order_by_col = Mem_Tab_Ord[idx_ord][1]; pad = " " * MARGEN

    while True:
        anchos = obtener_anchos_reales()
        os.system('cls')
        ancho_linea = sum(anchos) + (len(anchos) * 3)
        Mem_Cur_YosCfg.execute(f"PRAGMA table_info({Mem_Tab_Nom})")
        db_col_names = [col[1] for col in Mem_Cur_YosCfg.fetchall()]

        where_ftr = f"WHERE {order_by_col} LIKE ?" if Mem_Ftr else ""
        params_filtro = (f"%{Mem_Ftr}%",) if Mem_Ftr else ()
        Mem_Cur_YosCfg.execute(f"SELECT COUNT(*) FROM {Mem_Tab_Nom} {where_ftr}", params_filtro)
        total_regs = Mem_Cur_YosCfg.fetchone()[0]
        Mem_Cur_YosCfg.execute(f"SELECT rowid, *, ({order_by_col}) as ord_val FROM {Mem_Tab_Nom} {where_ftr} ORDER BY {order_by_col} COLLATE NOCASE LIMIT {nLin} OFFSET {offset}", params_filtro)
        registros = Mem_Cur_YosCfg.fetchall()

        pag_actual = (offset // nLin) + 1
        total_paginas = (total_regs + nLin - 1) // nLin if total_regs > 0 else 1

        etiqueta_orden = next((o[0] for o in Mem_Tab_Ord if o[1] == order_by_col), order_by_col)
        Mem_Tit_Ftr=""
        if Mem_Ftr:
            Mem_Tit_Ftr=f"{Fore.CYAN}Filtro : {Fore.RED}{Mem_Ftr} "

        print(f"{Fore.CYAN}TABLA : {Fore.WHITE}{Mem_Tab_Nom}{Fore.CYAN} | Orden : {Fore.YELLOW}{etiqueta_orden} {Mem_Tit_Ftr}{Fore.CYAN}| Reg : {Fore.WHITE}{offset+1}/{total_regs}{Fore.CYAN} | Pag : {Fore.WHITE}{pag_actual}/{total_paginas}{Fore.CYAN} | Lineas Browse : {Fore.WHITE}{nLin}{Fore.CYAN}\n")

        def b(d, t): return f"{Fore.WHITE}{d} {Fore.YELLOW}({t}){Fore.RESET} "
        SEP = f"{Fore.BLUE}|{Fore.RESET} "
        print(f"{b(' Salir','S')}{SEP}{b('Primero','P')}{b('Retroceder','R')}{b('Avanzar','A')}{b('Ultimo','U')}{SEP}{b('Orden','Ord')}{b('Buscar','B')}{b('Filtro','Ftr')}{SEP}{b('Lineas Browse','Lb')}")
        print(f"           {SEP}{b('Crear','C')}{b('Ver','nn,V')}{b('Modificar','nn,M')}{b('Eliminar','nn,E')}")
        print()

        header = "".join([f"{Fore.WHITE}{pad}{c[0].ljust(anchos[i])}{pad}{Fore.BLUE}|" for i, c in enumerate(Mem_Tab_Brw)])
        print(header); print(Fore.BLUE + "═" * ancho_linea)
        for idx, r in enumerate(registros):
            n_pan = str(idx + 1).zfill(2)
            bg = Back.YELLOW if (fila_resaltada and str(r[-1]).upper() == str(fila_resaltada).upper()) else ""
            linea = f"{bg}{Fore.YELLOW if not bg else Fore.BLACK}{pad}{n_pan.ljust(anchos[0])}{pad}{Style.RESET_ALL}{Fore.BLUE}|"
            for i in range(1, len(Mem_Tab_Brw)):
                idx_bd = db_col_names.index(Mem_Tab_Brw[i][2]) + 1 if Mem_Tab_Brw[i][2] else 0
                txt_v = str(r[idx_bd] if idx_bd > 0 and r[idx_bd] is not None else "")[:anchos[i]].ljust(anchos[i])
                linea += f"{bg}{Fore.BLACK if bg else Fore.CYAN}{pad}{txt_v}{pad}{Style.RESET_ALL}{Fore.BLUE}|"
            print(linea)
#        for _ in range(nLin - len(registros)): print("x")
        print(Fore.BLUE + "═" * ancho_linea)

        cmd = input(f"{Fore.YELLOW} OPCION : {Fore.RESET}").strip().upper()

        if cmd == 'S': break
        if cmd == 'LB':
            nueva_lin = input(f"{Fore.WHITE} Lineas Browse > ").strip()
            if nueva_lin.isdigit():
                val_num = int(nueva_lin)
                if val_num > 0:
                    nLin = val_num
                    offset = 0
        elif cmd == 'P': offset = 0
        elif cmd == 'A': offset = min(offset + nLin, max(0, ((total_regs-1)//nLin)*nLin))
        elif cmd == 'R': offset = max(0, offset - nLin)
        elif cmd == 'U': offset = max(0, ((total_regs - 1) // nLin) * nLin)
        elif cmd == 'ORD':
            if Mem_Tab_Ord:
                print(f"\n   {Fore.CYAN}SELECCIONE ORDEN:")
                for i, o in enumerate(Mem_Tab_Ord):
                    print(f"   {Fore.GREEN}{i+1} {Fore.WHITE}{o[0]}")
                op_ord = input(f"   {Fore.YELLOW}Opción: {Fore.RESET}")
                if op_ord.isdigit() and 1 <= int(op_ord) <= len(Mem_Tab_Ord):
                    idx_ord = int(op_ord) - 1
                    order_by_col = Mem_Tab_Ord[idx_ord][1]
                    offset = 0
        elif cmd == 'B': busqueda_incremental_dinamica(conn, db_col_names, anchos)
        elif cmd == 'FTR':
            Mem_Ftr = input(f"{Fore.YELLOW} Filtro por {etiqueta_orden} : {Fore.WHITE}").strip()
            offset = 0
        elif cmd == 'C':
            reg_nuevo = formulario_yos(db_col_names)
            if reg_nuevo:
                insert_data = {k: v for k, v in reg_nuevo.items() if k != "nAutInc"}
                cols = ", ".join(insert_data.keys())
                pls = ", ".join(["?"] * len(insert_data))
#                print("598")
#                print(cols)
#                input(pls)
                # añado
#               cambios_finales['cModRegNik'] = usuario_actual
#               cambios_finales['cModRegTim'] = Yos_TimeStamp(Fnc_Nue="")

                Mem_Cur_YosCfg.execute(f"INSERT INTO {Mem_Tab_Nom} ({cols}) VALUES ({pls})", list(insert_data.values()))
                Mem_Cnx_YosCfg.commit()
        elif ',' in cmd:
            try:
                partes = cmd.split(','); idx_p = int(partes[0]) - 1; accion = partes[1].upper()
                if 0 <= idx_p < len(registros):
                    reg_sel = registros[idx_p]
                    if accion == 'V':
                        formulario_yos(db_col_names, reg_sel, solo_lectura=True)
                    elif accion == 'M':
                        cambios = formulario_yos(db_col_names, reg_sel)
                        if cambios:
                            # 1. Quitamos campos técnicos
                            cambios.pop("nAutInc", None)

                            # 2. FILTRADO CRÍTICO: Solo permitimos persistir si cMod == 'Mod'
                            # (Evita que campos 'Cre' se sobrescriban en un UPDATE)
                            cambios_finales = {}
                            for k, v in cambios.items():
                                # Buscamos el permiso cMod en la configuración Mem_Tab_ClmMod
                                permiso = next((c[2].strip() for c in Mem_Tab_ClmMod if c[0] == k), "")
                                if permiso == "Mod":
                                    cambios_finales[k] = v
                            # añado
                            cambios_finales['cModRegNik'] = usuario_actual
                            cambios_finales['cModRegTim'] = Yos_TimeStamp()

                            if cambios_finales:
                                set_sql = ", ".join([f"{k}=?" for k in cambios_finales.keys()])
                                valores = list(cambios_finales.values()) + [reg_sel[0]] # rowid al final

                                Mem_Cur_YosCfg.execute(f"UPDATE {Mem_Tab_Nom} SET {set_sql} WHERE rowid=?", valores)
                                Mem_Cnx_YosCfg.commit()
                    elif accion == 'E':
                        formulario_yos(db_col_names, reg_sel, solo_lectura=True, eliminar=True)
                        print(f" \n   {Back.RED}{Fore.WHITE}¿ELIMINAR ESTE REGISTRO? (S/N) {Style.RESET_ALL}")
                        if msvcrt.getch().upper() == b'S':
                            Mem_Cur_YosCfg.execute(f"DELETE FROM {Mem_Tab_Nom} WHERE rowid=?", (reg_sel[0],))
                            Mem_Cnx_YosCfg.commit()
            except Exception as e:
                print(f"Error: {e}"); msvcrt.getch()

    Mem_Cnx_YosCfg.close()

# =============================================================================
# INICIO DEL SISTEMA
# =============================================================================
if __name__ == "__main__":

    Mem_Dbt = "YosCfg"
    Mem_Tab = "Mnu"

    Idd_TabMod_Txt(Mem_Dbt, Mem_Tab)   # Lo MINIMO
