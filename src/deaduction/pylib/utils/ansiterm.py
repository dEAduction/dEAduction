"""
#################################################
# ansiterm.py : Managing ANSII escape sequences #
#################################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : April 2018, Revised July 2020

Copyright (c) 2020 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import io
from   typing import Optional,List,Any

###############################
# Configuration vars
###############################
colors_fg = {
    "black"   : "30",
    "red"     : "31",
    "green"   : "32",
    "yellow"  : "33",
    "blue"    : "34",
    "magenta" : "35",
    "cyan"    : "36",
    "white"   : "37",
    "orange"  : "202"
}

colors_bg = {
    "black"   : "40",
    "red"     : "41",
    "green"   : "42",
    "yellow"  : "43",
    "blue"    : "44",
    "magenta" : "45",
    "cyan"    : "46",
    "white"   : "47"
}

modes = {
    "off"        : 0,
    "bold"       : 1,
    "underline"  : 4,
    "blink"      : 5,
    "reverse"    : 7,
    "concealed"  : 8
}

###############################
# Routines
###############################
def command( cmd: str, values: List[Any] ) -> str :
    """
    Builds the ANSI escape sequence corresponding to the given cmd.

    :param cmd: the command to use
    :param values: arguments for the given command

    :return: A string containing the desired ANSI escape sequence.
    """
    ss  = "\033["
    ss += ";".join(map(lambda x:str(x), values))
    ss += cmd
    return ss

def supports_color( term: io.TextIOBase ) -> bool :
    """
    Checks if given file handle is a term, so that we can use pretty neat colors !

    :param term: the file we want to check, i.e. sys.stdout, sys.stderr
    :return: a boolean indicating if we can use color
    """
    is_a_tty = hasattr( term , 'isatty' ) and term.isatty()
    return is_a_tty


def txt_mode( mode: Optional[str] = None,
              fg  : Optional[str] = None,
              bg  : Optional[str] = None ) -> str:
    """
    Wrapper to build an ANSI escape sequence string.

    :param mode: the mode to choose, None to keep default
    :param fg: Foreground color name, None to keep default
    :param bg: Background color name, None to keep default
    :return: An Ansi escape sequence, ready to go, ready to rock !!!
    """

    cmd  = "m"
    args = []

    if mode: args.append( modes[mode]   )
    if fg  : args.append( colors_fg[fg] )
    if bg  : args.append( colors_bg[bg] )

    return command(cmd,args)

def txt_reset():
    """
    Returns the reset sequence

    :return: Reset ASCII sequence
    """
    return command("m",[modes["off"]])

