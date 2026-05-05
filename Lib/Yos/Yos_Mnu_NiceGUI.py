#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from nicegui import ui, app
import builtins
import platform
import asyncio

# Importamos lo necesario de tu librería Yos
from Yos import Yos_TimeStamp

# Recuperamos la configuración global
YosCfg = getattr(builtins, 'YosCfg', {})

def Mnu_NiceGUI(Fnc_Mnu):
    res = {'id': '99'}

    if not Fnc_Mnu:
        Fnc_Mnu = YosCfg.get("Apl_Mnu", {})

    secret = "yos_2026_secret_key"

    # Datos para la cabecera
    datos_izq = "Usuario : " + YosCfg.get('Usr_Nik', "mtcyos")
    txt_rotulo_lista = YosCfg.get("Apl_Rot", ["CONTROL CENTRAL"])
    mem_cen = '\n'.join(txt_rotulo_lista)

    # Buscar Opcion Salir
    Salir_Num = "99"
    for clave, valor in Fnc_Mnu.items():
        if valor.get("Txt", "").upper() == "SALIR":
            Salir_Num = clave
            break

    # Lógica de grupos para las columnas
    grupos = {}
    items = sorted(Fnc_Mnu.items())
    indice_grupo = -1
    ent_cfg = YosCfg.get("Ent", "")

    for clave, valor in items:
        ent = valor.get("Ent", "")
        if ent == "" or ent in ent_cfg:
            if valor.get("Tip") == "Cab":
                indice_grupo += 1
                grupos[str(indice_grupo)] = [{"id": clave, "txt": valor["Txt"]}]
            elif valor.get("Tip") == "Opc":
                if indice_grupo == -1: indice_grupo = 0
                if str(indice_grupo) not in grupos: grupos[str(indice_grupo)] = []
                grupos[str(indice_grupo)].append({"id": clave, "txt": valor["Txt"]})

    # --- CORRECCIÓN CRÍTICA: Función asíncrona para permitir el retorno ---
    async def finalizar(id_opcion):
        import asyncio  # <--- Asegúrate de que esta línea esté AQUÍ
        res['id'] = id_opcion
        app.storage.user['seleccion_id'] = id_opcion

        # Damos un respiro para que NiceGUI guarde el storage
        await asyncio.sleep(0.2)

        if platform.system() == "Windows" and YosCfg.get("Dbg") == "X":
            if hasattr(app, 'native') and app.native.main_window:
                app.native.main_window.close()
            app.shutdown()
        else:
            app.shutdown()

    def on_enter(e):
        val = e.sender.value.strip().upper()
        if val in Fnc_Mnu:
            # Lanzamos la tarea asíncrona
            ui.timer(0.1, lambda: finalizar(val), once=True)
        else:
            e.sender.value = ""

    @ui.page('/')
    def main_page():
        if 'seleccion_id' not in app.storage.user:
            app.storage.user['seleccion_id'] = Salir_Num

        ui.colors(primary='#1e3a8a', secondary='#222222')
        ui.add_head_html('<style>body { background-color: #000033; color: white; font-family: monospace; }</style>')

        with ui.column().classes('w-full px-4 py-4 items-center'):
            with ui.row().classes('w-full justify-between items-start mb-2'):
                ui.label(datos_izq).classes('text-cyan-400 text-xs')
                ui.label(mem_cen).classes('text-orange-400 font-bold text-center whitespace-pre')
                ui.label(f"Tim: {Yos_TimeStamp()}").classes('text-cyan-400 text-xs')

            ui.separator().classes('bg-blue-600 mb-4 h-[2px]')

            with ui.row().classes('w-full justify-center gap-4'):
                for k in sorted(grupos.keys()):
                    with ui.column().classes('items-center border border-blue-900 p-2'):
                        ui.label(grupos[k][0]["txt"]).classes('text-blue-400 font-bold mb-2')
                        for i in range(1, len(grupos[k])):
                            item = grupos[k][i]
                            # Llamada asíncrona al hacer clic
                            ui.button(f"[{item['id']}] {item['txt']}",
                                      on_click=lambda o=item['id']: finalizar(o)) \
                                .classes('w-full bg-blue-800 text-white text-xs hover:bg-orange-500 rounded-none')

            with ui.row().classes('w-full bg-blue-900 p-2 mt-4 items-center'):
                ui.label("SELECCIONE OPCIÓN :").classes('text-white font-bold')
                inp = ui.input().on('keydown.enter', on_enter).classes('bg-black text-white w-20 px-2')
                inp.props('dark dense borderless')

    # ARRANCAR
    # --- ARRANCAR PROTEGIDO (Versión Final) ---
    from nicegui import core
    puerto = int(YosCfg.get("Prt", 8080))

    # El secreto es usar hasattr para ver si el servidor ya tiene configurado el middleware
    if not hasattr(core.app, 'middleware_stack') or core.app.middleware_stack is None:
        if YosCfg.get("Dbg") == "X":
            ui.run(port=puerto, reload=False, native=True, storage_secret=secret, title="Yos Control")
        else:
            ui.run(host='0.0.0.0', port=puerto, reload=False, show=False, storage_secret=secret)
    else:
        # Si ya existe el stack, el servidor está listo.
        # Solo necesitamos que el bucle de eventos procese la nueva entrada.
        import asyncio
        if not core.app.is_started:
             # Si por alguna razón se detuvo el loop pero no el proceso
             ui.run(port=puerto, reload=False, show=False)
