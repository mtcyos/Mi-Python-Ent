# -*- coding: utf-8 -*
"""
YosCtr - Desde aqui se controla todo el sistema

@author: Miguel Tortosa
"""

def Yos_Ent():
    import os
    import hashlib
    import getpass
    import msvcrt
    from colorama import Fore, Back, Style

#    from Yos.Yos_Frm import FrmCls, FrmWit, FrmLin
#    from Yos.Yos_Ini import AplIni
    from Yos import Yos_Pas, FrmCls, FrmWit, FrmLin, AplIni

    # Verifico Autorizacion
    FrmCls()
    AplIni()
    print(f"{Fore.YELLOW}{FrmLin('CONFIGURACIÓN DEL ENTORNO DE LA APLICACION', 'C')}")
    print()
    print(f"{Fore.RED}{FrmLin('ACCESO RESTRINGIDO - POR FAVOR IDENTIFÍQUESE', 'C')}")
    print()

    intentos = 0
    while intentos < 3:
        msg = f"          {Fore.YELLOW}Contraseña Administrador : {Fore.RESET}"
        pwd = Yos_Pas(msg)

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
    FrmCls()

    from Yos.Idd_TabMod_Txt import Idd_TabMod_Txt
    from Yos.Idd_TabMod import Idd_TabMod

    YosCtr_Mnu = {
    '00': {'Tip': 'Cab', 'Txt': 'ENTORNO',                          'Fnc': '',          'Ent': ''},
    '09': {'Tip': 'Opc', 'Txt': 'SALIR',                            'Fnc': 'S',         'Ent': ''},
    '100': {'Tip': 'Cab', 'Txt': 'INFORMACION',                     'Fnc': '',          'Ent': ''},
    '101': {'Tip': 'Opc', 'Txt': 'VER ENTORNO',                     'Fnc': 'EntMst',    'Ent': ''},
    '103': {'Tip': 'Opc', 'Txt': 'VER YosCfg',                      'Fnc': 'YosCfg',    'Ent': ''},
    '200': {'Tip': 'Cab', 'Txt': 'MODIFICACION DEL ENTORNO YosCtr', 'Fnc': '',          'Ent': ''},
    '201': {'Tip': 'Opc', 'Txt': 'Dat - DATOS DE LA APLICACION',    'Fnc': 'Dat',       'Ent': ''},
    '202': {'Tip': 'Opc', 'Txt': '------------------',              'Fnc': '',          'Ent': ''},
    '203': {'Tip': 'Opc', 'Txt': 'Mnu - MENUS',                     'Fnc': 'Mnu',       'Ent': ''},
    '204': {'Tip': 'Opc', 'Txt': 'Ord - ORDEN',                     'Fnc': 'Ord',       'Ent': ''},
    '205': {'Tip': 'Opc', 'Txt': 'Brw - BROWSE',                    'Fnc': 'Brw',       'Ent': ''},
    '206': {'Tip': 'Opc', 'Txt': 'ClmMod - COLUMNAS A MODIFICAR',   'Fnc': 'ClmMod',    'Ent': ''},
    '207': {'Tip': 'Opc', 'Txt': '------------------',              'Fnc': '',          'Ent': ''},
    '208': {'Tip': 'Opc', 'Txt': 'Bdt - BASES DE DATOS',            'Fnc': 'Bdt',       'Ent': ''},
    '300': {'Tip': 'Cab', 'Txt': 'HEERAMIENTAS',                    'Fnc': '',          'Ent': ''},
    '310': {'Tip': 'Opc', 'Txt': 'GENERAR md5',                     'Fnc': 'md5',        'Ent': ''},
#    '400': {'Tip': 'Cab', 'Txt': 'PRUEBAS',                         'Fnc': '',          'Ent': ''},
#    '401': {'Tip': 'Opc', 'Txt': 'Mnu - MENUS (Textual)',           'Fnc': '101',       'Ent': ''},
}
    # INICIO - Proceso del menu
    from Yos import Mnu, Mnu_Txt
    YosCfg['Apl_TitSub'] = "CONFIGURACIÓN DEL ENTORNO DE LA APLICACION"

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
                YosCfg['Apl_TitSub'] = ""
                os.system('cls')
                break

            case "EntMst":
                Yos_Ent_Mst()
            case "YosCfg":
                Yos_Ent_Mst_YosCfg()


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
                FrmCls()
                AplIni()
                print(f"{Fore.YELLOW}{FrmLin('CONFIGURACIÓN DEL ENTORNO YosCtr', 'C')}")
                print()
                print(f"{Fore.GREEN}{FrmLin('* GENERAR CÓDIGO md5 *', 'C')}")
                print()

                Mem_Txt = input(f"{Fore.YELLOW}{FrmLin('Cadena a convertir : ', 8)}{Fore.WHITE}")
                Mem_Txt_encoded = Mem_Txt.encode('utf-8')
                Mem_Txt_md5 = hashlib.md5()
                Mem_Txt_md5.update(Mem_Txt_encoded)

                Mem_Txt_Hex = Mem_Txt_md5.hexdigest()
                Mem_Txt = f"El MD5 de : '{Mem_Txt}' es : {Mem_Txt_Hex}"
                print(f"\n{Fore.GREEN}{FrmLin(Mem_Txt, 10)}")

                from Yos import Yos_ClipCopy
                if Yos_ClipCopy(Mem_Txt_Hex):
                    print(f"\n{Style.BRIGHT}{Fore.BLUE}{FrmLin('Se ha copiado al portapapeles.', 10)}")

                FrmWit()

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

