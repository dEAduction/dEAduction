# CONTRIBUTING.md

## Git commit messages

Git commit messages follow the [Angular project convention](
    https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit
).

Commit types must be *one* of the following:

- **chores**: Changes that do not affect the source-code nor the tools (e.g.
  reorganize tree).
- **doc**: Add or modify project or code documentation.
- **feat**: Introduce a new feature.
- **fix**: Fix a bug.
- **ref::enhance**: Do not fix bugs or add features but enhance code.
- **ref::opti**: Do not fix bugs or add features but improve performances.
- **snippets**: Add or modify code in `/snippets/`.
- **style**: Format code, change its style but do not affect its meaning.
- **test**: Add or modify tests.
- **tools**: Changes that only affect tools (e.g. envconfig).

## Installing the development environment

- Required (min) python version : 3.7
- Required dependencies : pip, virtualenv, flake8

It is recommended to use a python virtualenv while programming to ensure that
you have the same environmenent as everyone involved in twiddling the code.

There is an `envconfig` file included in this repo. Its role is to :

* Create the virtualenvironment using the command `virtualenv --python=python3
  env` if it doesn't exists
* Activate this environment
* Install the required dependencies using pip :
 `pip3 install -r requirements.txt`
* Install/Update the git hooks
* Set the `PYTHONPATH` variable to include the `src` directory

When starting a developement session, be sure to use `source envconfig` to have
everything you need to start programming.

### Notes on IDE/text editor configuration

Configuration hints for some text editors/IDE are available under the `tools`
folder.

### Notes on linting

This project uses [flake8](https://flake8.pycqa.org/en/latest/) as linter ; we
follow [PEP8](https://www.python.org/dev/peps/pep-0008/) as much as possible,
but ignore the following points :

- E201 : whitespace after ‘(‘
- E202 : whitespace before ‘)’
- E203 : whitespace before ‘:’
- E221 : multiple spaces before operator

## Other code conventions

### Header docstrings

```python3 
"""
##################################
# <filename> : Short description #
##################################
    
    (optional long description)

Author(s)     : - Name <mail@website.com>
Maintainer(s) : - Name <mail@website.com>
Created       : June 2020 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""
```

### Function docstrings

```python3
def my_function(a: int, b: int) -> int:
    """ 
    Sum two numbers. Best function in the world !

    :param a: First number :param b: Second number :return: The sum of the two
    numbers
    """

    return a + b
```

Note that `:type:` and `:rtype:` aren't used here. This is because we don't use
Sphinx yet and it seems more readable like this. Type hinting is not mandatory,
use it if it seems relevant.

The first verb is in the imperative form, like for the conventional commit
convention.
