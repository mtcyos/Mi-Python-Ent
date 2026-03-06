# -*- coding: utf-8 -*
"""
YosCtr - Desde aqui se controla todo el sistema

@author: Miguel Tortosa
"""

def YosCtr_Ent():
    import os
    import hashlib
    import getpass
    import msvcrt
    from colorama import Fore, Back, Style

    # Verifico Autorizacion

    os.system('cls')
    print(f"{Fore.YELLOW}")
    print("   #     #                  ######  #             ")
    print("    #   #   #####   #####  #       ####### ###### ")
    print("     # #   #     # #       #        #      #     #")
    print("      #    #     #  #####  #        #      ###### ")
    print("      #    #     #       # #        #      #    # ")
    print("      #     #####   #####   ######   ###   #     #")
    print()
    print("         MODIFICACION DEL ENTORNO YosCtr          ")
    print(f"{Style.RESET_ALL}")

    print(f"{Fore.RED}   ACCESO RESTRINGIDO - CONFIGURACIÓN DE ENTORNO\n")
    intentos = 0
    while intentos < 3:
        msg = f"{Fore.YELLOW}   Contraeña Administrador: {Fore.RESET}"
        pwd = Yos_GetPass(msg)

        Mem_Txt_encoded = pwd.encode('utf-8')
        Mem_Txt_md5 = hashlib.md5()
        Mem_Txt_md5.update(Mem_Txt_encoded)
        Mem_Txt_Hex = Mem_Txt_md5.hexdigest()
#        print("PAss "+pwd)
#        print("Apl "+YosCfg["Apl_AdmPas"])
#        print("Hex "+Mem_Txt_Hex)
        if Mem_Txt_Hex == YosCfg["Apl_AdmPas"]:
            break
        else:
            intentos += 1
            print(f"{Fore.RED} Clave Incorrecta. Intentos: {intentos}/3")

    if intentos == 3:
        print(f"{Fore.RED} Acceso Denegado.")
        msvcrt.getch()
        os.system('cls')
        return

    # Generamos el Menu

    from Yos.Idd_TabMod_Txt import Idd_TabMod_Txt
    from Yos.Idd_TabMod import Idd_TabMod

    YosCtr_Mnu = {
    '00': {'Tip': 'Cab', 'Txt': 'ENTORNO',                          'Fnc': '',          'Ent': ''},
    '09': {'Tip': 'Opc', 'Txt': 'SALIR',                            'Fnc': 'S',         'Ent': ''},
    '100': {'Tip': 'Cab', 'Txt': 'MODIFICACION DEL ENTORNO YosCtr', 'Fnc': '',          'Ent': ''},
    '101': {'Tip': 'Opc', 'Txt': 'Dat - DATOS DE LA APLICACION',    'Fnc': 'Dat',       'Ent': ''},
    '102': {'Tip': 'Opc', 'Txt': '------------------',              'Fnc': '',          'Ent': ''},
    '103': {'Tip': 'Opc', 'Txt': 'Mnu - MENUS',                     'Fnc': 'Mnu',       'Ent': ''},
    '104': {'Tip': 'Opc', 'Txt': 'Ord - ORDEN',                     'Fnc': 'Ord',       'Ent': ''},
    '105': {'Tip': 'Opc', 'Txt': 'Brw - BROWSE',                    'Fnc': 'Brw',       'Ent': ''},
    '106': {'Tip': 'Opc', 'Txt': 'ClmMod - COLUMNAS A MODIFICAR',   'Fnc': 'ClmMod',    'Ent': ''},
    '107': {'Tip': 'Opc', 'Txt': '------------------',              'Fnc': '',          'Ent': ''},
    '108': {'Tip': 'Opc', 'Txt': 'Bdt - BASES DE DATOS',            'Fnc': 'Bdt',       'Ent': ''},
    '109': {'Tip': 'Opc', 'Txt': '------------------',              'Fnc': '',          'Ent': ''},
    '200': {'Tip': 'Cab', 'Txt': 'HEERAMIENTAS',                    'Fnc': '',          'Ent': ''},
    '210': {'Tip': 'Opc', 'Txt': 'GENERAR md5',                     'Fnc': 'md5',        'Ent': ''},
#    '200': {'Tip': 'Cab', 'Txt': 'PRUEBAS',                         'Fnc': '',          'Ent': ''},
#    '201': {'Tip': 'Opc', 'Txt': 'Mnu - MENUS (Textual)',           'Fnc': '101',       'Ent': ''},
}

    # INICIO - Proceso del menu
    from Yos import Mnu
    from Yos import Mnu_Txt

    while True:
        match YosCfg["Apl_Etn"]:
            case "Gui": # Modo Terminal - Textual
                MnuFnc = Mnu(YosCtr_Mnu)  # Con textual
            case _:
                MnuFnc = Mnu_Txt(YosCtr_Mnu)  # Con Colorama

        Mem_Svr="YosCfg"
        Mem_Tab=""

        match MnuFnc:
            case "S": # Salir al Menú Anterior
                os.system('cls')
                break
            case "Bdt": # Bdt - BASES DE DATOS
                Mem_Tab="Bdt"

            case "Dat": # Dat - DATOS DE LA APLICACION
                Mem_Tab="Dat"

            case "Mnu": # Mnu - MENUS
                Mem_Tab="Mnu"

            case "Ord": # Ord - ORDEN
                Mem_Tab="Ord"

            case "Brw": # Brw - BROWSE
                Mem_Tab="Brw"

            case "ClmMod": # ClmMod - COLUMNAS A MODIFICAR
                Mem_Tab="ClmMod"

            case "md5": # GENERAR md5
                import hashlib

                os.system('cls')
                print(f"{Fore.GREEN}   * GENERAR md5 *{Fore.WHITE}")
                print()

                Mem_Txt = input("   Cadena a convertir : ")
                Mem_Txt_encoded = Mem_Txt.encode('utf-8')
                Mem_Txt_md5 = hashlib.md5()
                Mem_Txt_md5.update(Mem_Txt_encoded)

                Mem_Txt_Hex = Mem_Txt_md5.hexdigest()

                print(f"\n   El MD5 de  '{Mem_Txt}' es : {Mem_Txt_Hex}")

                from Yos import Yos_ClipCopy
                if Yos_ClipCopy(Mem_Txt_Hex):
                    print("   Se ha copiado al portapapeles.")

                input(f"\n{Fore.YELLOW}   Pulse INTRO para continuar{Fore.RESET}")

#            case "101": # Modificar Menu Textual
#                Idd_TabMod("YosCfg", "Mnu")
#                input("Fin")

        if Mem_Tab:
            match YosCfg["Apl_Etn"]:
                case "Gui": # Modo Terminal - Textual
                    Idd_TabMod(Mem_Svr, Mem_Tab)
                case _:
                    Idd_TabMod_Txt(Mem_Svr, Mem_Tab)

# FIN - Proceso del menu

def Yos_GetPass(prompt=""):
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
