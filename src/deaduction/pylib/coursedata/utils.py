"""
# utils.py : <#ShortDescription> #
    
    <#optionalLongDescription>

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 11 2020 (creation)
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
import logging
log = logging.getLogger(__name__)


def find_suffix(string, list):
    """
    return the number of items in a list of strings that ends with the given,
    and the index of the first matching item
    :param string:
    :param list:
    :return:
    """
    total = [item for item in list if item.endswith(string)]
    nb = len(total)
    index = -1
    if nb > 0:
        index = list.index(total[0])
    return index, nb


def separate(string) -> []:
    """like split but allows space or comma as separators"""
    if not isinstance(string, str):  # already split or substituted
        return string
    if string.count(","):
        list_ = string.split(",")
    else:
        list_ = string.split()
    return [item.strip() for item in list_]


def substitute_macros(string: str, macros: {}) -> str:
    """ Recursively substitute, in string, keys of macro with their values,
    if the values are strings
    """
    for macro_name in macros:
        if isinstance(macros[macro_name], str):
            new_string = ""
            macro_string = macros[macro_name]
            macro_name2 = '$' + macro_name
            if string.count(macro_name2):
                macro_name = macro_name2
            if string.count(macro_name):  # found macro_name in string
                n = string.find(macro_name)
                if string[n-1] == '-':  # minus !
                    macro_list = separate(macro_string)
                    macro_string = " -".join(macro_list)
                    # NB : we keep the preceding minus...
                new_string = string.replace(macro_name, macro_string)
    if new_string:
        log.debug(f"changed {string} into {new_string}")
        return substitute_macros(new_string, macros)
    else:  # no macro found
        return string


def extract_list(string: str, macros: {}, search: callable) -> list:
    """
    for each word in string,
     add search(word) in the list,
     or remove it from the list if word begins by '-'

     search is a callable that returns a list of items
     (in practice, items will be instances of Action or Statement)
    """
    final_list = []
    initial_list = separate(string)
    for word in initial_list:
        remove = False
        diff_list = None
        # (1) add or remove?
        if word.startswith('-'):
            remove = True
            word = word[1:]
        elif word.startswith('+'):
            word = word[1:]
        # (2) macro?
        word1 = '$' + word
        if word1 in macros:
            word = word1
        if word in macros:
            diff_list = (macros[word])
        else:  # find word
            diff_list = search(word)
            if diff_list is None:
                diff_list = search(word1)  # word could still be a
                                           # pre-defined macro , e.g. *ALL
        if diff_list is not None:
            if remove:
                for item in diff_list:
                    if item in final_list:
                        log.debug(f"removing {len(diff_list)} item(s)")
                        final_list.remove(item)
            else:
                log.debug(f"adding {len(diff_list)} item(s)")
                final_list.extend(diff_list)
        else:
            log.warning(f"Found no item for {word} in metadata")

    return final_list
