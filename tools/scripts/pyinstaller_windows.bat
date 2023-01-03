
// First time only
// pip3 install pyinstaller
// python3 -m venv pyinstaller_env

// Activate virtual env
pyinstaller_env\Scripts\activate.bat

// First time only
// python3 -m pip install -r ..\requirements.txt

// Is this useful?
// Set variables
set DEADUCTION_DEV_MODE=0
set PYTHONPATH=C:\Users\Flore\Documents\GitHub\dEAduction\src

cd ..\..\src

pyinstaller deaduction\dui\__main__.py --onefile --windowed --clean --add-data deaduction\lean_src;deaduction\lean_src --add-data deaduction\share;deaduction\share

