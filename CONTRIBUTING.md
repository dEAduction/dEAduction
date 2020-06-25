# CONTRIBUTING.md

## git commit

The convention used here for `git commit` is heavily inspired from the [Angular project convention](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit).

### Type

The type of the commit **must** be one of the following:

- **docs**: documentation only changes ;
- **feat**: a new feature ;
- **fix**: a bug fix ;
- **perf**: a code change that improves performance ;
- **refactor**: a code change that neither fixes a bug nor adds a feature ;
- **snippets**: adding or modifying code in `snippets/` ;
- **style**: changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc) ;
- **test**: adding missing tests or correcting existing tests.

## Installing the development environment

- Required (min) python version : 3.7
- Required dependencies : pip, virtualenv, flake8

It is recommended to use a python virtualenv while programming to ensure that
you have the same environmenent as everyone involved in twiddling the code.

There is an `envconfig` file included in this repo. Its role is to :

* Create the virtualenvironment using the command `virtualenv --python=python3 env` if it doesn't exists
* Activate this environment
* Install the required dependencies using pip : `pip3 install -r requirements.txt`
* Install/Update the git hooks
* Set the `PYTHONPATH` variable to include the `src` directory

When starting a developement session, be sure to use `source envconfig` to have
everything you need to start programming.

### Notes on IDE/text editor configuration

Configuration hints for some text editors/IDE are available under the `tools` folder.

### Notes on linting

This project uses [flake8](https://flake8.pycqa.org/en/latest/) as linter ; we
follow [PEP8](https://www.python.org/dev/peps/pep-0008/) as much as possible,
but ignore the following points :

- Multiple spaces around operators are allowed for alignment (E221)
