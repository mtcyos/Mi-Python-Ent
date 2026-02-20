# -*- coding: utf-8 -*-
import sqlite3
import os
import sys
import ctypes
import msvcrt
import locale
from datetime import datetime

# Configurar locale
try:
    locale.setlocale(locale.LC_TIME, "")
except:
    pass

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
except ImportError:
    os.system('pip install colorama')
    from colorama import init, Fore, Style, Back
    init(autoreset=True)

# =============================================================================
# CONFIGURACIÓN GLOBAL
# =============================================================================
usuario_actual = "mtcyos"
nLin = 30
offset = 0
fila_resaltada = None
MARGEN = 3

DB_NAME = "YosSis.Bdt"
TABLA = "Tab"
order_by_col = "cTab"

TABLA = "Tab"
order_by_col = "cTab"
Def_AbvBrw = [
    ("ID", "4", None),
    ("TABLA", "16", "cTab"),
    ("DESCRIPCION", "100%", "cDes"),
    ("USUARIO", "15", "cModRegNik"),
    ("MODIFICADO", "19", "cModRegTim")
]
"""
TABLA = "Abv"
order_by_col = "cAbv"
Def_AbvBrw = [
    ("ID", "4", None),
    ("ABREVIACION", "16", "cAbv"),
    ("DESCRIPCION", "100%", "cDes"),
    ("USUARIO", "15", "cModRegNik"),
    ("MODIFICADO", "19", "cModRegTim")
]
"""
# =============================================================================
# FUNCIONES DE APOYO
# =============================================================================
def obtener_indices_sqlite(conn):
    indices = []
    try:
        cur = conn.cursor()
        # Detectar Primary Key
        cur.execute(f"PRAGMA table_info({TABLA})")

        for col in cur.fetchall():
            if col[5] > 0: # Es PK
                indices.append(col[1])

        # Detectar Índices manuales
        cur.execute(f"PRAGMA index_list({TABLA})")
        for row in cur.fetchall():
            idx_name = row[1]
            cur.execute(f"PRAGMA index_info('{idx_name}')")
            for info in cur.fetchall():
                col_name = info[2]
                if col_name and col_name not in indices:
                    indices.append(col_name)
    except: pass
    return indices

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
        ancho_disponible = os.get_terminal_size().columns - 1
    except:
        ancho_disponible = 119
    espacio_fijo_por_columna = (MARGEN * 2) + 1
    total_fijo = 0
    idx_percent = -1
    for i, col in enumerate(Def_AbvBrw):
        if str(col[1]).endswith('%'): idx_percent = i
        else: total_fijo += int(col[1]) + espacio_fijo_por_columna
    anchos = []
    for i, col in enumerate(Def_AbvBrw):
        if i == idx_percent:
            espacio_para_percent = ancho_disponible - total_fijo - espacio_fijo_por_columna
            anchos.append(max(10, espacio_para_percent))
        else: anchos.append(int(col[1]))
    return anchos

