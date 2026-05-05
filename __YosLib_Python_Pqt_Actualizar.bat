@echo off 
cd _Python 
echo ACTUALIZANDO Paquetes de Python 
python.exe -m pip install --upgrade charset-normalizer
python.exe -m pip install --upgrade Django
python.exe -m pip install --upgrade pillow
python.exe -m pip install --upgrade Pygments
python.exe -m pip install --upgrade PyQt6
python.exe -m pip install --upgrade PyQt6-Qt6
python.exe -m pip install --upgrade requests
python.exe -m pip install --upgrade tzdata
cd.. 
del __YosLib_Python_Pqt_Actualizar.bat 
