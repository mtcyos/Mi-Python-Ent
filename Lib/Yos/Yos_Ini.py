# -*- coding: utf-8 -*-
"""
Procesos de inicio de la Aplicacion

@author: Miguel Tortosa
"""
import sys
import os
import time

from Yos import Yos_Cfg
from Yos.Yos_Frm import FrmCls
#time.sleep(5)

def AplIni():
#    print(YosCfg["Apl_Etn"])
    # Entorno de la Aplicacion Txt=Modo Terminal, Win=Entorno Grafico, Www=Web
    match YosCfg["Apl_Etn"]:
        case "Txt":
            # Terminal
            import ctypes
            import time

            match YosCfg["Etn"]:
                case "Windows":
                    # Obtener el handle de la ventana actual (CMD)
                    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                    # Maximizar la ventana
                    ctypes.windll.user32.ShowWindow(hwnd, 3) # 3 es SW_MAXIMIZE
                    # También puedes usar el atajo con ctypes
                    # ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0) # Presiona tecla Windows (0x5B)
                    # ctypes.windll.user32.keybd_event(0x26, 0, 0, 0) # Presiona Flecha Arriba (0x26)
                    # ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0) # Suelta tecla Windows
                    # ctypes.windll.user32.keybd_event(0x26, 0, 2, 0) # Suelta Flecha Arriba
                    pass

                case "Linux":
                    pass
                    try:
                        # Intentamos maximizar, pero si falla, no rompemos el programa
                        sys.stdout.write("\x1b[9;1t")
                        sys.stdout.flush()
                    except Exception:
                        # Si falla, simplemente limpiamos pantalla y seguimos
                        os.system("clear")

                case _:
                    print("Otro")
            # Obtenemos el ancho actual de la terminal
            import shutil
            # Intentamos obtener el ancho de la terminal, por defecto 80
            try:
                YosCfg["Apl_Etn_Lon"] = shutil.get_terminal_size().columns
            except:
                YosCfg["Apl_Etn_Lon"] = 80

            # Aplicamos el código universal
            import sys
            if os.name == 'nt':
                    os.system('')
            # Nombre de la vantana
            #sys.stdout.write(f"\033]0;{YosCfg["Apl_Apl"]+" - "+YosCfg["Apl_Vsn"]}\007") # Con Sonido
            #sys.stdout.write(f"\x1b]2;{YosCfg["Apl_Apl"]+" - "+YosCfg["Apl_Vsn"]}\x07")
            sys.stdout.write(f"\x1b]2;{YosCfg["Apl_Apl"]+" - "+YosCfg["Apl_Vsn"]}\x1b\\") # Sin Sonido
            sys.stdout.flush()
            # Fin

            FrmCls()

            import pyfiglet
            # Imprimo el Rotulo del nombre de la aplicacion
            print()
            #Rotulo=pyfiglet.figlet_format("YosCtr",font = YosCfg["Apl_Etn_Let"],justify="center", width=YosCfg["Apl_Etn_Lon"])#.strip()
            #print(Rotulo)
            import shutil
            # 1. Generamos el banner y aplicamos el strip (tu parámetro -s)
            Rotulo = pyfiglet.figlet_format(YosCfg["Apl_Apl"],font = YosCfg["Apl_Etn_Let"]).strip()
            Rotulo = " " +Rotulo
            #input(Rotulo)
            # 3. Centramos cada línea individualmente
            lineas = Rotulo.splitlines()
            from colorama import Fore, Style
            for linea in lineas:
                # Imprimimos la línea centrada en el ancho de la terminal
                print(Fore.WHITE+linea.center(YosCfg["Apl_Etn_Lon"]))
#            Rotulo=YosCfg['Apl_Nom']+" - Version - "+YosCfg['Apl_Vsn']
#            print(f"{Rotulo:^{YosCfg["Apl_Etn_Lon"]}}")

#            print(f"{Fore.WHITE+YosCfg['Apl_Nom']:^{YosCfg["Apl_Etn_Lon"]}}")
#            print(f"{YosCfg['Apl_Cpy']:^{YosCfg["Apl_Etn_Lon"]}}")
            #time.sleep(5))
#            print(Fore.BLUE + "═" * YosCfg["Apl_Etn_Lon"]+Fore.WHITE)

        case "Www":
            # Internet
            print("INICIO DE APLICACION EN WEB")

        case _:
            # El "Otherwise" o default
            print(f"ATENCION : EL ENTORNO {YosCfg['Apl_Etn']} NO ESTA IMPLEMENTADO")
            input("PULSE INTRO PARA FINALIZAR")
            import sys
            sys.exit(0)
