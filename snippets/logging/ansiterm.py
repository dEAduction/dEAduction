"""
######################################
# Simple ANSI Escape codes utilities #
######################################
  
  Florian Dupeyron (floolfy) <florian.dupeyron@mugcat.fr>
  Around April 2018 ?

<license>
"""

import sys
from   typing import Optional

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
    "white"   : "37"
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
def command( cmd, values ) -> str :
    ss  = "\033["
    if values:
        ss += str( values[0] )
        for e in values[1:]:
            ss += ";" + str( e )
    
    ss += cmd
    return ss

def supports_color( term ) -> bool :
    """
    Checks if given file handle is a term, so that we can use pretty neat colors !
    """
    is_a_tty = hasattr( term , 'isatty' ) and term.isatty()
    return is_a_tty


def txt_mode( mode : Optional[str] = None,
              fg   : Optional[str] = None,
              bg   : Optional[str] = None ) -> str:
    """
    Builds an ASCII escape string

    :param mode: the mode to choose, None to keep default
    :param fg: Foreground color name, None to keep default
    :param bg: Background color name, None to keep default
    :return: An ANSI escape sequence
    """

    cmd  = "m"
    args = []

    if mode : args.append( modes[mode]   )
    if fg   : args.append( colors_fg[fg] )
    if bg   : args.append( colors_bg[bg] )

    return command(cmd,args)

def txt_reset():
    """
    Returns the reset sequence

    :return: Reset ASCII sequence
    """
    return command("m",modes["off"])

