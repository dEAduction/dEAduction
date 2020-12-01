"""
# config.py : handle the configuration and the global variables
    
The configuration is stored in config.ini, IN THE SAME DIRECTORY

Use: from deaduction.config.config import user_config, Global
and then: allow_proof_by_sorry = user_config.getboolean('allow_proof_by_sorry')


Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 10 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""
import configparser
import logging
import os


log = logging.getLogger(__name__)

##################################################################
#               Setting cwd to src/deaduction                    #
# This assumes this file (config.py) is in src/deaduction/config #
##################################################################
deaduction_directory = os.path.join(os.path.dirname(__file__)) + '/../'
os.chdir(deaduction_directory)


################################
# A class for global variables #
################################
class Global:
    """
    all Python global vars should be given throught attrobutes of instances
     of this class
    Example if syntax =
    EXERCISE.PROPERTY_COUNTER
    """
    pass


EXERCISE = Global()  # class for global variables whose lifetime = exercise
EXERCISE.last_action = None
COURSE = Global()  # class for global variables whose lifetime = 1 course
SESSION = Global()  # class for global variables whose lifetime = a session

################################
# Reading configuration values #
################################
config = configparser.ConfigParser()

# reading file config.ini, assuming it is in the same directory as config.py
__config_file_path = os.path.join(os.path.dirname(__file__)) + '/config.ini'
config.read(__config_file_path)

# in case no config file is found
user_config = config['USER']


def write_config(field_name: str = None, field_content: str = None):
    with open(__config_file_path, 'w') as configfile:
        if field_name:
            user_config[field_name] = field_content
        config.write(configfile)