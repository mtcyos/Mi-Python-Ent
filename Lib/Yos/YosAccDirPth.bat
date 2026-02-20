@echo off

:: Traemos en Directorio inicial por parametro 1
:: Ponemos, de manera temporal, los accesos a mi Version de Python

set yosRoot=%1_Python\
set yosScripts=%yosRoot%Scripts\

set PATH=%yosRoot%;%yosScripts%;%PATH%

:: No ponemos 'pause' aquí para que sea silencioso
