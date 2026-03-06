#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   Yos_Mnu.py
   Genero el Menu de la Aplicacion

   Copyright (c) 2026 Miguel Tortosa

   Licenciado bajo la Licencia MIT.

   Consulte el archivo LICENCIA en la raíz del proyecto para más información.
"""

import Yos
from Yos.Yos_Frm import FrmCls, FrmWit
from Yos.Yos_Ini import AplIni
from Yos.Yos_Acd import Acd
from Yos.Yos_Cfg import Apl_Fin

import os
from textual.app import App, ComposeResult
from textual.widgets import Button, Static
from textual.containers import Horizontal, Vertical, Container

CSS_MNU = """
/* Pantalla base plana */
Screen {
    align: center middle;
    background: $surface;
}

#rotulo-app {
    text-align: center;
    color: $accent;
    text-style: bold;
    padding: 0 1;
    margin-bottom: 0;
}

#marco {
    border: none;
    padding: 0 2;
    width: 100%;
    height: 100%;
    background: $surface;
}

#titulo-app {
    text-align: center;
    color: $warning;
    text-style: bold;
    padding: 0 1;
    background: transparent;
    height: 1;
    margin-top: 0;
}

#copyright {
    text-align: center;
    color: $warning;
    text-style: italic;
    background: transparent;
    height: 1;
    content-align: center middle;
}

#fila-cols {
    width: 100%;
    height: 1fr;
    margin: 0;
    padding: 0;
}

.col {
    padding: 0;
    margin: 0;
    width: 1fr;
    background: $surface;
}

.titulo-col {
    text-align: center;
    text-style: bold;
    color: #AF87FF;
    background: $surface-darken-1;
    padding: 0 1;
    margin: 0;
    width: 100%;
    height: 1;
}

Button {
    width: 100%;
    border: none;
    background: $primary;
    color: white;
    text-align: left;
    content-align: left middle;
    height: 1;
    margin: 0;
    padding: 0 1;
}

Button:hover {
    background: $primary-lighten-1;
    color: white;
}

Button:focus {
    background: $accent;
    color: black;
}
"""

def _agrupar_menu(fnc_mnu, ent_permitidas):
    columnas  = []
    col_actual = None
    for clave, valor in sorted(fnc_mnu.items(), key=lambda x: int(x[0])):
        ent  = valor.get("Ent", "")
        tipo = valor.get("Tip", "")
        if ent != "" and ent not in ent_permitidas:
            continue
        if tipo == "Cab":
            col_actual = {"titulo": valor["Txt"].upper(), "items": []}
            columnas.append(col_actual)
        elif tipo == "Opc" and col_actual is not None:
            col_actual["items"].append({
                "id":  clave,
                "txt": valor["Txt"],
                "fnc": valor["Fnc"]
            })
    return columnas

def _generar_rotulo():
    """Captura el ASCII art de pyfiglet para usarlo en Textual."""
    try:
        import pyfiglet
        import shutil
        ancho = shutil.get_terminal_size().columns
        rotulo = pyfiglet.figlet_format(
            YosCfg["Apl_Apl"],
            font=YosCfg["Apl_Etn_Let"]
        ).strip()
        # Centramos cada línea
        lineas = rotulo.splitlines()
        return "\n".join(linea.center(ancho) for linea in lineas)
    except Exception:
        return YosCfg.get("Apl_Apl", "")


def _construir_widgets(columnas, nom, cpy):
    rotulo = _generar_rotulo()          # <-- generamos el rótulo aquí

    def _compose(self):
        with Container(id="marco"):
            yield Static(rotulo, id="rotulo-app")   # <-- ASCII art
            yield Static(f" {nom} ", id="titulo-app")
            with Horizontal(id="fila-cols"):
                for col in columnas:
                    with Vertical(classes="col"):
                        yield Static(col["titulo"], classes="titulo-col")
                        for item in col["items"]:
                            yield Button(
                                item["txt"],
                                id=f"btn_{item['id']}",
                                name=item["fnc"]
                            )
            yield Static(f" {cpy} ", id="copyright")
    return _compose

def _on_mount(self):
    try:
        self.query_one("Button").focus()
    except Exception:
        pass


def _on_button_pressed(self, event):
    self.exit(event.button.name or "")


def _on_key(self, event, salir_fnc):
    tecla = event.key
    if tecla == "escape":
        self.exit(salir_fnc)
    elif tecla == "up":
        self.screen.focus_previous()
    elif tecla == "down":
        self.screen.focus_next()
    elif tecla in ("left", "right"):
        botones_por_col = []
        for col in self.query(".col"):
            bts = list(col.query("Button"))
            if bts:
                botones_por_col.append(bts)
        focused = self.screen.focused
        col_actual = None
        for i, bts in enumerate(botones_por_col):
            if focused in bts:
                col_actual = i
                break
        if col_actual is not None:
            siguiente = (col_actual + 1 if tecla == "right" else col_actual - 1) % len(botones_por_col)
            botones_por_col[siguiente][0].focus()
    elif tecla == "enter":
        focused = self.screen.focused
        if focused and isinstance(focused, Button):
            self.exit(focused.name or "")

def Mnu(Fnc_Mnu=None):
    if not Fnc_Mnu:
        Fnc_Mnu = YosCfg["Apl_Mnu"]

    columnas   = _agrupar_menu(Fnc_Mnu, YosCfg.get("Ent", []))
    nom        = YosCfg.get("Apl_Nom", "Aplicación")
    cpy        = YosCfg.get("Apl_Cpy", "")
    salir_fnc  = next((i["fnc"] for col in columnas for i in col["items"] if i["txt"] == "SALIR"), "")

    _fn_compose = _construir_widgets(columnas, nom, cpy)  # rótulo incluido

    def _fn_on_key(self, event):
        _on_key(self, event, salir_fnc)

    class _App(App):
        CSS                    = CSS_MNU
        ENABLE_COMMAND_PALETTE = False
        compose                = _fn_compose
        on_mount               = _on_mount
        on_button_pressed      = _on_button_pressed
        on_key                 = _fn_on_key

    resultado = _App().run()
    return resultado if resultado else ""
