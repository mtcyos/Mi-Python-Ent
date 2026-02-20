#import os
import sys
import importlib
import subprocess

# Modulos que necesita la aplicacion
Mdl=("pip","psutil","pytimedinput","pyfiglet","colorama","django","pypyodbc")

# pip uninstall moco

# Verifico que Existen los modulos necesarios
for Dat in Mdl:
#    print(f"Verificando Modulo {Dat}")
    try:
        importlib.import_module(Dat)
 #       import Fnc_Mdl
    except ImportError:
        print(f"\nEl módulo '{Dat}' no está instalado o no se encuentra.")
        if input("Instalar (S=Instalar) : " ).upper()=="S":
            print(f"Instalando {Dat}")
            # Aquí podrías instalarlo automáticamente si quisieras, aunque no es lo común
            # import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", Dat, "--break-system-packages"])
    except Exception as e:
        print(f"Ocurrió otro error al importar: {e}")

# Aqui van TODOS los modulos de la YosLib
from .YosLib import *
from .Yos_Cfg import *
from .Yos_Frm import *
from .Yos_Acd import *
from .Yos_Ini import *
from .Yos_Mnu import *
from .Idd_BdtSvr import *
