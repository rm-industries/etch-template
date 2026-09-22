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
./etch
```

`./etch` displays the developer **plan**. It does not apply changes. Review the
module before applying: this starter links its generic file to `~/.gitconfig`.
An existing conflicting file is refused, so migrate its settings and decide
ownership before replacing anything.

```sh
./etch doctor --profile developer
./etch apply --profile developer
./etch facts --profile developer
```

Explicit arguments are passed to Etch unchanged. The launcher runs from the
consumer root even when invoked from another directory. Runtime needs only a
supported Linux/macOS environment, `/bin/sh`, and Python 3.9 or newer; no virtual
environment, pip, Git or network is needed after the engine is initialized.
Git and network access are needed to clone/initialize or update the submodule.

## Files you own

```text
etch
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
in `rm-industries/etch`. The included CI workflow is yours to extend alongside
your modules and profiles.

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
./etch doctor --profile developer
./etch
git add vendor/etch
git commit -m "Update pinned Etch engine"
```

Replace `REVIEWED_COMMIT` with the full revision you chose. Commit that gitlink
change in the consumer repository and review its diff. Avoid editing engine files
inside the submodule; contribute engine changes upstream. There is no automatic
engine upgrade, dependency resolver or implicit plugin installation.

## CI checks your configuration

The included workflow runs the real consumer commands on Linux and macOS, both
for the `developer` profile and the standalone `git` module. Each job uses a fresh
temporary home directory, initializes the pinned engine, then:

1. Runs `plan`, `apply`, and `doctor` for that selection.
2. Checks that `.gitconfig` is a link to the module-owned file and that Git reads
   the expected `init.defaultBranch = main` setting.
3. Applies the same selection again and fails if it reports changes or failures.

There are no template test fixtures or separate Python test suite. This workflow
validates your configuration through the commands you actually use. Etch's engine
repository separately tests bootstrap and provider implementation behavior.

Extend the selection matrix when you add profiles or standalone modules, install
their prerequisites on the CI runner, and add assertions for the state you expect.
The Git assertions in this starter suit both current selections; adapt or scope
them when adding unrelated modules. A successful apply alone is not a check of
every desired setting. Opaque commands may report execution on every apply;
adjust the second-run assertion deliberately if your configuration includes them.

The workflow runs on pushes, pull requests and manual dispatch. It uses Python
3.14; engine compatibility across Python versions is tested upstream. A temporary
home isolates home-file changes, but package-manager actions added later can still
change the runner's system state. Use disposable runners for installation jobs.
