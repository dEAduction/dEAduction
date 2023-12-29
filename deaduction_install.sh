#!/bin/bash
set -u

# DEADUCTION INSTALLACTION SCRIPT
# INSPIRED BY HOMEBREW,
# https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh
# execute with:
# /bin/bash -c "$(curl -L https://raw.githubusercontent.com/dEAduction/dEAduction/master/deaduction_install.sh)"

# String formatters
tty_mkbold() { tty_escape "1;$1"; }
tty_underline="$(tty_escape "4;39")"
tty_blue="$(tty_mkbold 34)"
tty_red="$(tty_mkbold 31)"
tty_bold="$(tty_mkbold 39)"
tty_reset="$(tty_escape 0)"

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


unset HAVE_SUDO_ACCESS # unset this from the environment

have_sudo_access() {
  if [[ ! -x "/usr/bin/sudo" ]]
  then
    return 1
  fi

  local -a SUDO=("/usr/bin/sudo")
  if [[ -n "${SUDO_ASKPASS-}" ]]
  then
    SUDO+=("-A")
  elif [[ -n "${NONINTERACTIVE-}" ]]
  then
    SUDO+=("-n")
  fi

  if [[ -z "${HAVE_SUDO_ACCESS-}" ]]
  then
    if [[ -n "${NONINTERACTIVE-}" ]]
    then
      "${SUDO[@]}" -l mkdir &>/dev/null
    else
      "${SUDO[@]}" -v && "${SUDO[@]}" -l mkdir &>/dev/null
    fi
    HAVE_SUDO_ACCESS="$?"
  fi

  if [[ -z "${HOMEBREW_ON_LINUX-}" ]] && [[ "${HAVE_SUDO_ACCESS}" -ne 0 ]]
  then
    abort "Need sudo access (e.g. the user ${USER} needs to be an Administrator)!"
  fi

  return "${HAVE_SUDO_ACCESS}"
}

shell_join() {
  local arg
  printf "%s" "$1"
  shift
  for arg in "$@"
  do
    printf " "
    printf "%s" "${arg// /\ }"
  done
}

chomp() {
  printf "%s" "${1/"$'\n'"/}"
}

ohai() {
  printf "${tty_blue}==>${tty_bold} %s${tty_reset}\n" "$(shell_join "$@")"
}

warn() {
  printf "${tty_red}Warning${tty_reset}: %s\n" "$(chomp "$1")"
}

execute() {
  if ! "$@"
  then
    abort "$(printf "Failed during: %s" "$(shell_join "$@")")"
  fi
}


##########
# CHECKS #
##########

# Check old deaduction
if [ -d "$HOME".deaduction ]; then
  echo "(Deaduction has already been installed on this computer)"
  continue ">>>>> Do you want to proceed anyway? (y/n)"
fi

# Check bash
if [ -z "${BASH_VERSION:-}" ]; then
  abort "Bash is required to interpret this script."
fi

# Check if script is run non-interactively (e.g. CI)
# If it is run non-interactively we should not prompt for passwords.
if [[ ! -t 0 || -n "${CI-}" ]]; then
  NONINTERACTIVE=1
fi

# Check OS.
OS="$(uname)"
if [[ "$OS" == "Linux" ]]; then
  DEADUCTION_ON_LINUX=1
  VERSION=$(cat /etc/issue)
  if [[ ${VERSION::6} == "Ubuntu" || ${VERSION::6} == "Debian" ]]; then
    UBUNTU_DEBIAN=1
    echo "(Ubuntu or Debian detected, the envconfig_user_ubuntu file will be
     used)"
  else
    UBUNTU_DEBIAN=0
  fi

elif [[ "$OS" = "Darwin" ]]; then
  DEADUCTION_ON_LINUX=0
else
  abort "Deaduction works only on Linux and MacOs."
fi

# Machine hardware name
CPU="$(/usr/bin/uname -m)"
if [[ "$CPU" == "arm64" ]]; then
  warn "Brew has some issues on the new mac M1 (as of 06/21)"
  echo "which may affect gmp install"
  echo "see e.g. https://www.wisdomgeek.com/development/installing-intel-based-packages-using-homebrew-on-the-m1-mac/"
  echo "and specifically https://leanprover-community.github.io/archive/stream/113489-new-members/topic/M1.20macs.html"
