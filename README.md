# Etch template

A minimal consumer repository for [Etch](https://github.com/rm-industries/etch).
It includes one generic Git configuration module, a developer profile, empty
provider defaults, and an engine pinned as a Git submodule. There are no optional
plugins, personal identity settings, credentials or package installations.
The Git module declares an `available` fact with the explicit `command` provider;
`./etch facts --profile developer` shows whether Git is on your path.

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

Keep module and profile files consistent with Etch's built-in formatter. Short
lists such as `['git']` stay inline, while longer lists split. Comments are kept.
No Python formatter or package installation is needed:

```sh
./etch format
./etch format modules/git/module.conf
./etch format --check
./etch validate
```

`format --check` verifies the canonical layout without changing files; `validate`
separately checks static configuration declarations. `.editorconfig` helps your
editor follow Etch's two-space style but does not control either command.

## Initialize and inspect the engine pin

For an ordinary clone or a new template copy without checked-out submodules:

```sh
git submodule update --init --recursive
git submodule status vendor/etch
git ls-tree HEAD vendor/etch
```

`.gitmodules` records where to fetch Etch. The `160000` entry in the consumer's
Git tree records the exact commit; it does not track a moving branch. This starter
pins Etch `v0.1.0` at `48dd8ee485f539196c83ff497f7a1298ffd5c803`. Generated consumers preserve that
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
inside the submodule; contribute engine changes upstream. Dependabot proposes
reviewed `vendor/etch` pin updates, and CI verifies those PRs without moving the
pin itself. There is no implicit plugin installation.

## CI checks your configuration

The included workflow runs the `developer` profile on Linux and macOS with both
Python 3.9 and the latest stable Python 3.x. The profile currently contains the
starter Git module; add ordinary modules to that profile rather than to the CI
matrix. Each job uses a fresh temporary home and the pinned engine, then:

1. Checks formatting and validates static declarations with Etch itself.
2. Runs `plan`, `apply`, and `doctor` for the representative profile.
3. Checks that `.gitconfig` is a link to the module-owned file and that Git reads
   the expected `init.defaultBranch = main` setting.
4. Applies the profile again and fails if it reports changes or failures.

There are no template test fixtures or separate Python test suite. This workflow
validates your configuration through the commands you actually use. Etch's engine
repository separately tests bootstrap and provider implementation behavior.

When you add modules, install their prerequisites on the CI runner and add only
the assertions needed for the state your repository promises. A successful
apply alone is not a check of every desired setting. Opaque commands may report
execution on every apply; adjust the second-run assertion deliberately if your
configuration includes them.

The workflow runs on configuration pushes, pull requests, a weekly schedule and
manual dispatch. Dependabot also proposes GitHub Actions and pinned Etch updates.
Repository automation checks workflow syntax and security with actionlint and
zizmor; a separate security workflow runs CodeQL for Actions and Dependency Review.
A temporary home isolates home-file changes, but package-manager actions added
later can still change the runner's system state. Use disposable runners for
installation jobs.