def busqueda_incremental_dinamica(conn, db_col_names, anchos):
    global offset, fila_resaltada, nLin
    bus = ""
    pad = " " * MARGEN
    while True:
        os.system('cls')
        cur = conn.cursor()

        # 1. Encontrar la posición absoluta del registro que coincide con la búsqueda
        cur.execute(f"SELECT COUNT(*) FROM {TABLA} WHERE {order_by_col} < ? COLLATE NOCASE", (bus,))
        posicion_real = cur.fetchone()[0]

        # 2. CALCULO DINÁMICO DEL CENTRO:
        # Restamos la mitad de nLin a la posición real para que el registro quede al medio
        mitad = nLin // 2
        offset_temp = max(0, posicion_real - mitad)

        # 3. Obtener el valor real para resaltar el cursor
        #input((f"SELECT {order_by_col} FROM {TABLA} WHERE {order_by_col} >= ? COLLATE BINARY ORDER BY {order_by_col} COLLATE BINARY LIMIT 1", (bus,)))
        cur.execute(f"SELECT {order_by_col} FROM {TABLA} WHERE {order_by_col} >= ? COLLATE BINARY ORDER BY {order_by_col} COLLATE BINARY LIMIT 1", (bus,))
        res = cur.fetchone()
        fila_resaltada = res[0] if res else None

        print(f"{Back.GREEN}{Fore.BLACK}  Bucar : {bus.ljust(20)}  {Style.RESET_ALL}")
        print(f"{Fore.WHITE} [Letras]: Buscar | [Enter]: Aceptar | [Esc]: Cancelar\n")

        # 4. Listar registros usando el offset centrado dinámicamente
        cur.execute(f"SELECT rowid, * FROM {TABLA} ORDER BY {order_by_col} COLLATE NOCASE LIMIT {nLin} OFFSET {offset_temp}")
        regs = cur.fetchall()

        for idx, r in enumerate(regs):
            n_fila = str(idx + 1).zfill(2) # ID Físico (01, 02...)ç
            idx_orden_en_r = db_col_names.index(order_by_col) + 1
            es_esta_fila = (fila_resaltada is not None and str(r[idx_orden_en_r]) == str(fila_resaltada))
            bg = Back.YELLOW if es_esta_fila else ""
            fg = Fore.BLACK if es_esta_fila else Fore.CYAN
            linea = f"{bg}{Fore.YELLOW if not bg else Fore.BLACK}{pad}{n_fila.ljust(anchos[0])}{pad}{Style.RESET_ALL}{Fore.BLUE}|"
            for i in range(1, len(Def_AbvBrw)):
                nombre_campo = Def_AbvBrw[i][2]
                idx_bd = db_col_names.index(nombre_campo) + 1
                valor = str(r[idx_bd] if r[idx_bd] is not None else "")[:anchos[i]].ljust(anchos[i])
                linea += f"{bg}{fg}{pad}{valor}{pad}{Style.RESET_ALL}{Fore.BLUE}|"
            print(linea)

        for _ in range(nLin - len(regs)): print("")
        print(Fore.BLUE + "═" * (sum(anchos) + len(anchos) * (MARGEN * 2 + 1)))

        char = msvcrt.getch()
        if char == b'\r':
            offset = offset_temp # Al aceptar, mantenemos la vista tal cual la vemos
            break
        elif char == b'\x1b':
            fila_resaltada = None
            break
        elif char == b'\x08': bus = bus[:-1]
        else:
            try:
                if len(bus) < 20: bus += char.decode('utf-8')
            except: pass

def formulario_yos(db_col_names, registro=None, solo_lectura=False):
    global usuario_actual
    os.system('cls')
    nuevo_reg = {}
    titulo_p = " CONSULTAR " if solo_lectura else (" MODIFICAR " if registro else " NUEVO REGISTRO ")
    print(f"\n{Back.CYAN}{Fore.BLACK} {titulo_p} {Style.RESET_ALL}\n")

    # Usamos Def_AbvBrw que es la que existe globalmente
    for i in range(1, len(Def_AbvBrw)):
        rotulo = Def_AbvBrw[i][0]; nom_col = Def_AbvBrw[i][2]
        if not nom_col: continue

        val_actual = ""
        if registro:
            try:
                # Usamos el db_col_names que recibe la función
                idx_bd = db_col_names.index(nom_col) + 1
                val_actual = str(registro[idx_bd] if registro[idx_bd] is not None else "")
            except: val_actual = ""

        if solo_lectura:
            color_val = Fore.YELLOW if nom_col in ("cModRegNik", "cModRegTim") else Fore.WHITE
            print(f"{Fore.YELLOW}{rotulo.ljust(15)}: {color_val}{val_actual}")
        else:
            if nom_col == "cModRegNik":
                entrada = usuario_actual
                print(f"{Fore.YELLOW}{rotulo.ljust(15)}: {Fore.YELLOW}{entrada}")
            elif nom_col == "cModRegTim":
                entrada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{Fore.YELLOW}{rotulo.ljust(15)}: {Fore.YELLOW}{entrada}")
            else:
                if registro: print(f"{Fore.YELLOW}{rotulo} : {Fore.WHITE}{val_actual} {Style.RESET_ALL}")
                else: print(f"{Fore.YELLOW}{rotulo}")
                prompt = f"{Fore.GREEN} Nuevo Valor > {Fore.WHITE}"
                entrada = input(prompt).strip()
                if registro and not entrada: entrada = val_actual
            nuevo_reg[nom_col] = entrada

    if solo_lectura:
        print(f"\n{Fore.GREEN}Presione cualquier tecla para volver..."); msvcrt.getch(); return None
    print(f"\n{Fore.GREEN}¿Desea grabar los cambios? (S/N): ", end="")
    confirmar = msvcrt.getch().decode('utf-8').upper()
    return nuevo_reg if confirmar == 'S' else None

