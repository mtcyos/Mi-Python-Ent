@echo off

Set AplNom=YosMnu
Set ApDir=%~dp0

:: Pongo os Path temporales
call %ApDir%Lib\Yos\YosAccDirPth.bat %ApDir%

:: Muestro lo desactualizado

echo  LISTA DE DESACTUALIZADOS
echo **************************
pip list --outdated
echo **************************

echo on

echo. 
echo CREAMOS __YosLib_Python_Lib_Actualizar.bat
echo Poner en cada libreria
echo "pip install --upgrade <nombre_libreria>"

pause
:: Sincronización del Sistema Yos
echo Creando script de actualización...

(for /f "skip=2 tokens=1" %%i in ('python.exe -m pip list --outdated') do (
    echo python.exe -m pip install --upgrade %%i
)) > __YosLib_Python_Pqt_Actualizar.bat

dir
pause
pip list --outdated > __YosLib_Python_Lib_Actualizar.bat
pause
python.exe -m pip list --outdated --format=freeze > Actualizar_Librerias.bat

pause
pause