# -*- coding: utf-8 -*-
"""
Idd_TabMod_Txt - Versión Textual (TUI Moderna)
Migrado desde Colorama a Textual Framework
"""
import inspect
import sqlite3
import os
import re
import sys
import subprocess
import tempfile
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import (
    DataTable, Input, Static, Header, Footer,
    Button, Label, Select, Checkbox, ListView, ListItem,
    TextArea
)
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.reactive import reactive
from textual.binding import Binding
from textual.coordinate import Coordinate

# =============================================================================
# CONFIGURACIÓN Y ESTADO GLOBAL (estilo procedural)
# =============================================================================
class AppState:
    """Estado global de la aplicación - evitamos POO en la lógica de negocio"""
    servidor: str = ""
    tabla_nombre: str = ""
    orden_actual: str = ""
    filtro: str = ""
    offset: int = 0
    limite_filas: int = 30
    fila_resaltada: Optional[str] = None
    usuario_actual: str = "YosCtr"

    # Metadatos de tablas
    columnas_browse: List[Tuple] = []      # Mem_Tab_Brw
    ordenes_disponibles: List[Tuple] = []  # Mem_Tab_Ord
    columnas_mod: List[Tuple] = []         # Mem_Tab_ClmMod
    definiciones_mod: List[Tuple] = []     # Mem_Tab_ClmMod_Def

    # Conexión
    conexion = None
    cursor = None

state = AppState()

# =============================================================================
# FUNCIONES DE UTILIDAD (procedural, sin clases)
# =============================================================================

def obtener_anchos_reales() -> List[int]:
    """Calcula anchos de columnas dinámicamente (igual que tu versión)"""
    try:
        ancho_terminal = os.get_terminal_size().columns - (len(state.columnas_browse) * 3)
    except:
        ancho_terminal = 118

    anchos_finales = [0] * len(state.columnas_browse)
    espacio_restante = ancho_terminal
    indices_porcentaje = []

    for i, col in enumerate(state.columnas_browse):
        ancho_config = str(col[1])
        if "%" not in ancho_config:
            valor_fijo = int(ancho_config)
            anchos_finales[i] = valor_fijo
            espacio_restante -= valor_fijo
        else:
            indices_porcentaje.append(i)

    if indices_porcentaje:
        total_slots = len(indices_porcentaje)
        for i, idx in enumerate(indices_porcentaje):
            if i == total_slots - 1:
                anchos_finales[idx] = max(0, espacio_restante)
            else:
                porcentaje_valor = int(str(state.columnas_browse[idx][1]).replace("%", ""))
                ancho_calculado = int((porcentaje_valor / 100) * espacio_restante)
                anchos_finales[idx] = ancho_calculado
                espacio_restante -= ancho_calculado

    return anchos_finales

def cargar_metadatos_tabla():
    """Carga metadatos desde la base de datos (procedural)"""
    # Cargar órdenes
    state.cursor.execute(
        "SELECT cTxt, cCmd FROM Ord WHERE cTab = ? ORDER BY cNum",
        (state.tabla_nombre,)
    )
    state.ordenes_disponibles = [(r['cTxt'], r['cCmd']) for r in state.cursor.fetchall()]
    # Cargar columnas de browse
    state.cursor.execute(
        "SELECT cCab, cLon, cClm FROM Brw WHERE cTab = ? AND cCod = ? ORDER BY cNum",
        (state.tabla_nombre, "Main")
    )
    state.columnas_browse = [(r['cCab'], r['cLon'], r['cClm']) for r in state.cursor.fetchall()]
    # Cargar columnas de modificación
    state.cursor.execute(
        "SELECT cClm, cCab, cMod, cNul, cOpc FROM ClmMod WHERE cTab = ? AND cCod = ? ORDER BY cNum",
        (state.tabla_nombre, "Main")
    )
    state.columnas_mod = [(r['cClm'], r['cCab'], r['cMod'], r['cNul'], r['cOpc']) for r in state.cursor.fetchall()]
    state.cursor.execute(f"PRAGMA table_info({state.tabla_nombre})")
    estructura_sql = {r[1]: r for r in state.cursor.fetchall()}
    state.definiciones_mod = []
    for col_local in state.columnas_mod:
        nom_col = col_local[0]
        if nom_col in estructura_sql:
            info = estructura_sql[nom_col]
            tipo_raw = str(info[2]).upper()

            # 1. PRIMERO: Determinar Tipo de Dato Yos (Universal)
            if any(x in tipo_raw for x in ["CHAR", "TEXT", "CLOB", "STR"]):
                tipo_yos = "C"
            elif any(x in tipo_raw for x in ["INT", "SERIAL", "BIT"]):
                tipo_yos = "N"
            elif any(x in tipo_raw for x in ["DATE", "TIME"]):
                tipo_yos = "D"
            elif any(x in tipo_raw for x in ["DECIMAL", "NUMERIC", "DOUBLE", "FLOAT", "REAL", "MONEY"]):
                tipo_yos = "M"
            else:
                tipo_yos = "C"

            # 2. DESPUÉS: Extraer Longitud
            m = re.search(r'\((\d+)\)', tipo_raw)
            if m:
                lon = int(m.group(1))
            else:
                if tipo_yos == "C": lon = 255
                elif tipo_yos == "N": lon = 10
                elif tipo_yos == "D": lon = 10
                elif tipo_yos == "M": lon = 15
                else: lon = 20

            state.definiciones_mod.append((tipo_yos, lon))
        else:
            state.definiciones_mod.append(("C", 20))
    # Agregar ID si no existe
    if state.columnas_browse and state.columnas_browse[0][0] != "ID":
        state.columnas_browse.insert(0, ("ID", "2", None))
    # Establecer orden por defecto
    if state.ordenes_disponibles:
        state.orden_actual = state.ordenes_disponibles[0][1]

