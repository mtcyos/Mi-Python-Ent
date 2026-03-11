@echo off
:: Bin > Entorno Protegido
cd /d "%~dp0"

:: Forzamos que la carpeta actual sea la PRIORIDAD absoluta
set PATH=%cd%\_Python;%cd%\_Python\Scripts;C:\Windows\system32

echo --- VERIFICANDO MOTOR ---
cd _Python
python.exe -V
echo Ubicacion real:
where python

echo.
echo --- REPARANDO PIP LOCAL ---
:: Usamos -m para asegurar que usamos el modulo interno
python.exe -m ensurepip --upgrade
python.exe -m pip install --upgrade --force-reinstall pip

echo.
echo --- RESULTADO FINAL ---
:: Usamos python -m pip para evitar que salte a otra carpeta
python.exe -m pip -V

pause