"""
###################
# Example logging #
###################

 Florian Dupeyron
 June 2020

 See :
    https://docs.python.org/fr/3/howto/logging-cookbook.html#logging-cookbook
    https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
"""

import logging
import ansiterm
from   copy import copy
import sys
import traceback

class Color_Formatter(logging.Formatter):
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

    def format( self, record ):
        pref = ""
        suff = ""

        if self._use_color and record.levelname in self.__class__.LEVELS_COLORS:
            mode,fg = self.__class__.LEVELS_COLORS[record.levelname]
            pref = ansiterm.txt_mode(mode=mode,fg=fg)
            suff = ansiterm.txt_reset()

        msg  = super().format(record)

        return f"{pref}{msg}{suff}"

# Creating basic handler and format
ft = Color_Formatter('%(asctime)-15s %(levelname)-9s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(ft)

logging.getLogger("").addHandler(sh) # Ajout du handler au root

log = logging.getLogger("test_logging")
log.setLevel(logging.DEBUG)

log.debug('This is debug mesage')
log.info('This is info message')
log.warning('This is warning message')
log.error('This is error message')
log.critical('This is critical message')

# Testing exception report
class My_Beautiful_Exception(Exception):
    def __init__( self, *args ):
        super().__init__(*args)
try:
    raise My_Beautiful_Exception("Coucou")
except My_Beautiful_Exception as e:
    log.error(f"An exception of type {e.__class__.__name__} has occured : {str(e)}")
    log.debug(traceback.format_exc())
