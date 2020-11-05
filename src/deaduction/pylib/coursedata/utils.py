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
            if string.count(macro_name):  # found macro_name in string
                new_string = string.replace(macro_name, macros[macro_name])
            if string.count('$' + macro_name):
                new_string = string.replace('$' + macro_name, macros[
                                            macro_name])
    if new_string:
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
        if '$' + word in macros:
            word = '$' + word
        if word in macros:
            diff_list = (macros[word])
        else:  # find word
            diff_list = search(word)
            if diff_list is None:
                diff_list = search('$' + word)  # word could still be a
                                           # pre-defined macro
        if diff_list:
            if remove:
                for item in diff_list:
                    if item in final_list:
                        final_list.remove(item)
            else:
                final_list.extend(diff_list)
        else:
            log.warning(f"Found no item for {word} in metadata")

    return final_list




def substitute_macros_old(list_: [], macros: {}) -> []:
    """recursively replace macros in list by their value"""
    for macro_name in macros:
        n = None
        if list_.count(macro_name):  # found macro_name in list_
            n = list_.index(macro_name)
        if list_.count('$' + macro_name):
            n = list_.index('$' + macro_name)
        if n is not None:  # replace macro_name with
            list_.pop(n)
            list_insert(list_, n, macros[macro_name])
            return substitute_macros(list_, macros)  # recursion

    # no macro found:
    return list_


def list_arithmetic(list_: [str]) -> [str]:
    """
    perform "arithmetic" n list_, e.g.
[banane, pomme, -banane]  -> [pomme]
    """
    list_2 = []
    for item in list_:
        if item.startswith('+'):
            list_2.append(item[1:])
        elif item.startswith('-'):
            item = item[1:]
            if list_2.count(item):
                list_2.remove(item)
            else:
                log.warning(f"No {item} found in {list_}")
        else:
            list_2.append(item)

    return list_2


def extract_list_old(names: [str], search: callable) -> iter:
    """
    replace each name by its value in the dictionary
    """
    list_ = map(lambda name: search(name), names)
    return list_


def list_insert(list_: [], n: int, macro_value):
    """
    insert the list macro_value in list_ at position n

    macro_value is either a list, or a string that has to be split
    """
    macro_value = separate(macro_value)  # make sure macro_value is a list
    counter = 0
    for item in macro_value:
        list_.insert(n+counter, item)
        counter += 1  # insert in the right order