fi

##########
# PYTHON #
##########
# Check the python and python3 commands, success if one refer
# to python ≥ 3.7
echo "Deaduction needs python ≥ 3.7"
if which python; then
  echo "python ->"
  python --version
  python -c 'import sys; exit(1) if (sys.version_info.major < 3 \
  or sys.version_info.minor < 7) \
  else exit(0)'
  if [ $? == 0 ]; then
    ohai "the command 'python' will work"
    #  CMD_PYTHON="python"
    #  echo "using python cmd"
  fi
else
  ohai "the command 'python' will not work"
fi

if which python3; then
  echo "python3 ->"
  python3 --version
  python3 -c 'import sys; exit(1) if (sys.version_info.major < 3 \
or sys.version_info.minor < 7) \
else exit(0)'
  if [ $? == 0 ]; then
    #    CMD_PYTHON="python3"
    #    echo "using python3 cmd"
    ohai "the command 'python3' will work"
  fi
else
  ohai "the command 'python3' will not work"
fi

echo ">>> Type the command that should be used to launch python"
echo ">>> or RETURN to abort (e.g. if you need to install or update python)"

# User's choice
read PYTHON_FOR_DEADUCTION
# Test this cmd:
`$PYTHON_FOR_DEADUCTION -c 'import sys; exit(1) if (sys.version_info.major < 3 \
or sys.version_info.minor < 7) \
else exit(0)'` &> /dev/null

if [ "$PYTHON_FOR_DEADUCTION" == "" -o $? == 1 ]; then
  warn "No python command or invalid python command given."
  echo "To install Python, please check"
  if [ "$DEADUCTION_ON_LINUX" == 1 ]; then
    echo "The following instructions should work (on Ubuntu/Debian):"
    echo "sudo apt update"
    echo "sudo apt install python3.7 (or posterior versions)"
    echo "See https://installpython3.com/linux/ for details"
  else
    echo "https://www.python.org/downloads/"
  fi
  abort ""
fi

echo "Python command: $PYTHON_FOR_DEADUCTION"


#################
# Brew (Mac OS) #
#################
if [ $DEADUCTION_ON_LINUX == 0 ]; then
  if which brew > /dev/null; then
    echo "(Found Homebrew... in case of problem try brew update?)"
    FOUND_BREW=1
  else
    echo "(Homebrew not found: see https://docs.brew.sh/Installation if needed)"
    FOUND_BREW=0
  fi

################
# gmp (Mac OS) #
################
  echo "Testing gmp (Gnu MultiPrecision, needed by Lean)"
  if [ $FOUND_BREW == 1 ]; then
    if brew info gmp &> /dev/null; then
      ohai "Found gmp !"
    else
      ohai "gmp not found"
      if [[ "$CPU" == "arm64" ]]; then
        echo "(WARNING: see above issue for brew and gmp on Mac M1)"
      fi
      abort "--> Try typing 'brew install gmp' and then rerun this script."
    fi
  elif [ -d /usr/local/Cellar/gmp ]; then
      echo "(/usr/local/Cellar/gmp found, should be OK)"
  else
      echo "gmp not found"
      # TODO: The following will NOT work on new Mac M1
      abort "--> Try installing Homebrew, then typing 'brew install gmp', and
      finally run this script again..."
  fi
fi

################################
# dEAduction dir already here? #
################################
if [ -d dEAduction ]; then
  echo "Directory dEAduction already exists,"
  echo "we will assume it contains dEAduction sources"
  echo "(If this is not the case then remove this directory and restart this script)"
  continue ">>>>> Proceed with install? (y/n)"
  DOWNLOADED=1
else
  DOWNLOADED=0
fi


