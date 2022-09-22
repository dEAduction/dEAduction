#!/bin/bash
### Deaduction pyinstaller script
echo "This is D∃∀DUCTION pyinstaller builder script"
echo "It should be launched from the tools/scripts directory"
### Launch me from where I am,
### dEAduction/tools/scripts

############
# Check OS #
############
DEADUCTION_ON_MAC=0
DEADUCTION_ON_LINUX=0
DEADUCTION_ON_WINDOWS=0

OS="$(uname)"
if [[ "$OS" == "Linux" ]]; then
  DEADUCTION_ON_LINUX=1
  echo "OS = Linux"
  VERSION=$(cat /etc/issue)
  if [[ ${VERSION::6} == "Ubuntu" -o ${VERSION::6} == "Debian" ]]; then
    UBUNTU_DEBIAN=1
    echo "(Ubuntu or Debian detected)"
  fi

elif [[ "$OS" = "Darwin" ]]; then
  echo "OS = Darwin (Mac)"
  DEADUCTION_ON_MAC=1
else
  echo "OS:"
  echo $OS
  abort "builder works only on Linux and MacOs."
fi

# Machine hardware name
# CPU="$(/usr/bin/uname -m)"
# if [[ "$CPU" == "arm64" ]]; then
#  warn "Brew has some issues on the new mac M1 (as of 06/21)"
#  echo "which may affect gmp install"
#  echo "see e.g. https://www.wisdomgeek
#  .com/development/installing-intel-based-packages-using-homebrew-on-the-m1-mac/"
#  echo "and specifically https://leanprover-community.github
#  .io/archive/stream/113489-new-members/topic/M1.20macs.html"
# fi

#############
# Utilities #
#############
abort() {
  printf "%s\n" "Aborted: $@"
  exit 1
}

continue() {
  printf "%s\n" "$@"
  read response
  while [ "$response" != "y" ]; do
    if [ "$response" = "n" ]; then
      abort "Script aborted"
    fi
    printf "%s\n" "$@"
    read response
  done
}

############################################
### Create virtual env?? First time only ###
############################################
# Back to deaduciton main dir
cd ../..
if [ -d pyinstaller_venv ]; then
  echo "Virtual env found in pyinstaller_env"
  FIRST_TIME = 0
else
  echo "Creating virtual env found in pyinstaller_env?"
  continue()
  python3 -m venv pyinstaller_venv
  FIRST_TIME = 1
############################
### Activate virtual env ###
############################
# From venv doc:
# Once you’ve created a virtual environment, you may activate it.
# On Windows, run:
# pyinstaller_env\Scripts\activate.bat
# On Unix or MacOS, run:
# source pyinstaller_env/bin/activate


echo "Activating pyinstaller virtual env"
if [ "$DEADUCTION_ON_LINUX" == 1 ]; then
  chmod a+x pyinstaller_env/bin/activate
  source pyinstaller_venv/bin/activate
elif [ "$DEADUCTION_ON_MAC" == 1 ]; then
  chmod a+x pyinstaller_env/bin/activate
  source pyinstaller_venv/bin/activate
else  # On Windows, run ???
  chmod a+x pyinstaller_env/Scripts/activate
  pyinstaller_env\Scripts\activate.bat

### Only first time: install pyinstaller ###
if [ $FIRST_TIME == 1 ]; then
  python3 -m pip install pyinstaller
  python3 -m pip install -r requirements.txt

### Environment variables ###
export DEADUCTION_DEV_MODE=0
export PYTHONPATH=/Users/leroux/Documents/PROGRAMMATION/LEAN/LEAN_TRAVAIL/dEAduction/src

### Main Pyinstaller instruction ###

# cd /Users/leroux/Documents/PROGRAMMATION/LEAN/LEAN_TRAVAIL/dEAduction/src
cd src

# From Pyinstaller doc:
# Note that when using venv, the path to the PyInstaller commands is:
#    Windows: ENV_ROOT\Scripts
#    Others: ENV_ROOT/bin
# Créer 4 variables : PYINSTALLER_PATH, DEADUCTION_MAIN, DEADUCTION_SHARE,
# DEADUCTION_LEANSRC

# This has been tested on Mac Os X.?? (NOT M1)
# Should be the same on Windows(?)
# Remove "--windowed" to see logs.
# Same should work on Linux, the "--windowed" option will be ignored.
pyinstaller deaduction/dui/__main__.py --onefile --windowed --clean --add-data deaduction/lean_src:deaduction/lean_src --add-data deaduction/share:deaduction/share

# —-name d∃∀duction --console
# --splash splashfile.png



### On MAC only: Create dmg ###
# https://github.com/create-dmg/create-dmg/blob/master/README.md
if [ $DEADUCTION_ON_MAC == 1 ]; then
  cd dist
  mv __main__ term_app/D∃∀DUCTION
# create-dmg D∃∀DUCTION.dmg term_app/
  create-dmg \
    --volname "D∃∀DUCTION installer" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --app-drop-link 600 185 \
  "D∃∀DUCTION-installer.dmg" \
  "term_app/"

#  --icon-size 100 \
#  --icon "Application.app" 200 190 \
#  --hide-extension "Application.app" \
#  --volicon "application_icon.icns" \
#  --background "installer_background.png" \