def obtener_registros() -> Tuple[List[Tuple], int]:
    """Obtiene registros paginados de la base de datos"""
    where_ftr = f"WHERE {state.orden_actual} LIKE '%{state.filtro}%'" if state.filtro else ""
    # Contar total
    state.cursor.execute(f"SELECT COUNT(*) FROM {state.tabla_nombre} {where_ftr}")
    total = state.cursor.fetchone()[0]
    # Obtener registros
    query = f"""
        SELECT rowid, *, ({state.orden_actual}) as ord_val
        FROM {state.tabla_nombre}
        {where_ftr}
        ORDER BY {state.orden_actual} COLLATE NOCASE
        LIMIT {state.limite_filas}
        OFFSET {state.offset}
    """
    state.cursor.execute(query)
    registros = state.cursor.fetchall()

    return registros, total

def obtener_nombres_columnas_bd() -> List[str]:
    """Obtiene nombres de columnas de la tabla"""
    state.cursor.execute(f"PRAGMA table_info({state.tabla_nombre})")
    return [col[1] for col in state.cursor.fetchall()]

# =============================================================================
# SCREENS DE TEXTUAL (mínimas clases necesarias para la UI)
# =============================================================================
class BrowseScreen(Screen):
    """Pantalla principal de navegación de datos"""
    BINDINGS = [
        Binding("s", "quit", "Salir |"),
        Binding("p", "primero", "Primero"),
        Binding("a", "avanzar", "Avanzar"),
        Binding("r", "retroceder", "Retroceder"),
        Binding("u", "ultimo", "Último |"),
        Binding("o", "orden", "Orden"),
        Binding("b", "buscar", "Buscar"),
        Binding("f", "filtro", "Filtro | "),
        Binding("l", "lineas", "Líneas |"),
        Binding("c", "crear", "Crear"),
        Binding("v", "ver", "Ver"),
        Binding("m", "modificar", "Modificar"),
        Binding("e", "eliminar", "Eliminar"),
    ]

    def __init__(self):
        super().__init__()
        self.registros_actuales = []
        self.total_registros = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Barra de estado superior
        self.status_bar = Static("", id="status")
        yield self.status_bar

        # Tabla de datos
        self.data_table = DataTable(id="browse_table")
        self.data_table.cursor_type = "row"
        self.data_table.zebra_stripes = True
        yield self.data_table

        yield Footer()

    def on_mount(self):
        self.title = f"Tabla : {state.tabla_nombre}"
        self.subtitle = f"Servidor : {state.servidor}"
        self._configurar_columnas()
        self._cargar_datos()

    def _configurar_columnas(self):
        """Configura columnas del DataTable"""
        anchos = obtener_anchos_reales()
        self.data_table.clear(columns=True)

        for i, (cabecera, _, _) in enumerate(state.columnas_browse):
            ancho = anchos[i] if i < len(anchos) else 20
            self.data_table.add_column(cabecera, width=ancho, key=str(i))

    def _cargar_datos(self):
        """Carga datos en la tabla refrescando estructura"""
        self.registros_actuales, self.total_registros = obtener_registros()
        # 1. ¡CLAVE!: Borramos TODO, incluidas las columnas
        self.data_table.clear(columns=True)
        # 2. Reconfiguramos las columnas (esto lee el nuevo ancho/líneas)
        self._configurar_columnas()

        db_col_names = obtener_nombres_columnas_bd()
        for idx, reg in enumerate(self.registros_actuales):
            fila = []
            # Comprobar si este registro es el resaltado (por creación o búsqueda)
            # asumiendo que el valor del orden actual está en el offset correspondiente
            # O mejor, comparando el ord_val (última columna del query `obtener_registros`)
            ord_val_reg = str(reg[-1]) if reg[-1] is not None else ""
            es_resaltado = (state.fila_resaltada is not None) and (ord_val_reg.upper() == state.fila_resaltada.upper())

            for i, col_def in enumerate(state.columnas_browse):
                if i == 0:
                    # Calculamos el número de línea real según el offset
                    fila.append(str(idx + 1 + state.offset).zfill(2))
                else:
                    nombre_col = col_def[2]
                    if nombre_col and nombre_col in db_col_names:
                        idx_bd = db_col_names.index(nombre_col) + 1
                        valor = str(reg[idx_bd] if reg[idx_bd] is not None else "")
                    else:
                        valor = ""
                    fila.append(valor[:50])

            # Agregar row y mover el cursor a la fila resaltada si coincide
            self.data_table.add_row(*fila, key=str(idx))

            if es_resaltado:
                self.data_table.move_cursor(row=idx)
                state.fila_resaltada = None

        self._actualizar_status()

    def _actualizar_status(self):
        """Actualiza barra de estado"""
        pag_actual = (state.offset // state.limite_filas) + 1
        total_pag = max(1, (self.total_registros + state.limite_filas - 1) // state.limite_filas)

        etiqueta_orden = next(
            (o[0] for o in state.ordenes_disponibles if o[1] == state.orden_actual),
            state.orden_actual
        )
        filtro_txt = f" | Filtro : [red]{state.filtro}[/]" if state.filtro else ""
        self.status_bar.update(
            f"[cyan]Orden :[/] [yellow]{etiqueta_orden}[/]{filtro_txt} | "
            f"[cyan]Reg :[/] {state.offset + 1}/{self.total_registros} | "
            f"[cyan]Pag :[/] {pag_actual}/{total_pag} | "
            f"[cyan]Líneas :[/] {state.limite_filas}"
        )

    # --- Acciones ---
    def action_quit(self) -> None:
        """Esta función se ejecuta al presionar 'q' por el binding"""
        # 1. Cerramos la conexión a la BD antes de salir (Honor a quien honor merece)
        if state.conexion:
            state.conexion.close()

        # 2. Salimos de la aplicación Textual
        self.app.exit()

    def action_primero(self):
        state.offset = 0
        self._cargar_datos()

    def action_avanzar(self):
        if state.offset + state.limite_filas < self.total_registros:
            state.offset += state.limite_filas
            self._cargar_datos()

    def action_retroceder(self):
        state.offset = max(0, state.offset - state.limite_filas)
        self._cargar_datos()

    def action_ultimo(self):
        state.offset = max(0, ((self.total_registros - 1) // state.limite_filas) * state.limite_filas)
        self._cargar_datos()

    def action_orden(self):
        self.app.push_screen(OrdenScreen(), self.refrescar_todo)

    def action_buscar(self):
        self.app.push_screen(BuscarScreen(), self.refrescar_todo)

    def action_filtro(self):
        self.app.push_screen(FiltroScreen(), self.refrescar_todo)

    def action_lineas(self):
        self.app.push_screen(LineasScreen(), self.refrescar_todo)

    def refrescar_todo(self, resultado_nulo=None):
        if not resultado_nulo:
            state.offset = 0
        self._cargar_datos()
        # Bin > Forzamos a la tabla a tomar el control de nuevo
        self.data_table.focus()

    def action_crear(self):
        self.app.push_screen(FormularioScreen(modo="crear"), self.refrescar_todo)

    def action_ver(self):
        cursor_row = self.data_table.cursor_row
        if cursor_row is not None and cursor_row < len(self.registros_actuales):
            self.app.push_screen(FormularioScreen(
                modo="ver",
                registro=self.registros_actuales[cursor_row]
            ))

    def action_modificar(self):
        cursor_row = self.data_table.cursor_row
        if cursor_row is not None and cursor_row < len(self.registros_actuales):
            self.app.push_screen(FormularioScreen(
                modo="modificar",
                registro=self.registros_actuales[cursor_row]
            ), self.refrescar_todo)

    def action_eliminar(self):
        cursor_row = self.data_table.cursor_row
        if cursor_row is not None and cursor_row < len(self.registros_actuales):
            self.app.push_screen(FormularioScreen(
                modo="eliminar",
                registro=self.registros_actuales[cursor_row]
            ), self.refrescar_todo)

class OrdenScreen(Screen):
    """Pantalla de selección de orden"""

    def compose(self) -> ComposeResult:
        yield Static("[cyan]SELECCIONE ORDEN:[/]", classes="titulo")

        opciones = [(o[0], i) for i, o in enumerate(state.ordenes_disponibles)]
        self.select = Select(opciones, id="orden_select")
        yield self.select

        with Horizontal(classes="botones"):
            yield Button("Aceptar", variant="success", id="btn_ok")
            yield Button("Cancelar", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_ok":
            idx = self.select.value
            if idx is not None:
                state.orden_actual = state.ordenes_disponibles[idx][1]
                state.offset = 0
                self.dismiss(True)
            else:
                self.dismiss(False)
        else:
            self.dismiss(False)

class BuscarScreen(Screen):
    """Búsqueda incremental"""

    def compose(self) -> ComposeResult:
        yield Static(f"[green]Buscar en {state.orden_actual}:[/]", classes="titulo")
        self.input = Input(placeholder="Escriba para buscar...", id="buscar_input")
        yield self.input

        self.preview = DataTable(id="preview_table")
        yield self.preview

        with Horizontal(classes="botones"):
            yield Button("Aceptar (Enter)", variant="success", id="btn_ok")
            yield Button("Cancelar (Esc)", variant="error", id="btn_cancel")

    def on_mount(self):
        self.preview.cursor_type = "row"
        self.preview.zebra_stripes = True
        # Configurar columnas preview
        for col in state.columnas_browse[:3]:  # Primeras 3 columnas
            self.preview.add_column(col[0])
        self._actualizar_preview()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._actualizar_preview()

    def _actualizar_preview(self):
        busqueda = self.input.value
        where_ftr = f"WHERE {state.filtro}" if state.filtro else ""
        op_and = "AND" if where_ftr else "WHERE"

        # Buscar posición
        state.cursor.execute(
            f"SELECT COUNT(*) FROM {state.tabla_nombre} {where_ftr} {op_and} {state.orden_actual} < ? COLLATE NOCASE",
            (busqueda,)
        )
        posicion = state.cursor.fetchone()[0]

        # Obtener ventana alrededor
        mitad = state.limite_filas // 2
        offset_temp = max(0, posicion - mitad)

        state.cursor.execute(
            f"SELECT rowid, *, ({state.orden_actual}) as ord_val FROM {state.tabla_nombre} "
            f"{where_ftr} {op_and} {state.orden_actual} >= ? COLLATE NOCASE "
            f"ORDER BY {state.orden_actual} COLLATE NOCASE LIMIT {state.limite_filas} OFFSET {offset_temp}",
            (busqueda,)
        )
        regs = state.cursor.fetchall()

        self.preview.clear()
        db_col_names = obtener_nombres_columnas_bd()

        for r in regs:
            fila = []
            es_resaltado = str(r[-1]).upper() == busqueda.upper()

            for i, col_def in enumerate(state.columnas_browse[:3]):
                if i == 0:
                    fila.append(str(r[0]))  # rowid
                else:
                    nombre_col = col_def[2]
                    if nombre_col and nombre_col in db_col_names:
                        idx_bd = db_col_names.index(nombre_col) + 1
                        val = str(r[idx_bd] if r[idx_bd] is not None else "")
                    else:
                        val = ""
                    fila.append(val)

            style = "on yellow" if es_resaltado else ""
            self.preview.add_row(*fila)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_ok":
            busqueda = self.input.value

            # CÁLCULO DE POSICIÓN (corregido)
            where_ftr = f"WHERE {state.filtro}" if state.filtro else ""
            op_and = "AND" if where_ftr else "WHERE"

            state.cursor.execute(
                f"SELECT COUNT(*) FROM {state.tabla_nombre} {where_ftr} {op_and} {state.orden_actual} < ? COLLATE NOCASE",
                (busqueda,)
            )
            posicion = state.cursor.fetchone()[0]

            state.offset = max(0, posicion - (state.limite_filas // 2))
            state.fila_resaltada = busqueda
            self.dismiss(True)
        else:
            self.dismiss(False)

class FiltroScreen(Screen):
    """Pantalla de filtro"""

    def compose(self) -> ComposeResult:
        etiqueta = next(
            (o[0] for o in state.ordenes_disponibles if o[1] == state.orden_actual),
            state.orden_actual
        )
        yield Static(f"[cyan]Filtro por {etiqueta}:[/]", classes="titulo")

        self.input = Input(value=state.filtro, placeholder="Texto a filtrar...", id="filtro_input")
        yield self.input

        with Horizontal(classes="botones"):
            yield Button("Aplicar", variant="success", id="btn_ok")
            yield Button("Limpiar", variant="warning", id="btn_clear")
            yield Button("Cancelar", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_ok":
            state.filtro = self.input.value
            state.offset = 0
            self.dismiss(True)
        elif event.button.id == "btn_clear":
            state.filtro = ""
            state.offset = 0
            self.dismiss(True)
        else:
            self.dismiss(False)

class LineasScreen(Screen):
    """Configuración de líneas por página"""

    def compose(self) -> ComposeResult:
        yield Static("[cyan]Líneas por página:[/]", classes="titulo")
        self.input = Input(value=str(state.limite_filas), id="lineas_input")
        yield self.input

        with Horizontal(classes="botones"):
            yield Button("Aceptar", variant="success", id="btn_ok")
            yield Button("Cancelar", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_ok":
            try:
                val = int(self.input.value)
                if val > 0:
                    state.limite_filas = val
                    state.offset = 0
                    self.dismiss(True)
                    return
            except ValueError:
                pass

        # Si llega aquí es porque canceló o hubo error
        self.dismiss(False)

class ConfirmScreen(Screen):
    """Screen modal simple de confirmación"""

    def __init__(self, mensaje: str, callback=None):
        super().__init__()
        self.mensaje = mensaje
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(classes="dialog"):
            yield Static(self.mensaje, classes="mensaje")
            with Horizontal(classes="botones"):
                yield Button("✅ Sí", variant="success", id="btn_si")
                yield Button("❌ No", variant="error", id="btn_no")

    def on_button_pressed(self, event: Button.Pressed):
        resultado = event.button.id == "btn_si"
        if self.callback:
            self.callback(resultado)
        self.app.pop_screen()

class EmlEnvTextualScreen(Screen):
    """
    Screen que reimplementa EmlEnv usando widgets nativos de Textual.
    Como EmlEnv tiene interacciones (inputs), la replicamos aquí en lugar
    de intentar ejecutarla en modo consola.
    """
    BINDINGS = [
        Binding("escape", "cancelar", "Cancelar"),
        Binding("f2", "enviar", "Enviar"),
    ]

    def __init__(self, asunto_id: str, bloque_md: str):
        super().__init__()
        self.asunto_id = asunto_id
        self.bloque_md = bloque_md
        self.datos_email = {
            'destinatario': '',
            'su_nombre': '',
            'su_email': '',
            'asunto': f"Ficha: {asunto_id}",
            'mensaje': bloque_md,
            'agregar_info': False,
            'info_adicional': ''
        }

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(f"[green]📧 Enviar Email - Ficha: {self.asunto_id}[/]", classes="titulo")

        with Vertical(classes="form_container"):
            # Destinatario
            with Horizontal(classes="campo_row"):
                yield Static("[red]*[/] [yellow]DESTINATARIO:[/]", classes="etiqueta")
                yield Input(
                    value=self.datos_email['destinatario'],
                    placeholder="email@ejemplo.com, email2@ejemplo.com",
                    id="input_destinatario"
                )

            # Su nombre
            with Horizontal(classes="campo_row"):
                yield Static("[yellow]NOMBRE:[/]", classes="etiqueta")
                yield Input(
                    value=self.datos_email['su_nombre'],
                    placeholder="Su nombre",
                    id="input_su_nombre"
                )

            # Su email
            with Horizontal(classes="campo_row"):
                yield Static("[yellow]EMAIL:[/]", classes="etiqueta")
                yield Input(
                    value=self.datos_email['su_email'],
                    placeholder="su@email.com",
                    id="input_su_email"
                )

            # Asunto
            with Horizontal(classes="campo_row"):
                yield Static("[red]*[/] [yellow]ASUNTO:[/]", classes="etiqueta")
                yield Input(
                    value=self.datos_email['asunto'],
                    placeholder="Asunto del email",
                    id="input_asunto"
                )

            # Info adicional - SIEMPRE VISIBLE (sin checkbox)
            with Horizontal(classes="campo_row"):
                yield Static("  [yellow]INFO ADICIONAL:[/]", classes="etiqueta")
                yield Input(
                    value=self.datos_email['info_adicional'],
                    placeholder="Información adicional a incluir",
                    id="input_info_adicional"
                )

            yield Static("[yellow]MENSAJE (pre-cargado desde el registro):[/]")

            # Mensaje (TextArea para mejor edición)
            yield TextArea(
                text=self.datos_email['mensaje'],
                id="text_mensaje",
                show_line_numbers=True,
                language="markdown"
            )

        yield Static(" ")

        # Botones
        with Horizontal(classes="botones"):
            yield Button("ENVIAR (F2)", variant="success", id="btn_enviar")
            yield Button("CANCELAR (Esc)", variant="error", id="btn_cancelar")

        yield Footer()

    def action_enviar(self):
        """Enviar el email"""
        self._enviar_email()

    def action_cancelar(self):
        """Cancelar y volver"""
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn_enviar":
            self._enviar_email()
        else:
            self.dismiss(False)

    def _enviar_email(self):
        """Valida y envía el email"""
        # Recoger datos
        destinatario = self.query_one("#input_destinatario", Input).value.strip()
        su_nombre = self.query_one("#input_su_nombre", Input).value.strip()
        su_email = self.query_one("#input_su_email", Input).value.strip()
        asunto = self.query_one("#input_asunto", Input).value.strip()
        mensaje = self.query_one("#text_mensaje", TextArea).text
        # ELIMINADO: agregar_info = self.query_one("#chk_agregar_info", Checkbox).value
        info_adicional = self.query_one("#input_info_adicional", Input).value.strip()

        # Validaciones
        if not destinatario:
            self.app.notify("❌ EMAIL DESTINATARIO es obligatorio", severity="error")
            self.query_one("#input_destinatario", Input).focus()
            return

        if not asunto:
            self.app.notify("❌ ASUNTO es obligatorio", severity="error")
            self.query_one("#input_asunto", Input).focus()
            return

        if not mensaje.strip():
            self.app.notify("❌ MENSAJE es obligatorio", severity="error")
            self.query_one("#text_mensaje", TextArea).focus()
            return

        # Construir cuerpo final
        cuerpo_final = ""
        if su_nombre:
            cuerpo_final += f"{su_nombre}\n"
        if su_email:
            cuerpo_final += f"Correo Electrónico : {su_email}\n"
        if su_nombre or su_email:
            cuerpo_final += "*****************************************\n"

        # CAMBIO: Siempre incluir info adicional si tiene contenido
        if info_adicional:
            cuerpo_final += f"{info_adicional}\n\n"

        cuerpo_final += mensaje

        # Mostrar pantalla de confirmación previa
        self.app.push_screen(ConfirmarEnvioScreen(
            destinatario=destinatario,
            asunto=asunto,
            cuerpo=cuerpo_final,
            su_nombre=su_nombre,
            su_email=su_email
        ), self._procesar_resultado_envio)

    def _procesar_resultado_envio(self, resultado: bool):
        """Callback después de la pantalla de confirmación"""
        if resultado:
            self.dismiss(True)
        # Si canceló, volvemos a la pantalla de edición

class ConfirmarEnvioScreen(Screen):
    """Pantalla de confirmación previa al envío (como en EmlEnv original)"""

    def __init__(self, destinatario: str, asunto: str, cuerpo: str, su_nombre: str = "", su_email: str = ""):
        super().__init__()
        self.destinatario = destinatario
        self.asunto = asunto
        self.cuerpo = cuerpo
        self.su_nombre = su_nombre
        self.su_email = su_email

    def compose(self) -> ComposeResult:
#        yield Static("[yellow]******************************[/]", classes="titulo")
        yield Static("[yellow]******************************[/]")
        yield Static("[yellow]*     VERIFIQUE EL EMAIL     *[/]")
        yield Static("[yellow]******************************[/]")

        yield Static(" ")
        yield Static(f"[cyan]DESTINATARIO:[/] [white]{self.destinatario}[/]")
        yield Static(" ")

        if self.su_nombre:
            yield Static(f"[cyan]SU NOMBRE:[/] [white]{self.su_nombre}[/]")
        if self.su_email:
            yield Static(f"[cyan]SU EMAIL:[/] [white]{self.su_email}[/]")
        if self.su_nombre or self.su_email:
            yield Static(" ")

        yield Static(f"[cyan]ASUNTO:[/] [white]{self.asunto}[/]")
        yield Static(" ")
        yield Static("[cyan]MENSAJE:[/]")

        # Mostrar mensaje con scroll si es largo
        mensaje_preview = self.cuerpo[:500] + "..." if len(self.cuerpo) > 500 else self.cuerpo
        yield Static(f"[dim]{mensaje_preview}[/]", classes="mensaje_preview")

        yield Static(" ")

        with Horizontal(classes="botones"):
            yield Button("ENVIAR", variant="success", id="btn_enviar")
            yield Button("VOLVER", variant="error", id="btn_cancelar")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn_enviar":
            # Aquí llamarías a la función real de envío
            self._ejecutar_envio()
        else:
            self.dismiss(False)

    def _ejecutar_envio(self):
        """Ejecuta el envío real del email"""
        try:
            # Intentar importar y usar la función de envío de Yos
            import smtplib
            from email.message import EmailMessage

            if not YosCfg.get("Eml_Svr", "").strip():
                self.app.notify("Servidor de correo no configurado en YosCfg", severity="error")
                self.dismiss(False)
                return

            # Normalizar destinatarios
            if isinstance(self.destinatario, str):
                lista_dest = [d.strip() for d in self.destinatario.split(",") if d.strip()]
            else:
                lista_dest = self.destinatario

            # Construir mensaje
            msg = EmailMessage()
            msg['Subject'] = self.asunto
            msg['From'] = f'{YosCfg["Eml_EmlEnv"]} <{YosCfg["Eml_EmlEnv"]}>'
            msg['To'] = ", ".join(lista_dest)

            # Añadir cabecera y pie configurados
            cuerpo_final = YosCfg.get("Eml_MsgCab", "").replace("\\n", "\n") + self.cuerpo + YosCfg.get("Eml_MsgPie", "").replace("\\n", "\n")
            msg.set_content(cuerpo_final)

            # Enviar
            with smtplib.SMTP(YosCfg["Eml_Svr"], YosCfg.get("Eml_Puo", 587)) as server:
                server.starttls()
                server.login(YosCfg["Eml_Usr"], YosCfg["Eml_Pas"])
                server.send_message(msg)

            self.app.notify(f"Email enviado a {len(lista_dest)} destinatario(s)", severity="information")
            self.dismiss(True)

        except Exception as e:
            self.app.notify(f"Error al enviar: {str(e)}", severity="error")
            self.dismiss(False)

class FormularioScreen(Screen):
    """Formulario de edición/creación/consulta/eliminación"""
    BINDINGS = [
        Binding("escape", "dismiss", "Volver"),
        Binding("c", "copy_clipboard", "Clipboard |"),
        Binding("e", "send_email", "Email |"),
    ]

    def action_copy_clipboard(self) -> None:
        try:
            import pyperclip
            if self.datos_temp:
                lineas = []
                for col in state.columnas_mod:
                    nombre_tecnico = col[0]
                    titular = col[1]
                    valor = self.datos_temp.get(nombre_tecnico, "")
                    valor = valor if valor is not None else ""
                    lineas.append(f"{str(titular)} : {valor}")

                txt_ficha = "\n".join(lineas)
                pyperclip.copy(txt_ficha)
                self.app.notify("Registro al Clipboard", title="Clipboard")
        except ImportError:
            self.app.notify("pyperclip no instalado. Use: pip install pyperclip", severity="warning")

    def action_send_email(self) -> None:
        """Abre el screen de email nativo de Textual (reemplaza EmlEnv modo consola)"""
        if not self.datos_temp:
            return

        # Preparar datos del registro
        lineas = [f"{col[1]} : {self.datos_temp.get(col[0], '')}" for col in state.columnas_mod]
        bloque_md = "\n".join(lineas)
        asunto_id = self.datos_temp.get('cNom') or self.datos_temp.get('cTxt') or 'Registro'

        # Abrir screen de email nativo (no modo consola)
        self.app.push_screen(EmlEnvTextualScreen(asunto_id, bloque_md))

    def __init__(self, modo: str = "crear", registro: Optional[Tuple] = None):
        super().__init__()
        self.modo = modo
        self.registro = registro
        self.datos_temp = {}
        self.inputs = {}

    def compose(self) -> ComposeResult:
        # Título según modo
        titulos = {
            "crear": "[green]NUEVO REGISTRO[/]",
            "modificar": "[yellow]MODIFICAR REGISTRO[/]",
            "ver": "[blue]CONSULTAR REGISTRO[/]",
            "eliminar": "[red]ELIMINAR REGISTRO[/]"
        }
        yield Static(titulos.get(self.modo, ""), classes="titulo")

        # Campos del formulario
        db_col_names = obtener_nombres_columnas_bd()

        for i, (col_def, tipo_def) in enumerate(zip(state.columnas_mod, state.definiciones_mod)):
            nombre_col = col_def[0]

            # Saltamos los campos de auditoría para ponerlos fijos al final
            if nombre_col in ["cModRegNik", "cModRegTim"]:
                continue

            etiqueta = col_def[1]
            permiso = str(col_def[2]).strip()
            if self.modo == "crear":
                es_modificable = permiso in ["Cre", "Mod"]
            elif self.modo == "modificar":
                es_modificable = permiso == "Mod"
            else:
                es_modificable = False

            val_nul = str(col_def[3]).strip().upper() if len(col_def) > 3 else ""
            es_obligatorio = (val_nul == "N")

            opciones_validas = col_def[4] if len(col_def) > 4 else None

            # Valor inicial
            if self.registro and nombre_col in db_col_names:
                idx_bd = db_col_names.index(nombre_col) + 1
                valor_inicial = str(self.registro[idx_bd] if self.registro[idx_bd] is not None else "")
            else:
                valor_inicial = ""

            self.datos_temp[nombre_col] = valor_inicial

            # Crear campo
            with Horizontal(classes="campo_row"):
                asterisco = "[red]*[/]" if es_obligatorio else " "
                yield Static(f"{asterisco} [yellow]{etiqueta}:[/]", classes="etiqueta")

                if es_modificable:
                    if opciones_validas:
                        # Select para opciones predefinidas
                        opciones_limpias = [opt.strip() for opt in opciones_validas.split(",")]
                        opts = [(opt, opt) for opt in opciones_limpias]

                        val_ini = valor_inicial if valor_inicial in opciones_limpias else (opciones_limpias[0] if opciones_limpias else None)

                        sel = Select(opts, value=val_ini, id=f"field_{nombre_col}")
                        self.inputs[nombre_col] = sel
                        yield sel
                    else:
                        # Input normal
                        inp = Input(
                            value=valor_inicial,
                            placeholder=f"Máx {tipo_def[1]} chars",
                            id=f"field_{nombre_col}",
                            disabled=not es_modificable
                        )
                        self.inputs[nombre_col] = inp
                        yield inp
                else:
                    yield Static(f"[white]{valor_inicial}[/]", classes="valor")

        # Renderizar campos de auditoría al final (solo vista)
        usuario_val = ""
        modificado_val = ""

        if self.registro and "cModRegNik" in db_col_names:
            idx = db_col_names.index("cModRegNik") + 1
            usuario_val = str(self.registro[idx] if self.registro[idx] is not None else "")
        if self.registro and "cModRegTim" in db_col_names:
            idx = db_col_names.index("cModRegTim") + 1
            modificado_val = str(self.registro[idx] if self.registro[idx] is not None else "")

        if self.modo == "crear":
            usuario_val = state.usuario_actual
            modificado_val = datetime.now().strftime("%Y-%m-%d %H:%M:%S*")

        yield Static(" ")

        with Horizontal(classes="campo_row"):
            yield Static("  [yellow]USUARIO:[/]", classes="etiqueta")
            yield Static(f"[white]{usuario_val}[/]", classes="valor")

        with Horizontal(classes="campo_row"):
            yield Static("  [yellow]MODIFICADO:[/]", classes="etiqueta")
            yield Static(f"[white]{modificado_val}[/]", classes="valor")

        yield Static(" ")

        # Botones
        with Horizontal(classes="botones"):
            if self.modo == "crear":
                yield Button("CREAR", variant="success", id="btn_save")
                yield Button("CANCELAR", variant="error", id="btn_cancel")
            elif self.modo == "modificar":
                yield Button("MODIFICAR", variant="success", id="btn_save")
                yield Button("CANCELAR", variant="error", id="btn_cancel")
            elif self.modo == "eliminar":
                yield Button("ELIMINAR", variant="error", id="btn_delete")
                yield Button("CANCELAR", variant="primary", id="btn_cancel")
            else:  # ver
                yield Button("CERRAR", variant="primary", id="btn_cancel")
                yield Button("CLIPBOARD (C)", variant="primary", id="btn_copy")
                yield Button("EMAIL (E)", variant="primary", id="btn_email")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_cancel":
            self.dismiss(False)
            return

        if event.button.id == "btn_copy":
            self.action_copy_clipboard()
            return

        if event.button.id == "btn_email":
            self.action_send_email()
            return

        if event.button.id == "btn_delete":
            # Eliminar registro
            if self.registro:
                rowid = self.registro[0]
                state.cursor.execute(f"DELETE FROM {state.tabla_nombre} WHERE rowid=?", (rowid,))
                state.conexion.commit()
            self.dismiss(True)
            return

        if event.button.id == "btn_save":
            # Validar y guardar
            if self._validar_datos():
                self._guardar_datos()

    def _validar_datos(self) -> bool:
        """Valida los datos del formulario"""
        for col_def, tipo_def in zip(state.columnas_mod, state.definiciones_mod):
            nombre_col = col_def[0]
            etiqueta = col_def[1]
            permiso = str(col_def[2]).strip()
            if self.modo == "crear":
                es_modificable = permiso in ["Cre", "Mod"]
            elif self.modo == "modificar":
                es_modificable = permiso == "Mod"
            else:
                es_modificable = False

            val_nul = str(col_def[3]).strip().upper() if len(col_def) > 3 else ""
            es_obligatorio = (val_nul == "N")

            tipo_yos = tipo_def[0]
            max_lon = tipo_def[1]

            if not es_modificable:
                if nombre_col not in ["cModRegNik", "cModRegTim"]:
                    self.datos_temp[nombre_col] = self.datos_temp.get(nombre_col, "")
                continue

            control = self.inputs.get(nombre_col)
            if not control:
                continue

            valor = str(control.value).strip()

            if es_obligatorio and not valor:
                self.app.notify(f"El campo '{etiqueta}' es obligatorio.", severity="error")
                control.focus()
                return False

            if len(valor) > max_lon:
                self.app.notify(f"{etiqueta} supera longitud máxima ({max_lon})", severity="error")
                control.focus()
                return False

            opciones_validas = col_def[4] if len(col_def) > 4 else None
            if opciones_validas and valor:
                opts = [o.strip() for o in opciones_validas.split(",")]
                if valor not in opts:
                    self.app.notify(f"{etiqueta}: valor no permitido", severity="error")
                    return False

            self.datos_temp[nombre_col] = valor

        return True

    def _guardar_datos(self) -> bool:
        """Guarda los datos en la base de datos"""
        # Fallback para Yos_TimeStamp si no está disponible
        try:
            from Yos import Yos_TimeStamp
        except ImportError:
            def Yos_TimeStamp(Fnc_Nue=None):
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            db_col_names = obtener_nombres_columnas_bd()

            if self.modo == "crear":
                if "cModRegNik" in db_col_names:
                    self.datos_temp["cModRegNik"] = state.usuario_actual
                if "cModRegTim" in db_col_names:
                    self.datos_temp["cModRegTim"] = Yos_TimeStamp(Fnc_Nue="Cre")

            datos_guardar = {k: v for k, v in self.datos_temp.items() if k != "nAutInc"}

            if self.modo == "crear":
                cols = ", ".join(datos_guardar.keys())
                placeholders = ", ".join(["?"] * len(datos_guardar))
                query = f"INSERT INTO {state.tabla_nombre} ({cols}) VALUES ({placeholders})"
                state.cursor.execute(query, list(datos_guardar.values()))

                try:
                    campo_orden = state.orden_actual
                    if campo_orden in datos_guardar:
                        busqueda = datos_guardar[campo_orden]
                        state.fila_resaltada = str(busqueda)
                except:
                    pass

            elif self.modo == "modificar" and self.registro:
                datos_finales = {}
                for k, v in datos_guardar.items():
                    permiso = next((str(c[2]).strip() for c in state.columnas_mod if c[0] == k), "")
                    if permiso == "Mod":
                        datos_finales[k] = v

                if "cModRegNik" in db_col_names:
                    datos_finales["cModRegNik"] = state.usuario_actual
                if "cModRegTim" in db_col_names:
                    datos_finales["cModRegTim"] = Yos_TimeStamp()

                if datos_finales:
                    set_clause = ", ".join([f"{k}=?" for k in datos_finales.keys()])
                    query = f"UPDATE {state.tabla_nombre} SET {set_clause} WHERE rowid=?"
                    valores = list(datos_finales.values()) + [self.registro[0]]
                    state.cursor.execute(query, valores)
                else:
                    self.app.notify("Sin cambios permitidos", severity="warning")
                    return False

            state.conexion.commit()
            self.app.notify("Datos guardados con éxito", severity="information")
            self.dismiss(True)
            return True

        except Exception as e:
            self.app.notify(f"Error crítico: {str(e)}", severity="error")
            return False

# =============================================================================
# APLICACIÓN PRINCIPAL
# =============================================================================

class IddTabModApp(App):
    """Aplicación Textual principal"""

    CSS = """
/* Pantalla base plana */
Screen {
    align: center middle;
    background: $surface;
}

/* Títulos sin bordes raros */
.titulo {
    text-align: center;
    text-style: bold;
    margin: 1 0;
    color: $accent;
    background: $surface-darken-1;
}

/* Botones rectangulares simples (ASCII compatible) */
Button {
    margin: 0 1;
    border: none;
    background: $primary;
    color: white;
    height: 3;
    min-width: 20;
}

Button:hover {
    background: $primary-lighten-1;
}

/* Campos del formulario */
.campo_row {
    height: auto;
    margin: 0 1;
}

.etiqueta {
    width: 15;
    content-align: right middle;
    color: $secondary;
    text-style: bold;
}

.valor {
    width: 1fr;
    content-align: left middle;
    padding-left: 1;
}

/* Tabla de datos limpia */
#browse_table {
    height: 1fr;
    margin: 0;
    border: none;
}

/* Barra de estado inferior plana */
#status {
    text-align: center;
    background: $surface-darken-2;
    color: $text-muted;
    height: 2;
    content-align: center middle;
}

/* Inputs y Selects sólidos */
Input, Select {
    width: 1fr;
    border: solid $primary;
    background: $surface;
}

/* Ajuste para el Footer de Textual */
Footer {
    background: $surface-darken-2;
    color: $text-muted;
}

/* Ajustar todos los componentes de Select para evitar caracteres extraños en Windows */
Select > SelectCurrent {
    border: none;
    padding: 0 1;
}

SelectOverlay {
    border: solid $primary;
}

/* Estilos para ConfirmScreen modal */
ConfirmScreen {
    align: center middle;
}

ConfirmScreen > .dialog {
    width: 60;
    height: auto;
    border: thick $background 80%;
    background: $surface;
    padding: 1 2;
}

ConfirmScreen > .dialog > .mensaje {
    text-align: center;
    margin: 1 0;
}

ConfirmScreen > .dialog > .botones {
    align: center middle;
    height: auto;
}

/* Estilos para EmlEnvTextualScreen */
EmlEnvTextualScreen {
    align: center middle;
}

EmlEnvTextualScreen > .form_container {
    width: 70;
    height: auto;
    padding: 0 1;
}

EmlEnvTextualScreen > .form_container > .campo_row {
    height: auto;
    margin: 0 1;
}

EmlEnvTextualScreen #text_mensaje {
    height: 15;
    border: solid $primary;
}

/* Estilos para ConfirmarEnvioScreen */
ConfirmarEnvioScreen {
    align: center middle;
}

ConfirmarEnvioScreen > .mensaje_preview {
    width: 70;
    height: 10;
    border: solid $primary-darken-1;
    padding: 1;
    overflow: auto scroll;
}
"""

    def on_mount(self):
        self.push_screen(BrowseScreen())

# =============================================================================
# FUNCIÓN DE ENTRADA (procedural, igual que tu versión original)
# =============================================================================

def Idd_TabMod(Fnc_Svr: str, Fnc_Tab: str, Fnc_Ord=None, Fnc_Brw=None, Fnc_ClmMod=None):
    """
    Función principal de entrada - mantiene la misma firma que tu versión colorama
    para compatibilidad hacia atrás.
    """
    global state

    # Obtener información del llamador (igual que tu versión)
    Err_CalFra = inspect.stack()[1]
    Err_Ach = os.path.basename(Err_CalFra.filename)
    Err_Lin = Err_CalFra.lineno
    Err_Fnc = Err_CalFra.function if Err_CalFra.function != '<module>' else "Main"

    if not Fnc_Svr:
        print(f"ERROR: Fnc_Svr es obligatorio ({Err_Fnc} {Err_Ach} - {Err_Lin})")
        input("Cualquier tecla para salir...")
        return None

    if not Fnc_Tab:
        print(f"ERROR: Fnc_Tab es obligatoria ({Err_Fnc} {Err_Ach} - {Err_Lin})")
        input("Cualquier tecla para salir...")
        return None

    # Inicializar estado
    state.servidor = Fnc_Svr
    state.tabla_nombre = Fnc_Tab
    import getpass
    state.usuario_actual = getpass.getuser()
    state.offset = 0
    state.limite_filas = 30
    state.filtro = ""

    # Conexión a base de datos (adaptar según tu Yos.Idd_BdtSvr)
    try:
        from Yos.Idd_BdtSvr import Cnx
        state.conexion = Cnx(Fnc_Svr)
        state.cursor = state.conexion.cursor()
    except ImportError:
        # Fallback a sqlite3 directo para pruebas
        state.conexion = sqlite3.connect(Fnc_Svr)
        state.conexion.row_factory = sqlite3.Row
        state.cursor = state.conexion.cursor()

    # Cargar metadatos
    cargar_metadatos_tabla()

    # Manejar parámetros opcionales (como en tu versión)
    if isinstance(Fnc_Ord, list):
        state.ordenes_disponibles = Fnc_Ord

    if isinstance(Fnc_Brw, list):
        state.columnas_browse = Fnc_Brw
        if state.columnas_browse[0][0] != "ID":
            state.columnas_browse.insert(0, ("ID", "2", None))

    if isinstance(Fnc_ClmMod, list):
        state.columnas_mod = Fnc_ClmMod

    # Iniciar aplicación Textual
    app = IddTabModApp()
    app.run()

    # Cerrar conexión al salir
    if state.conexion:
        state.conexion.close()

# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    Mem_Dbt = "YosCfg"
    Mem_Tab = "Mnu"

    Idd_TabMod(Mem_Dbt, Mem_Tab)
