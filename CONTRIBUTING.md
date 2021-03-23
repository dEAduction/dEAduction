# Contributing to d∃∀duction

Hello and welcome! Contributing to d∃∀duction is the best way to help. Since it
free software : everybody can access to the code-base and participate! We are a
small team of dumb devs, we don't know what we're doing. This document tells
you what you can do, how you can do it and what to expect. Feel free to suggest
any modification.

#### Table of contents

* [Get started](#get-started)
   * [Overview](#overview)
   * [What should I know?](#what-should-i-know)
* [Contributing](#contributing)
   * [What do?](#what-do)
   * [Contribution process](#contribution-process)
   * [What to expect?](#what-to-expect)
   * [Setting-up the development environment](#setting-up-the-development-environment)
* [Guidelines](#guidelines)
   * [Code documentation](#code-documentation)
      * [Functions and methods signatures](#functions-and-methods-signatures)
      * [Functions and methods docstrings](#functions-and-methods-docstrings)
      * [Classes docstrings](#classes-docstrings)
      * [Comments style](#comments-style)
   * [Python file headers](#python-file-headers)
   * [Git commit messages](#git-commit-messages)
      * [Specifications](#specifications)
      * [Examples](#examples)
   * [Git branch names](#git-branch-names)
   * [Python code (modified PEP 8) and linting](#python-code-modified-pep-8-and-linting)
      * [Consecutive lines with = operators](#consecutive-lines-with--operators)
      * [Import statements](#import-statements)
* [Resources (bonus)](#resources-bonus)
   * [For Python (version 3)](#for-python-version-3)
   * [For L∃∀N](#for-ln)
   * [For PySide2 / Qt for Python](#for-pyside2--qt-for-python)
   * [For Trio and QTrio](#for-trio-and-qtrio)
   * [For Git](#for-git)
   * [On free software](#on-free-software)


## Get started

### Overview

The d∃∀duction project has two repositories:
[deaduction](https://github.com/dEAduction/dEAduction) (Python source code and
tools) and [deaduction-lean](https://github.com/dEAduction/dEAduction-lean)
(L∃∀N code and exercises files). To know more about each directory, module or
file, simply open its `__init__.py` or `README.md`.

d∃∀duction is written in Python3 and L∃∀N (a proof assistant). The graphical
interface uses PySide2 (Qt for Python) and communication between the user
interface and L∃∀N uses Trio and Qtrio. The version control system we use is Git.

### What should I know?

Not much. A good experience in Python3 is *recommended*, as well as basic
terminal usage.  Some experience in Git is necessary but you can rapidly learn
it from scratch (you should feel at ease using git branches). L∃∀N experience
is useful only if you directly work on the L∃∀N side of the project, otherwise
you do not need it. Finally, **you do not need to be a programming wizard to
contribute**. In fact, nobody is in the core-team. You just need to know the
things that are relevant to *you* and what you want to do.

A [list](#resources-bonus) of online resources is available at the end of this
document. They do not cover everything but are all useful to this project. Do
not read them if you do not need or want to. 



## Contributing

### What do?

Consider working on an existing issue
[issue](https://github.com/dEAduction/dEAduction/issues); if you want to
develop a new feature, open an issue first so we can discuss it. If you chose
to work on an issue, reply to it first so we can discuss more precisely how we
work together. Otherwise, here are new-issue contribution ideas, in order of
preference:
- **Refactor code**: yeah, please help us. d∃∀duction needs a strong code-base
    and as of now it is rather weak.
- **Report stuff**: bugs, refactoring suggestions, user interface suggestions,
    new features proposals, etc.
- **Translate user interface**.
- **Write documentation**: many modules, classes or functions are undocumented,
    but they should be. You can also contribute to d∃∀duction's user manual.
    Contributions and feed-back to *this* document would also be very much
    appreciated.
- **Create exercises**.

In any case, every contribution proposition should have its issue, whether we
or you created it. To save you time, you should never work on a contribution
which was not approved (there would be a risk of it being rejected)!

> Issues that are best-suited for first contributions have the label [`good
first issue`](https://github.com/dEAduction/dEAduction/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22).

> Beware of the [contribution guidelines](#guidelines) for code, commit
messages, etc.

### Contribution process

To contribute, you first need to
[fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo)
d∃∀duction's repository and create a new branch (see branches
[guidelines](#git-branch-names) for your contribution (do not use a branch for
more than one thing). You can begin development on this branch. At this point,
your fork and d∃∀duction's repository are two distinct projects.

When you think your contribution is ready, git push it to your online fork.
Signal it in the contribution proposition's Github issue so we can review it,
discuss it and test it; it will be labeled with [`status::ready for
review`](https://github.com/dEAduction/dEAduction/issues?q=is%3Aopen+is%3Aissue+label%3A%22status%3A%3Aready+for+review%22+).
After potential modifications and if we approve your contribution, we will tell
you that your contribution is ready for pull-request! At that point, your issue
is labeled with [`status::ready for
PR`](https://github.com/dEAduction/dEAduction/issues?q=is%3Aopen+is%3Aissue+label%3A%22status%3A%3Aready+for+PR%22+);
you just do the pull request and we accept it.

Notes:
- Do *not* do your modifications directly on the `master` branch.
- Remember to commit often; in doubt commit. On top of that, keep your fork
  up-to-date with upstream (that is, with d∃∀duction's branch you forked from).
- At any stage, do feel free to discuss your contribution's development with
  the core team. This should be done publicly, in the contribution
  proposition's issue.

> This section is a basic outline of the contribution process. If you feel
  overwhelmed, spend some time inquiring on the internet or contact us (with
  precise questions).

### What to expect?

If you follow these steps, your contribution proposition should be accepted!
You shall then be credited as a d∃∀duction's contributor. Nevertheless,
respecting the above stages by nowise means that your contribution proposal
*will* be accepted. Those stages ensure that your contribution fits in
d∃∀duction's code-base as much as possible, but we may reject it if necessary.
Finally, you will not get any kind of financial retribution. We are poor
anyway.

### Setting-up the development environment

In order to contribute, it is necessary to set-up d∃∀duction's development
environment. This includes a Python virtual environment, a Python linter (file
[`.flake8`](.flake8)), git hooks, etc. To set it up and make sure every
dependency is up-to-date, open a terminal at the repository's root and run the
following command:

```bash
source envconfig
```

You should now have a `(env)` in front of your terminal prompt. It is *highly*
recommended to set up the development environment at the very beginning of
every development session.



## Guidelines

### Code documentation

As you will see in this section, d∃∀duction's code documentation may be long to
write and needs maintenance. **Documentation is however as essential as your
code**. It may be never useful for the author but *will* be for any person
discovering your code in order to maintain it understand it for their own
needs. When writing documentation, you should always assume that the reader is
not familiar with your code and has very few time to understand it. The writer
should do most of the work, so that the reader can efficiently and fastly
understand the essence and utility of your code by reading its documentation a
single time. Documentation should not only tell what a piece of code does, it
*must* tell why it exists, why it is *necessary*, where it is used and how it
is used (provide examples if necessary). Context of the code is almost as
important as the code.

#### Functions and methods signatures

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

#### Functions and methods docstrings

All functions and methods *must* be documented: you *must* provide a
[docstring](https://www.python.org/dev/peps/pep-0257/) *should* provide
comments. Functions and methods docstrings *must* have the following format:

```python3
"""
Summary (what does it do, why is it useful, why is it there, why should we not
delete it).

:param param_1: description of param_1
…
:param param_2: description of param_2
:return: what does it return (if applicable)
"""
```

See
[Examples](https://github.com/dEAduction/dEAduction/blob/dev/start-coex/src/deaduction/dui/stages/start_coex/start_coex_widgets.py).

#### Comments style

Comments follow the PEP 8 convention. If necessary and the result if not
bloated, you *may* use so-called *section comments*:

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
after them.

> If you are using vim / neovim, consider using the addon
[UltiSnips](https://github.com/sirver/UltiSnips) to effeciently add headers.
Ready-to-use snippets are available in
[`tools/vimconfig/UltiSnips/python.snippets/deaduction.snippets`](https://github.com/dEAduction/dEAduction/blob/dev/start-coex/tools/vimconfig/UltiSnips/python.snippets/deaduction.snippets).


#### Classes docstrings

All classes *must* be documented as well: you *must* provide a docstring and
*should* provide comments. Classes docstrings follow the same rules as
functions and methods docstrings, except that public class attributes must be
written in the class docstring using a `:attribute attribute_name: Attribute
description` syntax. See
[Examples](https://github.com/dEAduction/dEAduction/blob/dev/start-coex/src/deaduction/dui/stages/exercise/exercise_main_window.py).

### Python file headers

Files headers *must* have the following structure:

```python3 
"""
##################################
# <filename> : Short description #
##################################
    
    (optional long description)

Author(s)    : - Name <mail@website.com>
Maintainer(s): - Name <mail@website.com>
Created      : Creation date
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
[example](https://github.com/dEAduction/dEAduction/blob/dev/start-coex/src/deaduction/dui/stages/missing_dependencies/missing_dependencies_dialogs.py).
Non Python files *must* also have this header, simply get rid of the doctring
`"""` marks.

> If you are using vim / neovim, consider using the addon
[UltiSnips](https://github.com/sirver/UltiSnips) to effeciently add headers.
Ready-to-use snippets are available in
[`tools/vimconfig/UltiSnips/python.snippets/deaduction.snippets`](https://github.com/dEAduction/dEAduction/blob/dev/start-coex/tools/vimconfig/UltiSnips/python.snippets/deaduction.snippets).


### Git commit messages

#### Specifications

> This convention is strongly inspired from the Angular project Commit
Message Format
[guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit).

Commit messages consist of a mandatory header and an optional body. The
commit header is what you put between the quotation marks in the command `git
commit -m ""`. It is the most informative part of the commit and its structure
follows some rules. The body is everything after the header and a blank line,
its structure is free.  Most commit messages only have a header, which *must*
have the following structure:

```
area::type(scope): Summary
```

Argument `area` is mandatory and *must* be one of:

`area`     | Definition
--|-
`code`     | Changes affecting the code-base.
`doc`      | Changes affecting the documentation (including comments and docstrings).
`snippets` | Changes affecting the snippets.
`tests`    | Changes affecting the tests.
`tools`    | Changes affecting the tools and the development environment.
`dui`      | Changes that affect d∃∀duction's user interface (e.g. texts, tooltips) but do not have to do with how the code is.

Argument `type` is also mandatory and *must* be one of:

`type`   | Definition
|
`chores` | Changes affecting that do not affect the meaning of what is changed (e.g. changing a filename).
`dev`    | Work in progress for new features; changes that are part of its development though not introducing it. A series of `dev` commits end with a `feat` commit.
`feat`   | Changes that introduce a completed new feature. When developing it, the last commit *must* be the only one to use this type, all other *must* use dev.
`fix`    | Fix bugs and problems.
`revert` | Revert to a previous commit, feature or state of the project.
`ref`    | Refactoring.

Scope is optional, it is the (precise) part that was changed (e.g. a class,
function or module name or a combination of all that). Precision is up to you,
use it if necessary. In doubt, use a scope. Finally, the summary *should* be
the shortest possible sentence describing the commit. It *should* begin with a
capital letter and *must not* end with a period, it *should* also be in present
tense. The combination of the mandatory area and type, and optionally the
scope, help you identify which commits in the git log are most relevant to you.
The scope helps identifying which parts of the project are changed.

The body of the commit message *may* be used to provide additional information
about the changes, such as technical explanations.

There is one exception to these rules: merge messages. Merge commit messages
*must* have the following structure:

```
merge: repoA/branchA -> repoB/branchB
```

where `repoA` and `repoB` are remote names (if one of them is a copy on your
own computer, use `local`) and the merge is from `branchA` to `branchB`.

#### Examples

If you finish writing the first part of the function `my_function`, but this
function is not ready, you should use the type `dev`. Since this function is
part of the code-base, you must use the area `code`. This is a good commit
message:

```
code/dev: Finish first part of my_function
```

However you can be more precise using a scope. If the function is part of the
module `dui.utils`, this commit message is better:

```
code/dev(dui.utils): Finish first part of my_function
```

If you fix in the script `envconfig` (the one that sets up the virtual
environment), the header (we leave it to you to imagine a summary) should be:

```
tools/fix(envconfig):
```

Now if you wish to merge the branch `dev/the_new_feature` from Github (repo's
name is `origin`) to your computer, the commit message *must* be:

```
merge: origin/dev/the_new_feature -> local/dev/the_new_feature
```

and if you want to merge the branch `the_new_feature` to the branch `master` on
your computer, the commit mesage *must* be:

```
merge: local/dev/the_new_feature -> local/master
```

Beware that any non-compliant commit message *will* be rejected by the git
hook.

### Git branch names

Branch names *must* have the following structure:

```
area::type/name
```

Arguments `area` and `type` are mandatory and follow the same rules as in the
git commit message [guidelines](#git-commit-messages). Argument `name` is
mandatory is a description of what you are doing on this branch. It should be
as short as possible and words must be separated by an hyphen (-). Use lower
case.

> A branch should host a *single* new feature, fix, etc.

### Python code (modified PEP 8) and linting

d∃∀duction's Python code follows the [PEP 8 convention](https://pep8.org), with
the adjustments hereunder. You *should* check your Python code syntax using the
project's
[linter](https://sourcelevel.io/blog/what-is-a-linter-and-why-your-team-should-use-it),
that is a slightly modified [flake8](https://flake8.pycqa.org/en/latest/#)
version:
- E201: whitespace after ‘(‘;
- E202: whitespace before ‘)’;
- E203: whitespace before ‘:’;
- E221: multiple spaces before operator.

To lint your Python module, simply run the terminal command:

```bash
flake8 my_module.py
```

> Be sure to have the development environment properly [set
  up](#setting-up-the-development-environment) and to be in the Python virtual
  environment.

#### Consecutive lines with `=` operators

Occurrences of `=` operator on a series of consecutive non blank lines *must* be
vertically aligned. See example:

```python3
my_int             = 10
my_string          = 'd∃∀duction'
my_bigger_variable = 'Code is read much more often than it is written.'

other_int    = 2
other_string = 'free software'
```

#### Import statements

As PEP 8 says,
> Imports must be grouped in the following order:
> 
>   1. standard library imports
>   2. related third party imports
>   3. local application/library specific imports
>
> You must put a blank line between each group of imports.

We add the following rule: `import` statements *must* be vertically aligned.
Inside a group or a single statement, imports *must* be alphabetically ordered.
Finally, relative imports *may* be used in some cases; they follow the same
rules as regular imports and *must* be grouped after the last group of regular
imports and a blank line.
See [Example](https://github.com/dEAduction/dEAduction/blob/dev/start-coex/src/deaduction/dui/stages/exercise/exercise_main_window.py).



## Resources (bonus)

> Feel free to suggest new resources*.

### For Python (version 3)

- The [official documentation](https://docs.python.org/3/).

    There are dozens of online tutorials, if you are new to Python, be sure to
    choose one which covers classes (with heritage and usual decorators).

- A [guide](https://realpython.com/python-virtual-environments-a-primer/) to
    virtual environments.
- Python properties, [how tu use them and
    why](https://www.programiz.com/python-programming/property), this is
    defintely worth reading if you want to Python the Python way. Properties
    make the code stronger and nicer to read. Unfortunately, we did not use
    them enough in the code-base, but you should still do it if relevant.
- Python [thematic tutorials from ZetCode](https://zetcode.com/all/#python) are
    always great.

### For L∃∀N

- The [official documentation](https://leanprover.github.io/documentation/).
- The [Natural number
    game](https://wwwf.imperial.ac.uk/%7Ebuzzard/xena/natural_number_game/) to
    learn L∃∀N by using it, no experience needed.

### For PySide2 / Qt for Python

- The [official
    documentation](https://doc.qt.io/qtforpython/quickstart.html).
- This excellent [tutorial](http://zetcode.com/gui/pyqt5/), perfect if you want
    to learn from scratch. (To make it work, simply replace all occurences of
    `PyQt5` by `PySide2`; there are some other minor problems but you will make
    it.)

### For Trio and QTrio

- Trio's [official documentation](https://trio.readthedocs.io/en/stable/).
- QTrio's [repository](https://github.com/altendky/qtrio).

### For Git

- The [official documentation](https://git-scm.com/doc).
- The (free) book [*Pro Git*](https://git-scm.com/book/en/v2) is a complete and
    rigourous way of becoming proficient in Git.

### On free software

- GNU's article [What is free
    software?](https://www.gnu.org/philosophy/free-sw.html) covers the basics in a
    rigourous way.
- The page [How to Contribute to Open
    Source](https://opensource.guide/how-to-contribute/)) is a great introduction
    to free software in practice if you never contributed before. It will tell you
    what to expect from this first experience.
- A [collection](https://github.com/devspace/awesome-github-templates) of github
    issues and pull requests templates.
