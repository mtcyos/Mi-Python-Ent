@echo off

Set AplNom=YosMnu
Set ApDir=%~dp0

:: Pongo os Path temporales
call %ApDir%Lib\Yos\YosAccDirPth.bat %ApDir%

:: Muestro lo desactualizado

del __YosLib_Python_Pqt_Actualizar.bat

echo  LISTA DE DESACTUALIZADOS
echo **************************
pip list --outdated
echo **************************

echo SI NO HAY NADA, PARA AQUI
pause

echo. 
echo CREAMOS __YosLib_Python_Pqt_Actualizar.bat

echo @echo off > __YosLib_Python_Pqt_Actualizar.bat
echo cd _Python >> __YosLib_Python_Pqt_Actualizar.bat
echo echo ACTUALIZANDO Paquetes de Python >> __YosLib_Python_Pqt_Actualizar.bat

:: Sincronización del Sistema Yos
echo Creando script de actualizacion...

(for /f "skip=2 tokens=1" %%i in ('python.exe -m pip list --outdated') do (
    echo python.exe -m pip install --upgrade %%i
)) >> __YosLib_Python_Pqt_Actualizar.bat

echo cd.. >> __YosLib_Python_Pqt_Actualizar.bat
echo del __YosLib_Python_Pqt_Actualizar.bat >> __YosLib_Python_Pqt_Actualizar.bat

echo.
echo AHORA EJECUTE __YosLib_Python_Pqt_Actualizar.bat
pause