#######
# git #
#######
if [ $DOWNLOADED == 0 ]; then
  if which git &> /dev/null; then
    ohai "Found git"
    FOUND_GIT=1
  else
    warning "git not found: see https://git-scm .com/book/fr/v2/D%C3%A9marrage-rapide-Installation-de-Git if needed"
    FOUND_GIT=0
    # TODO: handle git installation
    echo "If you want to use git to keep deaduction up-to-date,"
    echo "stop this script and install git, then launch this script again"
  fi

  if [ $FOUND_GIT == 1 ]; then
    echo "Do you want to use git to install deaduction? (y/n)"
    echo "(This is necessary for developers, and convenient for frequent updating)"
    read RESPONSE
    if [ "$RESPONSE" == "y" ]; then
      WITH_GIT=1
    elif [ "$RESPONSE" == "n" ]; then
      WITH_GIT=0
    else
      abort "Wrong answer. Try again."
    fi
  fi

  # TODO: choose location
  # TODO: tester si curl existe?

ohai "Deaduction will be installed inside a directory named 'dEAduction/'"
echo "in the current directory."
continue ">>>>> Proceed with download? (y/n)"

  ############
  # DOWNLOAD #
  ############
  if [ $WITH_GIT == 0 ]; then
    echo "Downloading zip archive..."
    mkdir tmp
    curl -L https://github.com/dEAduction/dEAduction/zipball/master/ --output tmp/deaduction.zip
    # Test zip archive
    if unzip -t tmp/deaduction.zip > /dev/null; then
      echo "(Zip archive is OK)";
    else
      abort "Corrupted zip archive. Try again."
    fi
    echo "Unzipping..."
    # Dirty solution to get dir name
    DIR_NAME=$(unzip -l tmp/deaduction.zip | head -n5 | tail -n1 | awk '{print $4}')
    unzip tmp/deaduction.zip
    rm tmp/deaduction.zip
    mv $DIR_NAME dEAduction
  else
    echo "Downloading with git..."
    git clone https://github.com/dEAduction/dEAduction.git
  fi
fi


# Deaduction content has been extracted to directory dEAduction
echo "Deaduction sources have been extracted in the directory dEAduction."
cd dEAduction


# Need sudo access from now on

#########################
# WRITING LAUNCH SCRIPT #
#########################
# The following will write a script with adequate name for the python cmd
# and store it in deaduction_launcher.sh

if [[ $UBUNTU_DEBIAN == 1 ]] ; then

  echo -e "#!/bin/bash

  # Necessary for envconfig_user:
  export PYTHON_FOR_DEADUCTION=$PYTHON_FOR_DEADUCTION
  export DEADUCTION_DIR=$(pwd)

  cd \$DEADUCTION_DIR
  source envconfig_user_ubuntu
  export PYTHONPATH=\$PYTHONPATH:\"$(pwd)/src\"
  cd src/deaduction

  $PYTHON_FOR_DEADUCTION -m dui" > ../deaduction_launcher.sh

  warn "Since you are on Ubuntu or Debian, We will now run the following commands:"
  ohai "apt install python3-venv python3-pip"
  ohai "pip3 install --upgrade setuptools"
  ohai "(or apt install python3-setuptools)"
  continue ">>>>> Proceed? (y/n)"

  ohai "apt install python3-venv python3-pip"
  execute "apt" "install" "python3-venv" "python3-pip"

  echo "We try both commands for installing setuptools:"
  ohai "pip3 install --upgrade setuptools"
  #  execute "pip3" "install" --upgrade" setuptools"
  pip3 install --upgrade setuptools

  ohai "apt install python3-setuptools"
  #  execute "apt" "install" "python3-setuptools"
  apt install python3-setuptools

else
  echo -e "#!/bin/bash

  # Necessary for envconfig_user:
  export PYTHON_FOR_DEADUCTION=$PYTHON_FOR_DEADUCTION
  export DEADUCTION_DIR=$(pwd)

  cd \$DEADUCTION_DIR
  source envconfig_user
  export PYTHONPATH=\$PYTHONPATH:\"$(pwd)/src\"
  cd src/deaduction

  $PYTHON_FOR_DEADUCTION -m dui" > ../deaduction_launcher.sh
fi

chmod u+x ../deaduction_launcher.sh

echo "You can now try to start deaduction by executing"
ohai "deaduction_launcher.sh"
echo "(This launcher file can be put anywhere,"
echo "e.g. in your Applications/ directory)"
echo "First execution will download Lean and the Mathlib,"
echo "and create a virtual env for Python (be patient...)"

