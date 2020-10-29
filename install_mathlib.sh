#!/bin/bash
################################################################################
# extract_mathlib_rev.py : Temporary script to extract mathlib revision number #
################################################################################
#
#    Note : this is dumb and will be removed as soon as the package system will
#    be running.
#
#Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
#Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
#Date           : October 2020
#
#Copyright (c) 2020 the dEAduction team
#
#This file is part of d∃∀duction.
#
#    d∃∀duction is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    d∃∀duction is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.

set -e # Exit on first error

###############################
# Utilities
###############################
exit_error() {
    echo "$1"
    exit 1
}

###############################
# Get mathlib revision
###############################

# Check for file
[ ! -f src/deaduction/leanpkg.toml ] && exit_error "src/deaduction/leanpkg.toml not found !"

# Get revision number
mathlib_rev=$(python3 tools/scripts/extract_mathlib_rev.py src/deaduction/leanpkg.toml)

echo ">> mathlib revision is ${mathlib_rev}"

###############################
# Download mathlib
###############################
pushd src/deaduction/

URL="https://oleanstorage.azureedge.net/mathlib/${mathlib_rev}.tar.xz"
echo ">> Download archive from $URL"
curl -o "mathlib.tar.xz" "${URL}"

###############################
# Extract to targets
###############################
echo ">> Extract to $(pwd)/share/mathlib folder"
mkdir -p "share/mathlib"
tar xaf "mathlib.tar.xz" -C "share/mathlib"
rm "mathlib.tar.xz"

popd
