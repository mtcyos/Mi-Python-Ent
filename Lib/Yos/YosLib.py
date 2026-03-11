#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
   YosLib.py
   LIBRERIA DE PROPOSITO GENERAL>

   Copyright (c) 2026 Miguel Tortosa

   Licenciado bajo la Licencia MIT.

   Consulte el archivo LICENCIA en la raíz del proyecto para más información.
"""

import sys
import inspect
from .Yos_Frm import *

def MstFncLin(FncNiv="Act"):
    # Mustra la Funcion que llamo a la Funcion ACTUAL (Act/Ant)
    if YosCfg["Dbg"]=="S": print("******** Yos.MstFncLin() ********")
    if YosCfg["Dbg"]=="S": print(f"FncNiv={FncNiv}")

    match FncNiv:
        case "Ant": # Anterior
            marco_llamador = sys._getframe(2)
        case _:
            print("Actual")
            marco_llamador = sys._getframe(1)

    nombre_archivo = marco_llamador.f_code.co_filename
    numero_linea = marco_llamador.f_lineno
    return f"- {nombre_archivo} - {numero_linea}"

def YosCfg_Rcu(**FncDic):
    # Busca dentro de YosCfg las Clm del prefijo indicado Yos.YosCfg_Rcu(CodBus='_Prefijo_')
    if YosCfg["Dbg"]=="S": print("******** Yos.YosCfg_Rcu() ********")
    if YosCfg["Dbg"]=="S": print(f"FncDic={FncDic}")
    Fnc_Txt="Yos.YosCfg_Rcu(CodBus='_Prefijo_')"

    if not 'CodBus' in FncDic:
       FrmWit(Fnc_Wit=8, Fnc_Txt=f"{Fnc_Txt} La clave 'CodBus' no existe."+ MstFncLin("Ant"))
       return {}

    SalDat={k: v for k, v in YosCfg.items() if k.startswith(FncDic["CodBus"])}
    print(SalDat)
    #for key in YosCfg: # O for key in shelf.keys():
    #    print(f"Clave: {key} -> Valor: {YosCfg[key]}")

def EmlEnv(Destinatario=None, Asunto="", Cuerpo=""):
    # Envia un Email
    #Yos.EmlEnv("mmedina@upnfm.edu.hn", "Contacto desde YosCtr", "Desde Python con amor.")
    # Caso A (Un solo amigo): EmlEnv("mtcyos@yahoo.es", "Aviso", "Hola Bin")
    # Caso B (Varios socios): EmlEnv(["mtcyos@yahoo.es", "socio@gmail.com"], "Reporte", "Adjunto datos")

    import smtplib
    from email.message import EmailMessage
    from colorama import Fore, Back, Style

    from Yos import FrmCls, FrmWit, FrmLin, AplIni

    if not YosCfg.get("Eml_Svr", "").strip():
        FrmWit(f'\n{Fore.RED} [ ERROR ] El servidor de (YosCfg."Eml_Svr") correo no está configurado la tabla Dat.' ,8)
        return False

    FrmCls()
    AplIni()
    print()
    print(f"{Fore.YELLOW}{FrmLin('ENVÍO DE EMAIL', 'C')}{Style.RESET_ALL}")
    print()

    if not Destinatario or not Asunto or not Cuerpo:
        print(f"{Fore.GREEN}{FrmLin('******************************', 8)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{FrmLin('*        ENVÍO DE EMAIL      *', 8)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{FrmLin('******************************', 8)}{Style.RESET_ALL}")
        print()
        print(f"{Fore.RED}{FrmLin('DEBE RELLENAR TODOS LOS CAMPOS.', 8)}{Style.RESET_ALL}")
        print(f"{Fore.RED}{FrmLin('LOS CAMPOS CON * SON OBLIGATORIOS.', 8)}{Style.RESET_ALL}")
        print()

        if not Destinatario:
            print(f"{Style.BRIGHT}{Fore.BLUE}{FrmLin('EMAIL DESTINATARIO', 8)}")
            print(f"{Style.BRIGHT}{Fore.BLUE}{FrmLin('Uno solo : email', 8)}")
            print(f"{Style.BRIGHT}{Fore.BLUE}{FrmLin('Varios   : email, email_2, email_3', 8)}")
            print()
            Destinatario = input(f"{FrmLin(f'{Fore.RED}* {Fore.YELLOW}EMAIL DESTINATARIO : ', 6)}{Style.RESET_ALL}")
            if not Destinatario:
                FrmWit(f'{Fore.RED} [ ERROR ] EMAIL DESTINATARIO ES OBLIGATORIO.' ,8)
                return False
        else:
            print((f"{Fore.YELLOW}{FrmLin(f'DESTINATARIO : {Fore.WHITE}{Destinatario}', 8)}"))

        if not Asunto:
            Mem_Nom = input(f"\n{Fore.YELLOW}{FrmLin('SU NOMBRE : ', 8)}{Style.RESET_ALL}")
            Mem_Eml = input(f"{Fore.YELLOW}{FrmLin('SU EMAIL  : ', 8)}{Style.RESET_ALL}")

            Asunto = input(f"\n{FrmLin(f'{Fore.RED}* {Fore.YELLOW}ASUNTO : ', 6)}{Style.RESET_ALL}")
            if not Asunto:
                FrmWit(f'{Fore.RED} [ ERROR ] ASUNTO ES OBLIGATORIO.' ,8)
                return False

        if not Cuerpo:
            print(f"\n{FrmLin(f'{Fore.RED} * {Fore.YELLOW}MENSAJE', 6)}{Style.RESET_ALL}")
            Cuerpo = Yos_TxtMulLin(8) # input("Mensaje : ")
            if not Cuerpo:
                FrmWit(f'{Fore.RED} [ ERROR ] MENSAJE ES OBLIGATORIO.' ,8)
                return False
        else:
            # Si el cuerpo NO está vacío (trae la tabla), pero faltaba otro dato
            # preguntamos si quiere añadir algo más a esa tabla
            print(f"\n{Style.BRIGHT}{Fore.BLUE}{FrmLin('EL MENSAJE YA CONTIENE DATOS.', 8)}")

            if input(f"{Fore.YELLOW}{FrmLin('¿ AÑADIR OTRA INFORMACIÓN (S/) ? ', 8)}{Style.RESET_ALL}").upper() == 'S':
                nota = input(f"{Fore.YELLOW}{FrmLin('INFORMACIÓN : ', 8)}{Style.RESET_ALL}")
                if nota:
                    Cuerpo = f"{nota}\n\n{Cuerpo}"

        FrmCls()
        AplIni()
        print()
        print(f"{Fore.YELLOW}{FrmLin('ENVÍO DE EMAIL', 'C')}{Style.RESET_ALL}")
        print()
        print(f"{Fore.GREEN}{FrmLin('******************************', 8)}")
        print(f"{Fore.GREEN}{FrmLin('*     VERIFIQUE EL EMAIL     *', 8)}")
        print(f"{Fore.GREEN}{FrmLin('******************************', 8)}")
        print()
        print(f"{Fore.YELLOW}{FrmLin('******************************', 8)}")
        print(f"{Fore.YELLOW}{FrmLin(f'DESTINATARIO : {Fore.WHITE}{Destinatario}', 8)}")
        print()
        print((f"{Fore.YELLOW}{FrmLin(f'SU NOMBRE : {Fore.WHITE}{Mem_Nom}', 8)}"))
        print((f"{Fore.YELLOW}{FrmLin(f'SU EMAIL  : {Fore.WHITE}{Mem_Eml}', 8)}"))
        print()
        print((f"{Fore.YELLOW}{FrmLin(f'ASUNTO : {Fore.WHITE}{Asunto}', 8)}"))
        print()
        print(f"{Fore.YELLOW}{FrmLin('MENSAJE : ', 8)}")
        for Lin in Cuerpo.splitlines():
            print(FrmLin(Lin, 10))
        print()
        if input(f"{Fore.YELLOW}{FrmLin('¿ CORRECTO (S/) ? : ', 8)}{Style.RESET_ALL}").strip().capitalize() != "S":
            return False

        MemCab=""
        if Mem_Nom:
            MemCab=MemCab + f"{Mem_Nom}\n"
        if Mem_Eml:
            MemCab=MemCab + f"Correo Electrónico : {Mem_Eml}\n"
        MemCab=MemCab + "*****************************************\n"
        Cuerpo=MemCab +Cuerpo

    Cuerpo = YosCfg["Eml_MsgCab"].replace("\\n", "\n") +Cuerpo + YosCfg["Eml_MsgPie"].replace("\\n", "\n")

    # 1. Normalización: Si es un string, lo convertimos en lista de un elemento
    if isinstance(Destinatario, str):
        Lista_Dest = [Destinatario]
    else:
        Lista_Dest = Destinatario

    # 3. Construcción del mensaje
    Msg = EmailMessage()
    Msg['Subject'] = Asunto
    Msg['From'] = f'{YosCfg["Eml_EmlEnv"]} <{YosCfg["Eml_EmlEnv"]}>'
    Msg['To'] = ", ".join(Lista_Dest)
    Msg.set_content(Cuerpo)

    try:
        with smtplib.SMTP(YosCfg["Eml_Svr"], YosCfg["Eml_Puo"]) as server:
            server.starttls()
            server.login(YosCfg["Eml_Usr"], YosCfg["Eml_Pas"])
            # Enviamos a la lista completa
            server.send_message(Msg)
        FrmWit(f'{Style.BRIGHT}{Fore.BLUE} [ OK ] SISTEMA: Correo enviado a {len(Lista_Dest)} destinatario(s).' ,8)
        return True
    except Exception as e:
        FrmWit(f'{Style.BRIGHT}{Fore.BLUE} [ ERROR ] {e}.' ,0)
        print(f"ERROR EmlEnv: {e}")
        return False

def Yos_TxtMulLin(Fnc_Esp=0):
    # Introduce los datos en un Texto Multilinea
    from colorama import Fore, Back, Style

    try:
        # Convertimos a entero. Si es "8", se vuelve 8.
        Fnc_Esp = int(Fnc_Esp)
    except (ValueError, TypeError):
        # Si mandan algo que no es número (ej: "hola"), volvemos a 0
        Fnc_Esp = 0

    print(f"{Style.BRIGHT}{Fore.BLUE}{FrmLin('Ingrese el texto (Deje una línea en blanco y presione Enter para finalizar.', Fnc_Esp)}")
    lineas = []

    # Iniciamos el conteo según tu regla de numeración [cite: 2026-01-20]
    while True:
#       linea = input(f"{len(lineas) + 1}-> ")
        linea = input(f"{Fore.YELLOW}{FrmLin(f'{len(lineas) + 1}-> ', 8)}{Style.RESET_ALL}")
        if linea == "": # Si la línea está vacía, terminamos
            break
        lineas.append(linea)

    texto_final = "\n".join(lineas)
    return texto_final

def Yos_ClipCopy(texto):
    # Manda el texto a PortaPapeles
    import pyperclip
    """
    Copia cualquier cadena al portapapeles del sistema operativo actual.
    """
    try:
        # 1. Limpiamos espacios laterales para evitar errores de pegado
        cadena = str(texto).strip()

        # 2. Comando universal
        pyperclip.copy(cadena)

        return True
    except Exception as e:
        input(f"Error Portapapeles: {e}")
        return False

def Yos_Pas(prompt=""):
    # Entrada de datos tipo Password
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

def Yos_TimeStamp(Fnc_Nue=""):
    # Devuelve el formato TimeStamp , Fnc_Nue =="Cre" añado la marca de registro nuevo +"*"
    from datetime import datetime

    Mem_TimeStamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if Fnc_Nue =="Cre":
        Mem_TimeStamp = Mem_TimeStamp +"*"
    else:
        Mem_TimeStamp = Mem_TimeStamp +" "

    return Mem_TimeStamp


# PARA REVISION *********************************************************************
def Dic_Rcu(Fnc_Pre, Fnc_Dic="gcAplDat"):
    # Devuelve un Dicccionario Segun el Prefijo de los datos "Yos_"
    if YosCfg["Dbg"]=="S": print("******** Yos.Dic_Rcu() ********")
    print("YosCfg="+YosCfg)

    if isinstance(Fnc_Dic, dict):
        if gcAplDat["Dbg"]=="S": print("Es un diccionario Reg."+str(len(Fnc_Dic))+" Fnc_Pre="+Fnc_Pre)
        if gcAplDat["Dbg"]=="S": print(Fnc_Dic)
        SalDat={k: v for k, v in Fnc_Dic.items() if k.startswith(Fnc_Pre)}
    else:
        if gcAplDat["Dbg"]=="S": print("No es un diccionario")
        SalDat={}

    return SalDat

def Md5(Fnc_Txt):
    # Convierte Texto a Md5
    md5_hash = hashlib.md5()
    Fnc_Txt = Fnc_Txt.encode('utf-8')
    print(Fnc_Txt)
    md5_hash.update(Fnc_Txt)
    Fnc_Txt = md5_hash.hexdigest()
    print(Fnc_Txt)
    return Fnc_Txt

def Yos_Otp(Fnc_Txt):
    #def GenOtp()

    # Generate a secure random secret key (store this securely!)
    # It should be base32 encoded for compatibility with pyotp
    secret = base64.b32encode(pyotp.random_base32().encode()).decode()

    # Create a TOTP object
    totp = pyotp.TOTP(secret)

    # Generate a current OTP
    current_otp = totp.now()
    print(f"CODIGO TOTP: {current_otp}")

    # Verify an OTP (e.g., entered by the user)B
    user_entered_otp = input("Enter the OTP: ")
    if totp.verify(user_entered_otp):
        print("OTP verified successfully!")
    else:
            print("Invalid OTP.")

    # To generate a provisioning URI for QR code generation (e.g., for Google Authenticator)
    # Replace 'YourAppName' and 'user@example.com' with your actual values
    provisioning_uri = totp.provisioning_uri(name='user@example.com', issuer_name='YourAppName')
    print(f"Provisioning URI: {provisioning_uri}")