# =============================================================================
# MANTENIMIENTO PRINCIPAL
# =============================================================================
def yos_mantenimiento():
    global offset, order_by_col, fila_resaltada, nLin
    maximizar_consola()
    pad = " " * MARGEN

    while True:
        anchos = obtener_anchos_reales()
        os.system('cls')
        ancho_linea = sum(anchos) + (len(anchos) * (MARGEN * 2 + 1))

        conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({TABLA})")
        db_col_names = [col[1] for col in cur.fetchall()]
        Indices_Db = obtener_indices_sqlite(conn)

        cur.execute(f"SELECT COUNT(*) FROM {TABLA}"); total_regs = cur.fetchone()[0]
        cur.execute(f"SELECT rowid, * FROM {TABLA} ORDER BY {order_by_col} LIMIT {nLin} OFFSET {offset}")
        registros = cur.fetchall()

        rotulo_orden = next((c[0] for c in Def_AbvBrw if c[2] == order_by_col), order_by_col)
        pag_actual = (offset // nLin) + 1
        total_paginas = (total_regs + nLin - 1) // nLin if total_regs > 0 else 1

        print(f"{Fore.CYAN}TABLA : {Fore.WHITE}{TABLA}{Fore.CYAN} | Orden: {Fore.YELLOW}{rotulo_orden}{Fore.CYAN} | Reg: {Fore.WHITE}{offset+1}/{total_regs}{Fore.CYAN} | Pag: {Fore.WHITE}{pag_actual}/{total_paginas}{Fore.CYAN} | Linas Browse: {Fore.WHITE}{nLin}{Fore.CYAN}\n")

        header = ""
        for i, col in enumerate(Def_AbvBrw):
            tit, _, fld = col; anc = anchos[i]
            prefix = ""
            color = Fore.WHITE
            if fld in Indices_Db:
                color = Fore.WHITE
                if len(Indices_Db) > 1:
                    prefix = f"{str(Indices_Db.index(fld) + 1).zfill(2)} - "
            if fld == order_by_col: color = Fore.YELLOW
            header += f"{color}{pad}{(prefix + tit).ljust(anc)}{pad}{Fore.BLUE}|"

        print(header); print(Fore.BLUE + "═" * ancho_linea)

        for idx, r in enumerate(registros):
            # ID FÍSICO: Siempre 01 a nLin
            n_pan = str(idx + 1).zfill(2)
            idx_orden_en_r = db_col_names.index(order_by_col) + 1
            bg = Back.YELLOW if (fila_resaltada and str(r[idx_orden_en_r]).upper() == str(fila_resaltada).upper()) else ""
            fg = Fore.BLACK if bg else Fore.CYAN
            linea = f"{bg}{Fore.YELLOW if not bg else Fore.BLACK}{pad}{n_pan.ljust(anchos[0])}{pad}{Style.RESET_ALL}{Fore.BLUE}|"
            for i in range(1, len(Def_AbvBrw)):
                campo_nombre = Def_AbvBrw[i][2]
                idx_bd = db_col_names.index(campo_nombre) + 1
                txt_v = str(r[idx_bd] if r[idx_bd] is not None else "")[:anchos[i]].ljust(anchos[i])
                linea += f"{bg}{fg}{pad}{txt_v}{pad}{Style.RESET_ALL}{Fore.BLUE}|"
            print(linea)

        for _ in range(nLin - len(registros)): print("")
        print(Fore.BLUE + "═" * ancho_linea)

        def b(desc, tecla): return f"{Fore.WHITE}{desc} {Fore.YELLOW}({tecla}){Fore.RESET}  "
        SEP = f"{Fore.BLUE}|{Fore.RESET} "
        print(f"{b(' Salir','S')}{SEP}{b('Crear','C')}{b('Ver','nn,V')}{b('Modificar','nn,M')}{b('Eliminar','nn,E')}{SEP}{b('Buscar','B')}")
        print(f"{' '*12}{SEP}{b('Primero','P')}{b('Avanzar','A')}{b('Retroceder','R')}{b('Ultimo','U')}{SEP}{b('ID','Id')}")

        cmd = input(f"\n{Fore.YELLOW} OPCION : {Fore.RESET}").strip().upper()

        if cmd.isdigit() and len(cmd) <= 2:
            idx_num = int(cmd)
            if 1 <= idx_num <= len(Indices_Db):
                order_by_col = Indices_Db[idx_num - 1]; offset = 0; continue

        if cmd == 'ID':
            nueva_lin = input(f"{Fore.WHITE} Nuevo valor > ").strip()
            if nueva_lin.isdigit(): nLin = int(nueva_lin); offset = 0
        elif cmd == 'S': break
        elif cmd == 'B': busqueda_incremental_dinamica(conn, db_col_names, anchos)
        elif cmd == 'P': offset = 0
        elif cmd == 'A': offset = min(offset + nLin, max(0, ((total_regs-1)//nLin)*nLin))
        elif cmd == 'R': offset = max(0, offset - nLin)
        elif cmd == 'U': offset = max(0, ((total_regs - 1) // nLin) * nLin)
        elif cmd == 'C':
            reg_nuevo = formulario_yos(db_col_names)
            if reg_nuevo:
                cols = ", ".join(reg_nuevo.keys()); pls = ", ".join(["?"] * len(reg_nuevo))
                cur.execute(f"INSERT INTO {TABLA} ({cols}) VALUES ({pls})", list(reg_nuevo.values())); conn.commit()
        elif ',' in cmd:
            try:
                partes = cmd.split(','); idx_pantalla = int(partes[0]); accion = partes[1].upper()
                # Ajuste: Ahora idx_pantalla es directo (1 a 20 o 30)
                idx_lista = idx_pantalla - 1
                if 0 <= idx_lista < len(registros):
                    reg_sel = registros[idx_lista]
                    if accion == 'V': formulario_yos(db_col_names, reg_sel, solo_lectura=True)
                    elif accion == 'M':
                        cambios = formulario_yos(db_col_names, reg_sel)
                        if cambios:
                            set_sql = ", ".join([f"{k}=?" for k in cambios.keys()])
                            cur.execute(f"UPDATE {TABLA} SET {set_sql} WHERE rowid=?", list(cambios.values()) + [reg_sel[0]]); conn.commit()
                    elif accion == 'E':
                        if input(f"{Fore.RED}¿Eliminar? (S/N): ").upper() == 'S':
                            cur.execute(f"DELETE FROM {TABLA} WHERE rowid=?", (reg_sel[0],)); conn.commit()
            except: pass
        conn.close()

if __name__ == "__main__":
    yos_mantenimiento()
