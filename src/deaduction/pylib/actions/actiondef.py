
import deaduction.pylib.logger as logger
import logging
import inspect
from dataclasses import dataclass


############################################
# Very high meta stuff
############################################
@dataclass
class Action:
    """
    Associates data to a specific action function.
    """
    caption:str
    run:any

def action(caption: str):
    """
    Decorator used to reference the function as an available action,
    plus creating the Action object containing the metadata.
    """
    # Get caller module object.
    # See https://stackoverflow.com/questions/1095543/get-name-of-calling-functions-module-in-python
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])

    def wrap_action(func):
        act = Action(caption,func)
        
        # Init the __actions__ object in the corresponding module if not
        # existing, then add the function object. Identifier is taken from
        # the function name.
        if not "__actions__" in mod.__dict__: mod.__actions__ = dict()
        mod.__actions__[func.__name__] = act

        return func

    return wrap_action 
