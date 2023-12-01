REM Is this useful?
REM Set variables
set DEADUCTION_DEV_MODE="0"
set PYTHONPATH="C:%HOMEPATH%\Documents\GitHub\dEAduction\src"

REM First time only
REM pip3 install pyinstaller


REM Activate virtual env
cd C:%HOMEPATH%\Documents\GitHub\dEAduction\tools\scripts
REM If the python3 cmd not work, this is because the path to python3.exe  is not part
REM of the PATH environment variable.
REM You can modify PATH in the command window,
REM set PATH="%PATH%;<new_path>"  where <new_path> is something like
REM C:\%HOMEPATH%\AppData\Local\Programs\Python
python3 -m venv pyinstaller_env
pyinstaller_env\Scripts\activate.bat

REM First time only
REM python3 -m pip install -r ..\requirements.txt


cd ..\..\src

REM THe following line will NOT work, unless the path to Python Scripts
REM has been added to the PATH environment variable
REM Find your own python/Scripts address by searching in the
REM %HOMEPATH%\AppData\Local\
REM and add it to the PATH variable by
REM set PATH="%PATH%;<your pyinstaller path>"
REM This is the file where Windows will look for pynstaller.exe
pyinstaller deaduction\dui\__main__.py --onefile --windowed --clean --add-data deaduction\lean_src;deaduction\lean_src --add-data deaduction\share;deaduction\share

