# CONTRIBUTING.md

Hello and welcome! Contributing to d∃∀duction is the best way to help
d∃∀duction. We are a small team, we do not know what we are doing. d∃∀duction
is a free software (see [Annex A]()): everybody has access to the code-base and
can participate! This document tells you what you can do to help and how you
can do it.

# Get started

> Abstract: In this section, you will learn about the project's architecture, tools
and work environment.

## Project architecture

There are two repositories:
[deaduction](https://github.com/dEAduction/dEAduction) (contains all the source
code and tools) and
[deaduction-lean](https://github.com/dEAduction/dEAduction-lean) (contains
L∃∀N code and exercises files).

# Guidelines
## Git commit messages

> Note: This convention is strongly inspired from the Angular project Commit
Message Format
[guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit).

> Note: Words like must, may, etc, are to be understood as specified in the
[RFC 2119 specification](https://tools.ietf.org/html/rfc2119).

Commit messages consist of a mandatory **header** and an optional **body**. The
commit header is what you put between the marks in the command `git commit -m
""`. It is the most informative part of the commit and its structure follows
some rules. The body is everything after the header and a blank line, its
structure is free.  Most commit messages only have a header, which *must* have
the following structure:

```
<type>(<scope>): <summary>
```

Commit type *must* be one of the following:

- `chores`:	Changes in the code-base that do not affect the meaning of the
code.
- `dev`: Work in progress for new features; changes that are part of
its development though not introducing it. A series of `dev` commits end with a
`feat` commit.
- `doc`: Changes that affect documentation (including repository
documentation, code comments and docstrings, file headers).
- `feat`: Changes that introduce a completed new feature. When developing
it, the last commit *must* be the only one to use this type, all other *must*
use dev.
- `fix`: Fix problems in the code-base.
- `revert`: Revert to a previous commit or remove a feature. Commits
preparing a revert *must* use sub-types (e.g. `revert::dev`) and not direct
types.
- `ref`: Refactor code.
- `snippet`: Changes that affect snippets. Following sub-types may be used:
`snippet::chores`, `snippet::dev`, `snippet::doc`, `snippet::feat`,
`snippet::fix`, `snippet::revert`, `snippet::ref`.
- `test`: Changes that affect testing. Following sub-types may be used:
`test::chores`, `test::dev`, `test::doc`, `test::feat`, `test::fix`,
`test::revert`, `test::ref`.

Together with the scope, the commit type help you identify which commits in the
git log are the most relevant to you.  The scope helps identifying which are of
the project are changed. Precision is up to you; use it if helpful. Finally,
the summary *should* be the shortest possible sentence describing the commit.

The body of the commit message *may* be used to provide additional information
about the changes, such as technical explanations.
