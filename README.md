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

Explicit arguments are passed to Etch unchanged. The launcher resolves its actual checkout, including through absolute/relative
symlinks, and runs from the consumer root even when invoked from another directory. Runtime needs only a
supported Linux/macOS environment, `/bin/sh`, and Python 3.9 or newer; no virtual
environment, pip, Git or network is needed after the engine is initialized.
Git and network access are needed to clone/initialize or update the submodule.

## Files you own

```text
etch
.gitmodules
.gitignore
.gitlab-ci.yml
.github/workflows/etch.yml
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
pins Etch source commit `f0f0aa3ecce6b31bc2943318497e4f018557abca`. Generated consumers preserve that
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

The GitHub workflow runs the `developer` profile on Linux and macOS with both
Python 3.9 and the latest stable Python 3.x. The profile currently contains the
starter Git module; add ordinary modules to that profile rather than to the CI
matrix. Each job uses a fresh temporary home and the pinned engine to check formatting,
validate declarations, diagnose repository setup, preview the developer profile
and apply it. This follows the dotfiles workflow: CI checks whether **your setup
applies successfully**, rather than testing Etch's implementation. Extend the
profile and install runner prerequisites when adding modules. Optional assertions
for application-specific outcomes belong to the consumer only when desired.
Launcher regression tests, symlink edge cases and provider idempotence belong in
the core Etch project; the starter does not add fixtures or helper directories.

On macOS, CI prepares a temporary cask app directory and loads the environment
of preinstalled Homebrew, including its standard Apple Silicon/Intel locations.
If Homebrew is absent, this optional preparation is skipped; the generic starter
does not require it and CI does not install it. Modules added later can use the
prepared environment. GitLab's initial runner remains Linux, using the same
platform-aware commands. Consumers only need to add runner prerequisites when
their own modules need tools not already available; CI cannot infer every tool
from arbitrary scripts, and privileged bootstrap remains an explicit choice.

The GitHub workflow runs on every push and pull request targeting `main`, a weekly schedule and
manual dispatch. Dependabot also proposes GitHub Actions and pinned Etch updates.
Repository automation checks workflow syntax and security with actionlint and
zizmor; a separate security workflow runs CodeQL for Actions and Dependency Review.
A temporary home isolates home-file changes, but package-manager actions added
later can still change the runner's system state. Use disposable runners for
installation jobs.

## GitLab CI

`.gitlab-ci.yml` provides a Linux container-runner matrix for Python 3.9 and the latest stable Python 3.x. GitLab initializes the pinned engine through
[`GIT_SUBMODULE_STRATEGY: recursive`](https://docs.gitlab.com/ci/runners/git_submodules/); the public HTTPS submodule does not need a
token. Keep the submodule pin when moving your consumer to GitLab. Private
submodules require your own runner authentication configuration.

Both services keep their verification commands directly in their CI YAML files,
using matching blocks to create an isolated temporary home and apply your real
developer profile. Extend both blocks
when adding modules so they continue to exercise the same configuration. No separate test fixtures or Python test packages are added.
The full Python images provide Python, Bash and Git; use a Docker/Kubernetes
runner that supports the job's `image`. Shell runners need those tools installed
and do not select Python versions through `image`.

GitLab runs merge-request pipelines and branch pipelines, avoiding duplicate push
pipelines when a merge request is open. Create schedules in GitLab's UI if you want
periodic checks. macOS and Windows GitLab runners are outside this initial setup.

## Optional GitHub-to-GitLab sync

The `Sync GitLab` workflow copies `main` and tags to your GitLab repository.
In GitHub's Settings → Secrets and variables → Actions, add the repository
variable `GITLAB_REPOSITORY_URL` (a credential-free HTTPS URL ending in `.git`)
and repository secret `GITLAB_TOKEN` (a GitLab token with `write_repository`
scope and permission to push to the destination's protected branches).
Create the destination repository first, preferably without an initial commit.

Without the destination variable, the sync job is skipped. After merging the
workflow into `main`, pushes to `main` or tags sync automatically; manual dispatch
is also available from `main`. The push is atomic and does not force updates or
delete destination refs. Divergent branches or tags fail rather than being
overwritten. GitHub is the source of truth while this workflow is enabled; feature
branches, issues and merge requests are not copied. Successful pushes can start
GitLab CI. Credentials are supplied through a temporary askpass script and are
not stored in the remote URL.

## Optional user-local launcher

The native `sh` launcher follows symlinks using `readlink` (available on Linux
and macOS), without GNU-only `readlink -f` or a Python resolution step. Python
starts only when executing the pinned engine. It supports paths containing spaces,
without copying engine or launcher code. If `~/.local/bin` is on your PATH, a link
at `~/.local/bin/etch` can launch this consumer from any working directory. Keep
both the checkout and its pinned engine available; moving the checkout requires
updating the link. Dangling links and cycles fail rather than guessing a checkout.

With an engine that supports `link.source_scope` (core Etch issue
[#149](https://github.com/rm-industries/etch/issues/149)), declare an optional module
and add it explicitly to your profile:

```python
{
  'schema_version': 1,
  'name': 'launcher',
  'actions': [
    {'link': {'~/.local/bin/etch': {
      'path': 'etch', 'source_scope': 'repo', 'create': True,
    }}},
  ],
}
```

The pinned engine includes repository-scoped sources and repository-wide doctor
diagnostics. Review engine updates deliberately before changing the pin. Existing modules and
profiles need no format or schema migration. Apply the module through `./etch`
first; after setup, `etch validate`, `etch plan --profile developer`, and bare
`etch` use this consumer's configuration and default preview behavior. Regular
file/directory conflicts are refused; explicitly use `relink: True` only when you
want to replace a different symlink.

Installing the link and choosing your PATH are separate. If the directory is not
already on PATH, add `$HOME/.local/bin` using your shell's own startup configuration
(for example `export PATH="$HOME/.local/bin:$PATH"` in a POSIX-compatible shell).
The template does not pick a shell or edit startup files. Launcher regression coverage belongs in core Etch. Template CI only validates
and applies the selected consumer profile in an isolated home.
