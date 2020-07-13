"""
##############################################################
# logger module : configuration of the python logging module #
##############################################################

Author(s)      : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : July 2020

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

import logging
import sys

import deaduction.pylib.utils.ansiterm as ansiterm

############################################
# Logger classes
############################################
class Color_Formatter(logging.Formatter):
    """
    Python logging formatter to have some beautiful colors in terminal.
    """

    LEVELS_COLORS = {
        "DEBUG"    : ("off"     , "magenta"),
        "INFO"     : ("off"     , "blue"   ),
        "WARNING"  : ("bold"    , "yellow" ),
        "ERROR"    : ("bold"    , "red"    ),
        "CRITICAL" : ("reverse" , "red"    )
    }

    def __init__( self, format_ ):
        super().__init__( format_ )
        self._use_color = ansiterm.supports_color(sys.stdout)

    def format( self, record: logging.LogRecord ):
        """
        Formats the log record into a string

        :param record: the log record to format
        :return: a string with colors escape sequences if the terminal supports
                 it.
        """

        pref = "" # ANSI escape prefix
        suff = "" # ANSI escape suffix

        if self._use_color and record.levelname in self.__class__.LEVELS_COLORS:
            # Get colors info from config dict
            mode,fg = self.__class__.LEVELS_COLORS[record.levelname]

            # Configure prefix and suffix
            pref = ansiterm.txt_mode(mode=mode,fg=fg)
            suff = ansiterm.txt_reset()

        # Get message content from procedure in parent class.
        msg  = super().format(record) 

        return f"{pref}{msg}{suff}"

############################################
# Logger procedures
############################################
def configure( debug: bool = True ):
    """
    Configures the logging module for use with d∃∀duction.

    :param debug: enable debug messages
    """

    root = logging.getLogger("") # Get the root logger

    # Creating basic handler and format
    ft = Color_Formatter('%(asctime)-15s %(levelname)-9s: %(message)s')
    ft._use_color = True
    sh = logging.StreamHandler()
    sh.setFormatter(ft)

    root.addHandler(sh)

    # Set message level
    if debug: root.setLevel(logging.DEBUG)
    else    : root.setLevel(logging.INFO )

############################################
# Tests
############################################
