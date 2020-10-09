"""
# config.py : handling the configuration
    
The configuration is stored in config.ini, IN THE SAME DIRECTORY

Use: from deaduction.config.config import user_config
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

config = configparser.ConfigParser()

# reading file config.ini, assuming it is in the same directory as config.py
config_file_path = os.path.join(os.path.dirname(__file__)) + '/config.ini'
config.read(config_file_path)
user_config = config['DEFAULTS']
# FIXME: this should be set to config['USER'], but then DEFAULTS values
# are not taken into account ??

# in case no config file is found
try:
    user_config = config['DEFAULTS']
except KeyError:
    config['DEFAULTS'] = {'alert_target_solved':  True,
                          'fold_statements':      True,
                          'allow_proof_by_sorry': True
                          }
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)
    user_config = config['DEFAULTS']

if __name__ == "__main__":
    # boolean = user_config.getboolean('fold_statements')
    # text_boolean = user_config.get('fold_statements')
    # print(boolean, text_boolean)

    #####################
    # Print config file #
    #####################
    for sect in config.sections():
        print('Section:', sect)
        for k, v in config.items(sect):
            print(f' {k} = {v}')
