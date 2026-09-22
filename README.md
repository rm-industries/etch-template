# Etch template

A minimal consumer repository for [Etch](https://github.com/rm-industries/etch).
It includes one generic Git configuration module, a developer profile, empty
provider defaults, and an engine pinned as a Git submodule. There are no optional
plugins, personal identity settings, credentials or package installations.

## Create your own consumer

Choose **Use this template → Create a new repository** on GitHub, then clone your
new repository with its submodule:

```sh
git clone --recurse-submodules https://github.com/YOU/YOUR-DOTFILES.git
cd YOUR-DOTFILES
./install
```

`./install` displays the developer **plan**. It does not apply changes. Review the
module before applying: this starter links its generic file to `~/.gitconfig`.
An existing conflicting file is refused, so migrate its settings and decide
ownership before replacing anything.

```sh
./install doctor --profile developer
./install apply --profile developer
./install facts --profile developer
```

Explicit arguments are passed to Etch unchanged. The launcher runs from the
consumer root even when invoked from another directory. Runtime needs only a
supported Linux/macOS environment, `/bin/sh`, and Python 3.9 or newer; no virtual
environment, pip, Git or network is needed after the engine is initialized.
Git and network access are needed to clone/initialize or update the submodule.

## Files you own

```text
install
.gitmodules
.gitignore
defaults.conf
profiles/developer.conf
modules/git/module.conf
modules/git/files/gitconfig
vendor/etch/                 # pinned engine submodule
```

Edit the modules, profile, defaults and launcher in your own repository. Add your
personal Git identity there, not in this public template. Your consumer has its
own history and receives no automatic template updates or synchronization.
Template-specific development belongs in this repository; engine issues belong
in `rm-industries/etch`. The starter's validation workflow/tests are optional
consumer maintenance files and can be removed from your copy.

## Initialize and inspect the engine pin

For an ordinary clone or a new template copy without checked-out submodules:

```sh
git submodule update --init --recursive
git submodule status vendor/etch
git ls-tree HEAD vendor/etch
```

`.gitmodules` records where to fetch Etch. The `160000` entry in the consumer's
Git tree records the exact commit; it does not track a moving branch. This starter
pins `2c671d95179780c9559e532144b321f7dac18102`. Generated consumers preserve that
pin when they retain the template's Git tree. Downloading a source ZIP does not
include submodule contents; use a recursive clone or initialize the submodule.
The launcher prints initialization guidance when the engine is absent.

## Update deliberately

Choose and review an Etch release or commit, then update the pin explicitly:

```sh
git -C vendor/etch fetch origin
git -C vendor/etch checkout --detach REVIEWED_COMMIT
./install doctor --profile developer
./install
git add vendor/etch
git commit -m "Update pinned Etch engine"
```

Replace `REVIEWED_COMMIT` with the full revision you chose. Commit that gitlink
change in the consumer repository and review its diff. Avoid editing engine files
inside the submodule; contribute engine changes upstream. There is no automatic
engine upgrade, dependency resolver or implicit plugin installation.

## Validation

```sh
python3 -S -m unittest discover -s tests -v
```

The test suite creates a new consumer history from the template tree, recursively
clones it using a local engine mirror, and checks the pin. Runtime then has only
Python on PATH, site packages disabled, and a temporary home. It verifies the
no-argument plan, first apply, declarative second-apply no-op, missing-engine
message, and argument/exit forwarding. No real home configuration is changed.
Git is a test-fixture requirement, not a runtime requirement. CI runs these tests
on Linux/macOS with Python 3.9 and 3.14. This checks the consumer tree locally;
it does not claim to exercise GitHub's web template-generation service.
