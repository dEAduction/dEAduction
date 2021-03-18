# Contributing to d∃∀duction

Hello and welcome! Contributing to d∃∀duction is the best way to help
d∃∀duction. We are a small team of dumb devs, we don't know what we're doing.
d∃∀duction is a free software &#x1F534;**TODO** (lien free software):
everybody has access to the code-base and can participate! This document tells
you what you can do to help, how you can do it and what to expect.

## Get started

The d∃∀duction project has two repositories:
[deaduction](https://github.com/dEAduction/dEAduction) (contains all the source
code and tools) and
[deaduction-lean](https://github.com/dEAduction/dEAduction-lean) (contains L∃∀N
code and exercises files). To know more about each directory, module or file,
simply open its `__init__.py` or `README.md`.

d∃∀duction is written in Python3 (&#x1F534;**TODO** lien) and L∃∀N (L∃∀N is a
proof assistant able to understand mathematical expressions and prove
statements to be true or false, &#x1F534;**TODO** liens). The graphical
interface uses the module PySide2 (Qt for Python) and communication between the
user interface and L∃∀N uses two modules called Trio and Qtrio
(&#x1F534;**TODO** lien). A good experience in Python3 is *recommended*, as
well as basic terminal usage, but you do not need to be advanced in anything to
contribute. The version control system (&#x1F534;**TODO** liens) we use is Git
(&#x1F534;**TODO** liens). Some experience in Git is necessary but you can
rapidly learn it from scratch (&#x1F534;**TODO** lien tuto).

A very important thing is *virtual environments* (&#x1F534;**TODO** lien). A
virtual environment is an isolated environment in a project directory in which
all dependencies versions are frozen until manually changed (they can remain
unchanged if we chose to). It is very easy to determine whether or not you are
in the virtual environment of your project directory: there should be a `(env)`
in front of your shell prompt, like in this screenshot:

![venv screenshot](docs/CONTRIBUTING-images/veng.png)

To setup d∃∀duction's virtual environment, open a terminal at the repository's
root and run the command

```
source envconfig
```

This will also make sure everything is up-to-date.

## Contributing

(&#x1F534;**TODO** intro pour cette §)

### What do?

There are many different things you can do to help, and you do not need to be a
programming wizard. Quality is *much* more helpful than quantity, there is no
small contribution. You should always browse issues (&#x1F534;**TODO** lien)
first to know what you can do. If you think you can work on an issue, reply to
it first so we can discuss more precisely how we work together. Note that
issues include many things, such as new features proposals, bug reports, code
refactoring and discussions. If you wish to develop a new feature, open an
issue first (see issues guidelines (&#x1F534;**TODO** lien vers la §) so we can
discuss it.

That being said, not all good contribution ideas are in the issues (we are
often too lazy to open an issue when we see code that should be refactored). Do
feel free to open one. Here are contribution ideas, in order of preference:
- **Refactor code**: yeah, please help us. d∃∀duction needs a strong code-base
    and as of now it is rather weak.
- **Report stuff**: bugs, refactoring suggestions, user interface suggestions,
    new features proposals, etc (see issues guidelines (&#x1F534;**TODO** lien
    vers la §).
- **Translate user interface**.
- **Write documentation**: many modules, classes or functions are undocumented,
    but they should be. You can also contribute to d∃∀duction's user manual.
    Contributions and feed-back to *this* document would also be very much
    appreciated.
- **Create exercises**.

(&#x1F534;**TODO** ajouter issues avec tag first contribution)

In any case, every contribution proposition should have its issue, whether we
or you created it. To save you time, you should never work on a contribution
which was not approved (there would be a risk of it being rejected)!

### How do?

You first need to fork (&#x1F534;**TODO** lien c'est quoi une fourchette)
d∃∀duction's repository and create a new branch for your single contribution
(do not use a branch for more than one thing), see branches guidelines
(&#x1F534;**TODO** lien). Do not do your modifications on the `master` branch.
You can now begin writing your contribution!

Remember to commit often; in doubt commit. On top of that, keep your fork
up-to-date with upstream (that is, with d∃∀duction's branch you forked from).

At any stage, do feel free to discuss your contribution's development with the
core team. This should be done publicly, in the contribution proposition's
issue.

When you think your contribution is finished, push it to your online fork.
Signal it in the contribution proposition's Github issue so we can review it,
discuss it and test it. After potential modifications and if we approve your
contribution, we will tell you that your contribution is ready for
pull-request! At that point, you just do the pull request and we accept it.

### What to expect?

To summarize, here is how you should contribute:
1. Choose an existing issue or open one with a contribution idea.
2. In this issue, inform us dummies that you would like to contribute so we can
   discuss.
3. Make your fork, create your new branch, code, keep up-to-date and push your
   contribution proposal once you think it is ready.
4. In the contribution's proposal issue, inform us apes that you think your
   contribution is ready so we can discuss and potentially ask you to make some
   changes.
5. If we approve the final version of the contribution proposition, you may do
   a pull request. We should accept it after a final review.

If you follow these steps, your contribution proposition should be accepted!
You shall then be credited as a d∃∀duction's contributor. Nevertheless,
respecting the above stages by nowise means that your contribution proposal
*will* be accepted. Those stages ensure that your contribution fits in
d∃∀duction's codebase as much as possible, but we may reject it if necessary.
Finally, you will not get any kind of financial retribution. We are poor
anyway.

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

Non function or method annotations *may* be provided.

#### Function and methods docstrings

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

Here is an example from the codebase, with the method annotated:

```python3
 def set_preview(self, main_widget: Optional[QWidget], title: Optional[str],
                subtitle: Optional[str], details: Optional[Dict[str, str]],
                description: Optional[str], expand_details: Optional[bool]):
    """
    Set the preview area of the choosen course or exercise (given
    something has been chosen). The preview area is made of a title,
    a substitle, details, a description and a main widget. This
    widget is of course specific to CourseChooser or ExerciseChooser
    and defined when the set_preview method is redefined in
    CourseChooser or ExerciseChooser. Visually, the preview area
    looks like this:

    |----------------------------|
    | title (big)                |
    | subtitle (small, italic)   |
    | |> Details:                |
    |     …: …                   |
    |     …: …                   |
    |                            |
    | description .............. |
    | .......................... |
    | .......................... |
    |                            |
    | |------------------------| |
    | |      main_widget       | |
    | |------------------------| |
    |----------------------------|

    :param main_widget: The main widget of the preview (nothing for
        the course, goal preview for the exercise).
    :param title: Course or exercise title.
    :param subtitle: Course or exercise subtitle.
    :param details: Other data for the course or exercise such as
        the course's year, teacher, school, etc.
    :param description: The course or exercise description.
    :param exapand_details: Tell if the 'Details' disclosure tree is
        expanded at __init__ (True) or not (False).
    """
```

#### Classes docstrings

All classes *must* be documented as well: you *must* provide a docstring and
*should* provide comments. Classes docstrings follow the same rules as
functions and methods docstrings, except that public class attributes must be
written in the class docstring using a `:attribute attribute_name: Attribute
description` syntax. Here is an example from the codebase:

```python3
class ExerciseMainWindow(QMainWindow):
    """
    This class is responsible for both:
        - managing the whole interface for exercises;
        - communicating with a so-called server interface (self.servint, not
          instantiated in this class): a middle man between the interface and
          L∃∀N.

    … docstring continues …

    Finally, all of this uses asynchronous processes (keywords async and
    await) using trio and qtrio.

    :attribute exercise Exercise: The instance of the Exercise class
        representing the exercise to be solved by the user, instantiated
        in deaduction.dui.__main__.py.
    :attribute current_goal Goal: The current goal, which contains the
        tagged target, tagged math. objects and tagged math. properties.
    :attribute current_selection [MathObjectWidgetItem]: The ordered of
        currently selected math. objects and properties by the user.
    :attribute ecw ExerciseCentralWidget: The instance of
        ExerciseCentralWidget instantiated in self.__init__, see
        ExerciseCentraiWidget.__doc__.
    :attribute lean_editor LeanEditor: A text editor to live-edit lean
        code.
    :attribute servint ServerInterface: The instance of ServerInterface
        for the session, instantiated in deaduction.dui.__main__.py.
    :attribute toolbar QToolBar: The toolbar.
    """
```

### Git commit messages

#### Specifications

> Note: This convention is strongly inspired from the Angular project Commit
Message Format
[guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit).

> Note: Words like must, may, etc, are to be understood as specified in the
[RFC 2119 specification](https://tools.ietf.org/html/rfc2119).

Commit messages consist of a mandatory header and an optional body. The
commit header is what you put between the quotation marks in the command `git
commit -m ""`. It is the most informative part of the commit and its structure
follows some rules. The body is everything after the header and a blank line,
its structure is free.  Most commit messages only have a header, which *must*
have the following structure:

```
part/type(scope): Summary
```
Part is mandatory and *must* be one of:

Part       | Definition
-----------|-------------------------------------------------------------------
`code`     | Changes affecting the code-base.
`doc`      | Changes affecting the documentation (including comments and docstrings).
`snippets` | Changes affecting the snippets.
`tests`    | Changes affecting the tests.
`tools`    | Changes affecting the tools and the development environment.
| &#x1F534;**TODO**: RAJOUTER PART TOOLTIPS

Type is also mandatory and *must* be one of:

Type     | Definition
---------|---------------------------------------------------------------------
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
tense. The combination of the mandatory part and type, and optionally the
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
part of the code-base, you must use the part `code`. This is a good commit
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

### Python code guidelines (modified PEP 8)

d∃∀duction's Python code follows the [PEP 8 convention](https://pep8.org), with
the following exceptions.

#### Consevutive lines with `=` operators

Occufences of `=` operator on a series of consecutive non blank lines *must* be
vertically aligned. Example:

```python3
my_int             = 10
my_string          = 'd∃∀duction'
my_bigger_variable = 'Code is read much more often than it is written.'

other_int    = 2
other_string = 'free software'
```
**Import statements**

PEP 8 tells us that
> Imports must be grouped in the following order:
> 
>   1. standard library imports
>   2. related third party imports
>   3. local application/library specific imports
>
> You must put a blank line between each group of imports.

We add the following rule: `import` statements *must* be vertically
aligned. Example:

```python3
from functools import partial
import                logging
from typing import    Callable
import                qtrio

from PySide2.QtCore import (    Signal,
                                Slot,
                                QEvent )
from PySide2.QtWidgets import ( QInputDialog,
                                QMainWindow,
                                QMessageBox )

from deaduction.dui.elements            import ( ActionButton,
                                                 LeanEditor,
                                                 StatementsTreeWidgetItem,
                                                 MathObjectWidget,
                                                 MathObjectWidgetItem )
from deaduction.dui.primitives          import   ButtonsDialog
from deaduction.pylib.config.i18n       import   _
from deaduction.pylib.memory            import   Journal
from deaduction.pylib.actions           import ( InputType,
                                                 MissingParametersError,
                                                 WrongUserInput)
import deaduction.pylib.actions.generic as       generic
```

Inside a group or a single statement, imports *must* be alphabetically
ordered. Finally, relative imports *may* be used in some cases; they follow
the same rules as regular imports and *must* be grouped after the last
group of regular imports and a blank line.
