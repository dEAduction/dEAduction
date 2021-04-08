# Contributing to d∃∀duction

Hello and welcome! Contributing to d∃∀duction is the best way to help. We are a
small team, we don't know what we are doing. We made d∃∀duction free software so
that everybody can access the codebase and participate! This document aims to
explain what you can do, how you can do it and what you can expect. Feel free
to suggest any modification.

#### Table of contents

* [Get started](#get-started)
   * [Overview](#overview)
   * [What you should know](#what-you-should-know)
* [Contributing](#contributing)
   * [What you can do](#what-you-can-do)
   * [Contribution process](#contribution-process)
   * [What you can expect](#what-you-can-expect)
   * [Setting up the development environment](#setting-up-the-development-environment)
* [Guidelines](#guidelines)
   * [Code documentation](#code-documentation)
      * [Function and method signatures](#function-and-method-signatures)
      * [Function and method docstrings](#function-and-method-docstrings)
      * [Class docstrings](#class-docstrings)
      * [Comment style](#comment-style)
   * [File headers](#file-headers)
   * [Git branch names](#git-branch-names)
   * [Git commit messages](#git-commit-messages)
      * [Specifications (non-merge commits)](#specifications-non-merge-commits)
      * [Specifications (merge commits)](#specifications-merge-commits)
      * [Examples](#examples)
   * [Python code (modified PEP 8) and linting](#python-code-modified-pep-8-and-linting)
      * [Consecutive lines with = operators](#consecutive-lines-with--operators)
      * [Import statements](#import-statements)
* [Resources (bonus)](#resources-bonus)
   * [For Git](#for-git)
   * [For L∃∀N](#for-ln)
   * [For PySide2 / Qt for Python](#for-pyside2--qt-for-python)
   * [For Python (version 3)](#for-python-version-3)
   * [For Trio and QTrio](#for-trio-and-qtrio)
   * [On free software](#on-free-software)

## Get started

### Overview

The d∃∀duction project has two repositories:
[deaduction](https://github.com/dEAduction/dEAduction) (Python source code and
tools) and [deaduction-lean](https://github.com/dEAduction/dEAduction-lean)
(L∃∀N code and exercise files). To learn more about each directory, module or
file, simply open its `__init__.py` or `README.md`.

d∃∀duction is written in Python3 and [L∃∀N](https://leanprover-community.github.io/)
(a proof assistant). The graphical
interface uses PySide2 (Qt for Python). Communication between the user
interface and L∃∀N uses Trio and Qtrio. The version control system we use is
Git.

### What you should know

Not much. A good experience in Python3 is *recommended*, as well as basic
terminal usage. Some experience in Git is *necessary* but you can rapidly learn
it from scratch (you should feel at ease using git branches). L∃∀N experience
is only useful for the L∃∀N side of the project. **You do not need to be a
programming wizard to contribute**! In the core-team, nobody is.

A [list](#resources-bonus) of online resources is available at the end of this
document.

## Contributing

### What you can do

Preferably consider working on an existing
[issue](https://github.com/dEAduction/dEAduction/issues) (check-out issue
labels). If you decide to do so, write a comment so we can talk about it. For
instance, you could contribute to work-in-progress [new
features](https://github.com/dEAduction/dEAduction/issues?q=is%3Aopen+is%3Aissue+label%3A%22type%3A%3Anew+feature%22).
If you would rather do something else, start by opening an issue so we can
discuss it. Here are contribution ideas, in order of priority:
- **Refactor code**: we really need help on that. d∃∀duction needs a strong
  codebase and as of now it is rather weak.
- **Report stuff, suggest improvements**: report bugs, suggest new features,
  fundamental changes, enhancements…
- **Translate the user interface**.
- **Write documentation**: many modules, classes or functions still lack
  documentation ; you can contribute to its elaboration or to the d∃∀duction
  user manual.
- **Create exercises**.

In any case, each contribution should have its own issue. Please note that to
avoid wasting your time, you should never work on a contribution that hasn't
been discusses with us.

> Issues that are best-suited for first contributions have the label [`good
first issue`](https://github.com/dEAduction/dEAduction/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22).

Finally, please respect the [contribution guidelines](#guidelines) for code,
commit messages, etc.

### Contribution process

To contribute, you first need to
[fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo)
d∃∀duction repository and create a new git branch (see branches
[guidelines](#git-branch-names), do *not* develop on the `master` branch) for
your contribution (do not use a branch for more than one thing).

> At this point, your fork and the d∃∀duction repository are two distinct
  projects.

When you think your contribution is ready, git push it to your online fork.
Then let us know about it in the issue; core-team members will review your
contribution proposal. After potential modifications and approval, do a [*pull
request*](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests)
for your contribution to be integrated into d∃∀duction's codebase.

You should feel free to discuss the advancement of your contribution with us at
any point. (This should be done publicly, in the issue of the contribution.)

### What you can expect

If you follow these steps, your contribution proposition should be approved!
You will then be credited as a d∃∀duction's contributor. Nevertheless,
respecting the above stages does not guarantee that your contribution proposal
will necessarily be accepted.

### Setting up the development environment

In order to contribute, it is necessary to set-up the d∃∀duction's development
environment. It includes a Python virtual environment, a Python linter (file
[`.flake8`](.flake8)), git hooks, environment variables, etc. To set it up and
make sure every dependency is up to date, open a terminal in the repository's
root and run the following command:

```bash
source envconfig
```

This should add `(env)` in front of your terminal prompt. It is *highly*
recommended to set up the development environment at the very beginning of
every development session, otherwise the code will not run.


## Guidelines

### Code documentation

As will be shown in this section, the d∃∀duction's code documentation may be
long to write and needs be to maintained when the code is changed. But **the
documentation is as essential as the code**. It might prove useless for the
author but it is essential for any person discovering your code. As Guido said,
*code is read much more often than it is written*. When writing documentation,
you should always assume that the reader is not familiar with your code and has
very little time and skill to understand it. The writer should do most of the
work, so that the reader can efficiently understand the essence and utility of
the code in one reading. Documentation should not only tell what a piece of
code does, but also why it exists, why it is necessary, where it is used and
how, and provide examples if needed.

#### Function and method signatures

All functions and methods *must* be
[annotated](https://www.python.org/dev/peps/pep-3107/#syntax), using the
[`typing` module](https://docs.python.org/3/library/typing.html) if necessary.
For example, this is correct:

```python3
def factorial(n: int) -> int:
    return 1 if n == 1 else n * factorial(n - 1)
```

but this is not:

```python3
def factorial(n):
    return 1 if n == 1 else n * factorial(n - 1)
```

#### Function and method docstrings

All functions and methods *must* have a
[docstring](https://www.python.org/dev/peps/pep-0257/). Function and method
docstrings *must* have the following format:

```python3
"""
Summary (what does it do, why is it useful, why is it there, why should we not
delete it).

:param param_1: description of param_1
:param param_2: description of param_2
…
:param param_n: description of param_n
:return: what does it return (if applicable)
"""
```

[Here](https://github.com/dEAduction/dEAduction/tree/master/src/deaduction/dui/stages/start_coex/start_coex_widgets.py)
are a few examples.


#### Class docstrings

All functions and methods *must* have a
[docstring](https://www.python.org/dev/peps/pep-0257/). Class docstrings follow
the same rules as function and method docstrings, except that public class
attributes must be written in the class docstring using a `:attribute
attribute_name: Attribute description` syntax.
[Here](https://github.com/dEAduction/dEAduction/tree/master/src/deaduction/dui/stages/exercise/exercise_main_window.py)
are a few examples.

#### Comment style

Comments also follow the [PEP 8 convention (¶
Comments)](https://pep8.org/#comments). If the result is not bloated, you may
use the *section comments*:

```python3
###################
# Section comment #
###################
```

and *separator comments*:

```python3
# ──────────────── Separator comment ─────────────── #
```

Both those types of comments *must* have a blank line just before and right
after them. They are good for titles but bad for explanations so be as succinct
as possible.

> If you use Vim, consider using the addon
[UltiSnips](https://github.com/sirver/UltiSnips) to efficiently add headers.
Ready-to-use snippets are available in
[`tools/Vimconfig/UltiSnips/python.snippets/deaduction.snippets`](https://github.com/dEAduction/dEAduction/tree/master/tools/Vimconfig/UltiSnips/python.snippets/deaduction.snippets).

### File headers

File headers *must* have the following structure:

```python3 
"""
##################################
# <filename> : Short description #
##################################
    
    (optional long description)

Author(s)    : - Name <mail@website.com>
Maintainer(s): - Name <mail@website.com>
Created      : Creation date (DD month YYYY)
Repo         : https://github.com/dEAduction/dEAduction

Copyright (c) Year the dEAduction team

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

See
[example](https://github.com/dEAduction/dEAduction/tree/master/src/deaduction/dui/stages/missing_dependencies/missing_dependencies_dialogs.py).
Non Python files *must* also have this header, simply get rid of the doctring
`"""` marks.

> If you use Vim, consider using the addon
[UltiSnips](https://github.com/sirver/UltiSnips) to efficiently add headers.
Ready-to-use snippets are available in
[`tools/Vimconfig/UltiSnips/python.snippets/deaduction.snippets`](https://github.com/dEAduction/dEAduction/tree/master/tools/Vimconfig/UltiSnips/python.snippets/deaduction.snippets).

### Git branch names

Branch names *must* have the following structure:

```
area::type/name
```

Arguments `area` and `type` (both mandatory) follow the same
[rules](#git-commit-messages) as the git commit message. Argument `name`
(mandatory) is a description of what you are doing on this branch. It should be
as short as possible and words must be separated by a hyphen (-). Use lower
case.

> A branch should host a *single* new feature, fix, etc.

### Git commit messages

> This convention is strongly inspired from the Angular project Commit
Message Format
[guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit).

#### Specifications (non-merge commits)

Commit messages consist of a header (mandatory) and a body (optional). The
commit header is what you put in between the quotation marks in the command
`git commit -m ""`. The body is everything that comes after the header (a blank
line), it doesn't have a specific structure. Most commit messages only have a
header, which *must* have the following structure:

```
area::type(scope): Summary
```

Argument `area` (mandatory) *must* be one of:

`area`     | Definition
-----------|-----------------------------------------------------------------------------------------------------------------------
`code`     | Changes affecting the codebase.
`doc`      | Changes affecting the documentation (including comments and docstrings).
`dui`      | Changes affecting only d∃∀duction's user interface (e.g. texts, tooltips) but have nothing to do with the code itself.
`other`    | Changes that do not go in any other category, please avoid using it.
`snippets` | Changes affecting the snippets.
`tests`    | Changes affecting the tests.
`tools`    | Changes affecting the tools and the development environment.

Argument `type` (mandatory) *must* be one of:

`type`   | Definition
---------|------------------------------------------------------------------------------------------------------------------------------------------------------------
`chores` | Changes not affecting the meaning of what is changed (e.g. changing a filename).
`dev`    | Work in progress for new features; changes that are part of its development though not introducing it. A series of `dev` commits ends with a `feat` commit.
`feat`   | Introduce a completed new feature. When developing it, the last commit *must* be the only one to use this type, all other *must* use dev.
`fix`    | Fix bugs and problems.
`ref`    | Refactoring.
`revert` | Revert to a previous commit, feature or state of the project.

Scope (optional) is the precise part of the codebase that was changed (e.g. a
class, function or module name or a combination of all that). Precision is up
to you. The summary (mandatory) should be the shortest possible sentence
describing the commit. It should begin with a capital letter and *must not*
end with a period, it should also be written using present tense.

The body of the commit message may be used to provide additional information
about the changes, such as technical explanations.

#### Specifications (merge commits)

Merge commit messages have a different structure:

```
merge: repoA/branchA -> repoB/branchB
```

where `repoA` and `repoB` are remote names (if one of them is a copy on your
own computer, use `local`) and the merge is from `branchA` to `branchB`.

#### Examples

If you finished writing the first part of the function `my_function`, but this
function is not ready, you should use the type `dev`. Since this function is
part of the codebase, you must use the area `code`. Here is an example of a
good commit message:

```
code::dev: Finish first part of my_function
```

However you can be more precise by using a scope. If the function is part of
the module `dui.utils`, this commit message is better:

```
code::dev(dui.utils): Finish first part of my_function
```

If you fixed the script `envconfig` (the one that sets up the virtual
environment), the header (we leave it to you to imagine a summary) should be:

```
tools::fix(envconfig):
```

Now if you wish to merge the branch `dev/the_new_feature` from Github (repo's
name is `origin`) to your computer, the commit message *must* be:

```
merge: origin/dev/the_new_feature -> local/dev/the_new_feature
```

and if you want to merge the branch `the_new_feature` with the branch `master`
on your computer, the commit message *must* be:

```
merge: local/dev/the_new_feature -> local/master
```

Please note that any non-compliant commit message will be rejected by the git
hook.

### Python code (modified PEP 8) and linting

The Python code of d∃∀duction follows the [PEP 8 convention](https://pep8.org),
with the adjustments hereinafter. You should check your Python code syntax
using the project's
[linter](https://sourcelevel.io/blog/what-is-a-linter-and-why-your-team-should-use-it),
that is a slightly modified [flake8](https://flake8.pycqa.org/en/latest/#)
version. To lint your Python module, simply run the terminal command:

```bash
flake8 my_module.py
```

> Be sure to have the development environment properly [set
  up](#setting-up-the-development-environment) and to be in the Python virtual
  environment.

> If you use Vim, consider using the addon
[ALE](https://github.com/dense-analysis/ale) to have an integrated linter.

#### Consecutive lines with `=` operators

Occurrences of `=` operator on a series of consecutive non blank lines *must* be
vertically aligned. Example:

```python3
my_int             = 10
my_string          = 'd∃∀duction'
my_bigger_variable = 'Code is read much more often than it is written.'

other_int    = 2
other_string = 'free software'
```

#### Import statements

As PEP 8 states, imports should be grouped in the following order:
1. standard library imports,
2. related third party imports,
3. local application/library specific imports.

Items in a given `import` statement *must* be on different lines, vertically
aligned, alphabetically ordered.

```python3
from my_module import (MyClass,
                       MyOtherClass,
                       this_function)
```

[Here](https://github.com/dEAduction/dEAduction/tree/master/src/deaduction/dui/stages/exercise/exercise_main_window.py)
are a few examples.

Relative imports may be used in some cases (avoid them as much as you
possibly can); they follow the same rules as regular imports and *must* be
grouped after the last group of regular imports and a blank line.

## Resources (bonus)

### For Git

- The [official documentation](https://git-scm.com/doc).
- The (free) book [*Pro Git*](https://git-scm.com/book/en/v2), complete and
    rigorous, a short way of becoming proficient in Git.

### For L∃∀N

- The [official documentation](https://leanprover.github.io/documentation/).
- The [Lean and mathlib community page](https://leanprover-community.github.io/), a good starting point.
- The [Natural number
    game](https://wwwf.imperial.ac.uk/%7Ebuzzard/xena/natural_number_game/) to
    learn L∃∀N by using it, no experience needed.

### For PySide2 / Qt for Python

- The [official
    documentation](https://doc.qt.io/qtforpython/quickstart.html).
- This excellent [tutorial](http://zetcode.com/gui/pyqt5/), perfect if you want
    to learn from scratch. (To make it work, simply replace all occurences of
    `PyQt5` by `PySide2`; there are some other minor problems but you should
    manage.)

### For Python (version 3)

- The [official documentation](https://docs.python.org/3/).

There are dozens of online tutorials. If you are new to Python, be sure to
choose one which covers classes (with heritage and usual decorators).

- The [zen of Python](https://www.python.org/dev/peps/pep-0020/#the-zen-of-python).
- A [guide](https://realpython.com/python-virtual-environments-a-primer/) to
    virtual environments.
- Python properties, [how tu use them and
    why](https://www.programiz.com/python-programming/property), this is
    definitely worth reading if you want to Python the
    [pythonic](https://en.wiktionary.org/wiki/Pythonic) way. Properties make
    the code stronger and nicer to read. Unfortunately, we did not use them
    enough in the codebase, but you should still do it if relevant.
- Python [thematic tutorials from ZetCode](https://zetcode.com/all/#python) are
    always great.

### For Trio and QTrio

- Trio's [official documentation](https://trio.readthedocs.io/en/stable/).
- QTrio's [repository](https://github.com/altendky/qtrio).

### On free software

- GNU's article [What is free
    software?](https://www.gnu.org/philosophy/free-sw.html) covers the basics
    in a rigourous way.
- The page [How to Contribute to Open
    Source](https://opensource.guide/how-to-contribute/) is a great
    introduction to free software in practice if you have never contributed
    before.
