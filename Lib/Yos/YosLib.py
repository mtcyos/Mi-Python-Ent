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
    # Mustra la Funcion que llamo a la Funcion ACTUAL
    # Accede al marco anterior (el llamador)
    if YosCfg["Dbg"]=="S": print("******** Yos.MstFncLin() ********")
    if YosCfg["Dbg"]=="S": print(f"FncNiv={FncNiv}")
    """ Parametros de entrada
        CodBus -> Prefijo a buscar

        Yos.YosCfg_Rcu(CodBus="Prefijo_a_Buscar")
    """
    match FncNiv:
        case "Ant": # Anterior
            marco_llamador = sys._getframe(2)
        case _:
            print("Actual")
            marco_llamador = sys._getframe(1)

    nombre_archivo = marco_llamador.f_code.co_filename
    numero_linea = marco_llamador.f_lineno
    return f"- {nombre_archivo} - {numero_linea}"
#    return " - salida de prueba"

def YosCfg_Rcu(**FncDic):
    if YosCfg["Dbg"]=="S": print("******** Yos.YosCfg_Rcu() ********")
    if YosCfg["Dbg"]=="S": print(f"FncDic={FncDic}")
    """ Parametros de entrada
        CodBus -> Prefijo a buscar

        Yos.YosCfg_Rcu(CodBus="Prefijo_a_Buscar")
    """
    Fnc_Txt="Yos.YosCfg_Rcu(CodBus='_Prefijo_')"
    if not 'CodBus' in FncDic:
       FrmWit(Fnc_Wit=8, Fnc_Txt=f"{Fnc_Txt} La clave 'CodBus' no existe."+ MstFncLin("Ant"))
       return {}

    SalDat={k: v for k, v in YosCfg.items() if k.startswith(FncDic["CodBus"])}
    print(SalDat)
    #for key in YosCfg: # O for key in shelf.keys():
    #    print(f"Clave: {key} -> Valor: {YosCfg[key]}")

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


# -*- coding: utf-8 -*-
# Tim - 2026Jan28 13:05:22

def EmlEnv(Destinatario, Asunto="", Cuerpo=""):
    import smtplib
    from email.message import EmailMessage
    #Yos.EmlEnv("mmedina@upnfm.edu.hn", "Contacto desde YosCtr", "Desde Python con amor.")
    # Caso A (Un solo amigo): EmlEnv("mtcyos@yahoo.es", "Aviso", "Hola Bin")
    # Caso B (Varios socios): EmlEnv(["mtcyos@yahoo.es", "socio@gmail.com"], "Reporte", "Adjunto datos")
    if not Asunto:
        print("******************************")
        print("*        CONTACTENOS         *")
        print("******************************")
        print("")
        print("Debe rellenar todos los campos.")
        print("")

        Mem_Nom=input("Nombre : ")
        if not Mem_Nom:
            return

        Mem_Eml=input("Correo Electrónico : ")
        if not Mem_Eml:
            return

        Asunto=input("Asunto : ")
        if not Asunto:
            return

        print("Mensaje")
        Cuerpo=capturar_texto_multilinea() # input("Mensaje : ")
        if not Cuerpo:
            return

        print("******************************")
        print("*     VERIFIQUE EL EMAIL     *")
        print("******************************")
        print("")
        print("Nombre : " +Mem_Nom)
        print("Correo Electrónico : " +Mem_Eml)
        print("Asunto : " +Asunto)
        print("Mensaje")
        print(Cuerpo)

        if input("\n¿CORRECTO? (Si/): ").strip().capitalize() != "Si":
            return


        MemCab="Nombre : "+Mem_Nom+"\n"
        MemCab=MemCab +"Correo Electrónico : "+Mem_Eml+"\n"
        MemCab=MemCab +"*****************************************\n"
        Cuerpo=MemCab +Cuerpo

    Cuerpo=Cuerpo +"\n\n******** EMAIL DE ENVIO AUTOMATICO, POR FAVOR NO RESPONDA A ESTE EMAIL ********"

    # 1. Normalización: Si es un string, lo convertimos en lista de un elemento
    if isinstance(Destinatario, str):
        Lista_Dest = [Destinatario]
    else:
        Lista_Dest = Destinatario

    # 2. Configuración (Sacar de YosCfg preferiblemente)
    Svr  = "smtp.gmail.com"
    Puo = 587
    Usr  = "dpe_gesitg@upnfm.edu.hn"
    Pas = "wyvzugjdmlcnmamq"
    NombreRemitente = "DFP_GesItg@NoContesteEsteCorreo.com"

    """

Eml_Svr  = "smtp.gmail.com"
Eml_Puo = 587
Eml_Usr  = "dpe_gesitg@upnfm.edu.hn"
Eml_Pas = "wyvzugjdmlcnmamq"
Eml_NombreRemitente = "DFP_GesItg@NoContesteEsteCorreo.com"
Eml_MsgCab=""
Eml_MsgPie="\n\n******** EMAIL DE ENVIO AUTOMATICO, POR FAVOR NO RESPONDA A ESTE EMAIL ********"

    """

    # 3. Construcción del mensaje
    Msg = EmailMessage()
    Msg['Subject'] = Asunto
    Msg['From'] = f"{NombreRemitente} <{Usr}>"
    Msg['To'] = ", ".join(Lista_Dest)
    Msg.set_content(Cuerpo)

    try:
        with smtplib.SMTP(Svr, Puo) as server:
            server.starttls()
            server.login(Usr, Pas)
            # Enviamos a la lista completa
            server.send_message(Msg)
        print(f"SISTEMA: Correo enviado a {len(Lista_Dest)} destinatario(s).")
        return True
    except Exception as e:
        print(f"ERROR EmlEnv: {e}")
        return False

def capturar_texto_multilinea():
    print("Ingrese el texto (Deje una línea en blanco y presione Enter para finalizar):")
    lineas = []

    # Iniciamos el conteo según tu regla de numeración [cite: 2026-01-20]
    while True:
        linea = input(f"{len(lineas) + 1}. > ")
        if linea == "": # Si la línea está vacía, terminamos
            break
        lineas.append(linea)

    texto_final = "\n".join(lineas)
    return texto_final
