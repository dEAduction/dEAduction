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
from pathlib import Path


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

# config for temporary parameters
temp_config = configparser.ConfigParser()


#########
# utils #
#########
def add_to_recent_courses(course_path: Path,
                          course_type: str = '.lean',
                          title: str = "",
                          exercise_number: int = -1):
    """
    Add course_path to the list of recent courses in user_config
    NB: do not save this in config.ini; write_config() must be called for that
    """
    try:
        max = user_config['max_recent_courses']
    except KeyError:
        max = 5

    if course_type == '.pkl' and course_path.suffix == '.lean':
        course_path = course_path.with_suffix('.pkl')

    courses_paths, courses_titles, exercises_numbers = get_recent_courses()
    # log.debug(f"Recent courses paths: {courses_paths}")
    # log.debug(f"Adding path: {course_path}")
    if course_path in courses_paths:
        # We want the course to appear exactly once, and in pole position
        # 0 = newest, last = oldest
        n = courses_paths.index(course_path)
        courses_paths.pop(n)
        courses_titles.pop(n)
        exercises_numbers.pop(n)
    courses_paths.insert(0, course_path)
    courses_titles.insert(0, title)
    exercises_numbers.insert(0, exercise_number)

    if len(courses_paths) > max:
        # Remove oldest
        courses_paths.pop()
        courses_titles.pop()
        exercises_numbers.pop()

    # Turn each list into a single string
    courses_paths_strings = [str(path) for path in courses_paths]
    courses_paths_string   = ','.join(courses_paths_strings)
    courses_titles_string = ','.join(courses_titles)
    exercises_numbers_string = ','.join(map(str, exercises_numbers))
    user_config['recent_courses'] = courses_paths_string
    user_config['recent_courses_titles'] = courses_titles_string
    user_config['exercise_numbers'] = exercises_numbers_string

    # Save config file
    write_config()


def get_recent_courses() -> ([Path], [str], [int]):
    """
    Return the list of (recent course, title) found in the user_config dict
    """

    try:
        recent_courses  = user_config['recent_courses']
    except KeyError:
        recent_courses  = ""
    try:
        titles    = user_config['recent_courses_titles']
    except KeyError:
        titles    = ""
    try:
        numbers    = user_config['exercise_numbers']
    except KeyError:
        numbers    = ""

    if recent_courses:
        recent_courses_list = recent_courses.split(',')
        courses_paths = list(map(Path, recent_courses_list))
        courses_titles = titles.split(',')
        exercises_numbers = [-1] * len(recent_courses_list)
    else:
        courses_paths = []
        courses_titles = []
        exercises_numbers = []

    if exercises_numbers:
        try:
            exercises_numbers = list(map(int, numbers.split(',')))
        except ValueError:
            pass
    return courses_paths, courses_titles, exercises_numbers


def write_config(field_name: str = None, field_content: str = None):
    with open(__config_file_path, 'w') as configfile:
        if field_name:
            user_config[field_name] = field_content
        config.write(configfile)
