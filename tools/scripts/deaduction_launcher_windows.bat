REM This script should launch deaduction in a Windows OS.
REM Replace the command python3 by python3.xx if necessary
REM Replace the following by the path to deaduction directory:
set deaductiondir=C:%HOMEPATH%\Documents\dEAduction

REM Go to the Deaduction directory
cd %deaductiondir%

REM *******************
REM Virtual environment
REM *******************

REM Create virtual environment
REM TODO: do this only first time (by checking if dir already exists)
python3 -m venv deaduction_venv

REM Activate virtual environment
call deaduction_venv\Scripts\activate

REM Check packages requirements
REM First time only
python3 -m ensurepip
python3 -m pip install -r requirements.txt


REM *******************
REM Launch Deaduction
REM *******************

REM Go to python src directory
cd src/deaduction

REM Set variables
set DEADUCTION_DEV_MODE="0"

REM Add path to deaduction python sources
set pythonsrc = %deaductiondir%\src
set PYTHONPATH=%PYTHONPATH%;%pythonsrc%

REM Launch Deaduction
python3 -m dui
