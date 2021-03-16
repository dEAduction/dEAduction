# Contributing to d∃∀duction

Hello and welcome! Contributing to d∃∀duction is the best way to help
d∃∀duction. We are a small team, we don't know what we're doing. d∃∀duction is
a free software  &#x1F534;**TODO** (lien free software): everybody has access
to the code-base and can participate! This document tells you what you can do
to help, how you can do it and what to expect.

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