def Yos_Ent_Mst():
    from Yos.Yos_Frm import FrmCls, FrmWit, FrmLin
    from Yos.Yos_Ini import AplIni

    from colorama import Fore, Back, Style

    if YosCfg["Dbg"]=="S": print("******** Yos.AcdEtn() ********")
    Acd=[]
    # Entorno
#    Acd.append("ACERCA DE ...")
#    Acd.append("")

#    Acd.append("ENTORNO")
#    Acd.append("")
    Acd.append("S.O. : " +YosCfg["Etn"]+" - "+YosCfg["Etn_Des"])
    Acd.append("")

    Acd.append("DIRECTORIOS")
    Acd.append("")

    Acd.append("Dir.Apl : "+YosCfg["Apl_Dir"])
    Acd.append("Dir.Yos : " +YosCfg["Yos_Dir"])
    Acd.append("")

    if YosCfg.get("Apl_Bdt_Sis_Dir"):
        Acd.append("Yosis : " +YosCfg["Apl_Bdt_Sis_Dir"])
        Acd.append("")

    if YosCfg.get("Apl_Bdt_Msi_Dir"):
        Acd.append("YosMsi : " +YosCfg["Apl_Bdt_Msi_Dir"])
        Acd.append("")

    if YosCfg.get("Apl_Bdt_Mrp_Dir"):
        Acd.append("YosMrp : " +YosCfg["Apl_Bdt_Mrp_Dir"])
        Acd.append("")

    if YosCfg.get("Apl_Bdt_Mae_Dir"):
        Acd.append("YosMae : " +YosCfg["Apl_Bdt_Mae_Dir"])
        Acd.append("")

    if YosCfg.get("Apl_Bdt_Dat_Dir"):
        Acd.append("YosDat : " +YosCfg["Apl_Bdt_Dat_Dir"])
        Acd.append("")

    if YosCfg.get("Apl_Bdt_Ach_Dir"):
        Acd.append("Archivo : " +YosCfg["Apl_Bdt_Ach_Dir"])
        Acd.append("")

    Acd.append("Dir.Tmp : " +YosCfg["Etn_Tmp"])

    FrmCls()
    AplIni()
    print()
    print(f"{Fore.YELLOW}{FrmLin('ENTORNO DEL SISTEMA', 'C')}")
    print()

    Mem_nLon = 0
    for linea in Acd:
        if len(linea) > Mem_nLon:
            Mem_nLon = len(linea)

    Mem_nLonMax = Mem_nLon +4

    Mem_Txt = f'{"*" * Mem_nLonMax}'
    print(f"{FrmLin(Mem_Txt, 'C')}")

    for lin in Acd:
        Text=f"* {lin:<{Mem_nLon}} *"
        print(f"{FrmLin(Text, 'C')}")

    Mem_Txt = f'{"*" * Mem_nLonMax}'
    print(f"{FrmLin(Mem_Txt, 'C')}")

    FrmWit()
    FrmCls()

