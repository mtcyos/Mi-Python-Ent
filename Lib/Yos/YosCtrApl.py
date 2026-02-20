# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 16:12:06 2025
@author: mtcyos

yosLib_CtrApl - Libreria de Control de Acceso a las Aplicaciones y Subprogramas
"""

import sys
import os
import getpass

import YosIdd
import Yos

print("YosCtrApl")


def AccAplUsr():
    """Este es el login de la aplicacion"""
    YosIdd.Bdt_Cnx()
    Mem_Num = 1
    while Mem_Num<4:
        print("ACCESO A LA APLICACION (",Mem_Num,")")
        global Yos_Usr_Nik
        print("CORRECTO ",Yos.Usr_Nik)
        # nueva extrcutura vDbt es una Variable de programa
        vUsrNik=input("USUARIO : ")
        vUsrPas= getpass.getpass("CONTRASEÑA : ") 
        print(vUsrPas)
        vUsrPas = Yos.Md5(vUsrPas)
        print("vUsrPas",vUsrPas)
        #vUsrNik="mtcyos"
        #vUsrPas="274834"
        Cont=input("Continuar")

        Mem_Sql=YosIdd.Bdt_Cnx_Sql('SELECT * FROM Usr WHERE cNik="'+vUsrNik+'" and cPasMd5="'+vUsrPas+'"')
        if Mem_Sql!=None:
            Yos.Apl["Usr_Nik"]=Mem_Sql[0]
            Yos.Apl["Usr_Nom"]=Mem_Sql[1]
            print("CORRECTO ",Yos.Usr_Nik)
            return
            
        Mem_Num += 1
        print("Mem_Num->",Mem_Num)

    else:
            input("ADIOS")
            sys.exit()