#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Yos_Mnu.py
    Genero el Menu de la Aplicacion

    Copyright (c) 2026 Miguel Tortosa

    Licenciado bajo la Licencia MIT.

    Consulte el archivo LICENCIA en la raíz del proyecto para más información.
"""
from Yos import Yos_FrmCls, FrmWit, Apl_Txt_Fin, FrmCab

import os

# --- IMPORTACIONES DE PROMPT_TOOLKIT ---
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Label, TextArea, Button
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

def Mnu(Fnc_Mnu):
    # Menu Grafico con soporte de Raton
    """
    Menú dinámico con persistencia.
    Se mantiene ejecutándose hasta que se elige una función externa.
    """

    if not Fnc_Mnu:
        Fnc_Mnu = YosCfg["Apl_Mnu"]

    Salir_Num = ""
    while True:
#        AplIni()
        from Yos import FrmLin

        # Recuperar variables de configuración
        ancho_total = YosCfg["Apl_Etn_Lon"] -1
        titulo_app = f"{YosCfg['Apl_Nom']}"
        subtitulo_app = YosCfg['Apl_TitSub']
        copy_app = YosCfg['Apl_Cpy']

        # 1. Preparar el agrupamiento por Tipo (Cab / Opc)
        grupos = {}
        items = sorted(Fnc_Mnu.items())
        indice_grupo = -1

        for clave, valor in items:
            ent = valor.get("Ent", "")
            if ent == "" or ent in YosCfg["Ent"]:
                tipo = valor.get("Tip")

                # Si es CABECERA
                if tipo == "Cab":
                    indice_grupo += 1
                    str_idx = str(indice_grupo)
                    grupos[str_idx] = []
                    grupos[str_idx].append({
                        "id": clave,
                        "txt": valor["Txt"],
                        "fnc": valor.get("Fnc", "")
                    })

                # Si es OPCIÓN
                elif tipo == "Opc":
                    if indice_grupo == -1:
                        indice_grupo = 0
                        grupos["0"] = []

                    grupos[str(indice_grupo)].append({
                        "id": clave,
                        "txt": valor["Txt"],
                        "fnc": valor.get("Fnc", "")
                    })

        # 2. Preparar columnas
        claves_grupos = sorted(grupos.keys())
        columnas = [grupos[k] for k in claves_grupos]
        num_cols = len(columnas)
        if num_cols == 0: return ""

        ancho_col = ancho_total // num_cols

        # Variables de estado para prompt_toolkit
        estado_aplicacion = {"opcion": None}

        # --- CONSTRUCCIÓN DE LA INTERFAZ PROMPT_TOOLKIT ---
        elementos_body = []

        # ROTULO
        lineas_cab_lista = YosCfg["Apl_Cab"]
        lineas_cab_lista.insert(0, " " * (YosCfg["Apl_Etn_Lon"] - 1))
        Mem_Cab_Final = '\n'.join(lineas_cab_lista)         # Convertimos la lista en un solo string para el control visual

        # Creamos la Window que respetará tus espacios y el logo a la derecha
        lbl_Cab = Window(
            content=FormattedTextControl(
                HTML(f"<orange>{Mem_Cab_Final}</orange>")
            ),
            height=len(lineas_cab_lista),
            wrap_lines=False
        )

        # Añadimos el objeto a la lista de elementos que se dibujarán
        elementos_body = []
        elementos_body.append(lbl_Cab)
        # ----------------------------------
        titulo_app_espaciado = FrmLin(titulo_app, 'C')
        lbl_titulo = Label(HTML(f"<ansiyellow><b>{titulo_app_espaciado}</b></ansiyellow>"))
        elementos_body.append(lbl_titulo)

        if subtitulo_app:
            subtitulo_app_espaciado = FrmLin(subtitulo_app, 'C')
            lbl_subtitulo = Label(HTML(f"<ansicyan>{subtitulo_app_espaciado}</ansicyan>"))
            elementos_body.append(lbl_subtitulo)

        # Títulos de las columnas
        cabeceras = []
        for i, col in enumerate(columnas):
            titulo = col[0]["txt"].upper()
            ancho_disponible = ancho_col - 1

            # Forzamos centrado físico en el texto
            bloque_titulo = f"{titulo[:ancho_disponible]:^{ancho_disponible}}"

            # Anclamos el width real a nivel de widget para que VSplit no encoja la cabecera
            lbl_texto = Label(HTML(f"<b><ansimagenta>{bloque_titulo}</ansimagenta></b>"), width=ancho_disponible)

            if i < len(columnas) - 1:
                # El pipe azul ocupa exactamente 1 de width, igual que en las filas inferiores
                lbl_pipe = Label(HTML("<ansiblue>|</ansiblue>"), width=1)
                cabeceras.append(VSplit([lbl_texto, lbl_pipe]))
            else:
                cabeceras.append(lbl_texto)

        elementos_body.append(VSplit(cabeceras))
        elementos_body.append(Label(HTML("<ansiblue>" + "═" * ancho_total + "</ansiblue>")))

        # --- FUNCIÓN MANEJADORA DE BOTONES ---
        def crear_handler(id_opc):
            def handler():
                estado_aplicacion["opcion"] = id_opc
                app.exit()
            return handler

        # Filas de opciones
        max_filas = max(len(col) for col in columnas)

        for i in range(1, max_filas):
            fila_elementos = []
            for j, col in enumerate(columnas):
                ancho_disponible = ancho_col - 1

                if i < len(col):
                    item = col[i]
                    id_ver = "S".ljust(len(item['id'])) if item['txt'] == "SALIR" else item['id']
                    if item['txt'] == "SALIR":
                        Salir_Num = item['id']

                    texto_celda = f" {id_ver} - {item['txt']}"
                    contenido = f"{texto_celda[:ancho_disponible]:<{ancho_disponible}}"

                    # Botón como opción de menú, sin corchetes
                    btn = Button(contenido, handler=crear_handler(item['id']), width=ancho_disponible)
                    btn.left_symbol = ""
                    btn.right_symbol = ""

                    if j < num_cols - 1:
                        fila_elementos.append(VSplit([btn, Label(HTML("<ansiblue>|</ansiblue>"), width=1)]))
                    else:
                        fila_elementos.append(btn)
                else:
                    # Rellenar espacio vacío
                    fila_elementos.append(Label(" " * ancho_disponible, width=ancho_disponible))
                    if j < num_cols - 1:
                        fila_elementos.append(Label(HTML("<ansiblue>|</ansiblue>"), width=1))

            elementos_body.append(VSplit(fila_elementos))

        elementos_body.append(Label(HTML("<ansiblue>" + "═" * ancho_total + "</ansiblue>")))
        elementos_body.append(Label(HTML(f"<ansiyellow>{copy_app:^{ancho_total}}</ansiyellow>")))

        # Entrada de texto inferior (modo manual con Intro)
        lbl_prompt = Label(HTML("<orange>  Seleccione Opción : </orange>"), width=23)
        txt_opcion = TextArea(multiline=False, width=3)

        def aceptar_entrada(buff):
            texto = txt_opcion.text.strip()
            if texto:
                estado_aplicacion["opcion"] = texto
                app.exit()
            return True # Retener texto en buffer

        txt_opcion.accept_handler = aceptar_entrada
        elementos_body.append(VSplit([lbl_prompt, txt_opcion]))

        # KeyBindings (atajos de teclado)
        kb = KeyBindings()

        @kb.add('c-c')
        @kb.add('c-q')
        def _(event):
            estado_aplicacion["opcion"] = Salir_Num if Salir_Num else "99"
            event.app.exit()

        # Estilo estético (basado en Win_prompt_toolkit y colores ANSI)
        estilo_yos = Style.from_dict({
            'pantalla': 'bg:#000000',
            'button': 'fg:white bg:#000000',
            'button.focused': 'bg:#0000aa fg:white bold',
            'text-area': 'bg:#333333 fg:white',
        })

        layout = Layout(HSplit(elementos_body, style='class:pantalla'))

        app = Application(
            layout=layout,
            key_bindings=kb,
            style=estilo_yos,
            mouse_support=True,
            full_screen=True,
            erase_when_done=True
        )

        # Foco inicial en el TextArea por si prefieren teclear
        app.layout.focus(txt_opcion)

        # Correr la aplicación
        app.run()

        # Lógica secundaria al salir de app.run()
        MnuOpc = estado_aplicacion["opcion"]

        if not MnuOpc:
            return ""

        if MnuOpc.upper() == 'S':
            MnuOpc = Salir_Num
        else:
            MnuOpc = MnuOpc.zfill(2)

        # Lógica de validación
        if MnuOpc in Fnc_Mnu:
            ent_opc = Fnc_Mnu[MnuOpc].get("Ent", "")
            if ent_opc == "" or ent_opc in YosCfg["Ent"]:
                MnuFnc = Fnc_Mnu[MnuOpc].get("Fnc", "")
                if MnuFnc != "":
                    return MnuFnc
            else:
                continue
        else:
            continue