def Yos_Ent_Mst_YosCfg():
    from Yos.Yos_Frm import FrmCls, FrmWit, FrmLin
    from Yos.Yos_Ini import AplIni

    from colorama import Fore, Back, Style

    FrmCls()
    AplIni()

    print(f"{Fore.YELLOW}{FrmLin(' SELECCIONE LOS DATOS A VER de YosCfg[*]', 8)}")
    print(f"{Fore.YELLOW}{FrmLin('*****************************************', 8)}")
    print(f"{Fore.YELLOW}{FrmLin(' Vacio = TODO', 8)}")
    print(f"{Fore.YELLOW}{FrmLin(' Apl_ = APLICACION', 8)}")
    print(f"{Fore.YELLOW}{FrmLin(' Dbg_ = DEBUG / DEPURACION', 8)}")
    print(f"{Fore.YELLOW}{FrmLin(' Eml_ = EMAIL', 8)}")
    print(f"{Fore.YELLOW}{FrmLin(' Etn_ = ENTORNO', 8)}")
    print(f"{Fore.YELLOW}{FrmLin(' Usr_ = USUARIO', 8)}")
    print(f"{Fore.YELLOW}{FrmLin(' Yos_ = LIBRERIA Yos', 8)}")
    print()
    print(f"{Fore.YELLOW}{FrmLin(' Apl_Mnu = MENU APLICACION', 8)}")
    print(f"{Fore.YELLOW}{FrmLin('*****************************************', 8)}")
    print()

    Mem_Sub = input(f"{Fore.YELLOW}{FrmLin('SELECCION : ', 8)}")
    print()

    FrmCls()
    AplIni()
    print(f"{Fore.YELLOW}{FrmLin(f'VALORES YosCfg[{Mem_Sub}]', 8)}")
    print(f"{Fore.YELLOW}{FrmLin('*****************************************', 8)}")

#    for k, v in YosCfg.items():
#        if k.startswith(Mem_Sub) and k != "Apl_Mnu":
#            Mem_Txt = f"{Fore.YELLOW}{k} : {Fore.WHITE}{v}"
#            print(FrmLin(Mem_Txt, 8))
    for k, v in YosCfg.items():
#        if k.startswith(Mem_Sub):
        if k.startswith(Mem_Sub):   # Empieza por el Prefijo
            if k == "Apl_Mnu" and Mem_Sub == "Apl_Mnu":
                    Mem_Txt = f"{Fore.YELLOW}{k} : "
                    print(FrmLin(Mem_Txt, 8))
                    if isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            # Formateamos cada opción del menú en una línea nueva
                            Mem_Txt = f"   {Fore.CYAN}'{sub_k}'{Fore.WHITE}: {sub_v}"
                            print(FrmLin(Mem_Txt, 10))
            elif k == "Apl_Mnu" and Mem_Sub != "Apl_Mnu":
                pass
            else:
                Mem_Txt = f"{Fore.YELLOW}{k} : {Fore.WHITE}{v}"
                print(FrmLin(Mem_Txt, 8))
    print(f"{Fore.YELLOW}{FrmLin('*****************************************', 8)}")

    FrmWit()
    FrmCls()



