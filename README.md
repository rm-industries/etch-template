# Etch template

A minimal consumer repository for [Etch](https://github.com/rm-industries/etch).
It includes generic Git and launcher modules, a developer profile, empty
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
modules before applying: this starter links its generic file to `~/.gitconfig`
and installs a user-local launcher through the `etch` module.
An existing conflicting file is refused, so migrate its settings and decide
ownership before replacing anything.

```sh
./etch doctor --profile developer
./etch apply --profile developer
./etch facts --profile developer
```

Explicit arguments are passed to Etch unchanged. The launcher resolves its actual checkout, including through absolute/relative
symlinks, and runs from the consumer root even when invoked from another directory. Runtime needs only a
supported Linux/macOS environment with `/bin/sh`, or native Windows with
PowerShell, and Python 3.9 or newer on PATH; no virtual
environment, pip, Git or network is needed after the engine is initialized.
Git and network access are needed to clone/initialize or update the submodule.

## Windows and the user-local launcher

On Windows, use `.\etch.cmd` or `.\etch.ps1` with the same arguments as `./etch`.
A bare invocation shows a plan. For example:

```powershell
.\etch.cmd plan --profile developer
.\etch.cmd apply --profile developer
```

The `etch` module links the consumer's launchers into `~/.local/bin` and adds that
directory to Windows **user** PATH. Open a new terminal afterward; `etch` will find
this consumer from other directories. On Unix the module links `etch`; add
`~/.local/bin` to your shell PATH if needed. The module does not use machine PATH.

Before Windows `apply`, the launcher probes file and directory symlink creation
with the current Python process. If denied, it stops before applying and explains
how to enable Developer Mode for non-admin use. It does not elevate or change
system settings. `plan`, `doctor`, and help remain available. Success in an admin
session does not grant a normal terminal privileges; test from your normal session.
Individual destination permissions can still deny linking after the probe passes.

## Bootstrap a generated repository

`install.sh` (macOS/Linux) and `install.ps1` (native Windows PowerShell 5.1 or
PowerShell 7) are fresh-machine bootstraps. They require Git, clone once, and
initialize pinned submodules. They do not install prerequisites, elevate, pull,
update an existing checkout, or apply a complete profile.

GitHub does **not** rewrite script contents when generating a repository from a
template. Before sharing your installer, configure the owner-editable values at
the top of **both** scripts:

- Repository: your generated repository URL. It is initially empty and must be
  configured or supplied with `--repo URL`; there is no upstream-template fallback.
- Destination: initially `~/.dotfiles`. Edit the default or set `DOTFILES_DIR`.
- Module: initially empty, so no module runs. Set `module='etch'` in `install.sh`
  and `$module = 'etch'` in `install.ps1` to install only the user-local launcher.

`--repo URL` overrides the owner's repository default. `--module NAME` runs
exactly that one module through the existing Etch CLI after a fresh clone.
`--no-module` suppresses any configured or explicit module, regardless of flag
order. Python 3.9+ (`python3` on Unix, `python` on Windows) is required only when a
fresh install will run a module; clone-only and existing-checkout runs need no Python.

After committing these files in **your generated repository**, substitute its
owner/name in both URLs below. The downloaded script and the clone URL must refer
to the same repository. These commands become available only after your commit is
published to that repository's `main` branch:

```sh
installer=$(curl -fsSL https://raw.githubusercontent.com/YOUR-OWNER/YOUR-DOTFILES/main/install.sh) && printf '%s\n' "$installer" | sh -s -- --repo https://github.com/YOUR-OWNER/YOUR-DOTFILES.git
```

```powershell
powershell.exe -NoProfile -Command "& ([scriptblock]::Create((Invoke-RestMethod -Uri 'https://raw.githubusercontent.com/YOUR-OWNER/YOUR-DOTFILES/main/install.ps1' -ErrorAction Stop))) --repo 'https://github.com/YOUR-OWNER/YOUR-DOTFILES.git'"
```

Downloading and executing an installer trusts that repository's current code and
pinned submodules. On managed machines, or when reviewing changes, prefer downloading
and reading the script first. An immutable commit URL can replace `main`:

```sh
curl -fsSL https://raw.githubusercontent.com/YOUR-OWNER/YOUR-DOTFILES/main/install.sh -o install.sh
less install.sh
DOTFILES_DIR="$HOME/my dotfiles" sh install.sh --repo https://github.com/YOUR-OWNER/YOUR-DOTFILES.git --no-module
```

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/YOUR-OWNER/YOUR-DOTFILES/main/install.ps1' -OutFile install.ps1
Get-Content .\install.ps1
$env:DOTFILES_DIR = Join-Path $HOME 'my dotfiles'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 --repo https://github.com/YOUR-OWNER/YOUR-DOTFILES.git --no-module
```

The reviewed-file Windows command sets execution policy only for that process;
Group Policy still takes precedence. Windows modules that create symlinks still
need Developer Mode or the appropriate session privileges. The installers do not
change those settings. To select a module, replace `--no-module` with `--module etch`
(or another module name), then open a new terminal if it updates user PATH.

An existing checkout with the expected `origin` is a **strict no-op**, even with
`--module`: no pull, submodule update, or Etch command runs. GitHub HTTPS and SSH
origins are recognized as the same repository, with or without `.git`. Other
occupied destinations, including dangling links, fail without being overwritten.
Failed clone/submodule operations can leave a partial checkout. It is retained
for inspection; a rerun does not repair it. If a module fails, resolve the error
and run Etch explicitly from the retained checkout.

Both scripts use exit 2 for invalid arguments or missing repository configuration,
127 for a missing prerequisite, and 1 for an unrelated destination. Git and Etch
failure exit codes are preserved. Bootstrap behavior is tested with local generated
repositories and recursive submodules, on Unix and both Windows PowerShell hosts.

## Files you own

```text
etch
install.sh
install.ps1
etch.cmd
etch.ps1
.gitmodules
.gitignore
.gitlab-ci.yml
.github/workflows/etch.yml
defaults.conf
profiles/developer.conf
modules/etch/module.conf
modules/etch/add-user-path.ps1
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
pins Etch source commit `652196260fa53eda727f55e69ef649673ade607e`. Generated consumers preserve that
pin when they retain the template's Git tree. Downloading a source ZIP does not
include submodule contents; use a recursive clone or initialize the submodule.
The launcher prints initialization guidance when the engine is absent. Once the
engine is available, use `./etch submodules update` (or `etch submodules update`
through the optional user-local launcher) to initialize all consumer submodules
at their recorded pins. This does not select newer upstream revisions.

## Update deliberately

Choose and review an Etch release or commit, then update the pin explicitly:

```sh
git -C vendor/etch fetch origin
git -C vendor/etch checkout --detach REVIEWED_COMMIT
git add vendor/etch
./etch doctor --profile developer
./etch
git commit -m "Update pinned Etch engine"
```

Replace `REVIEWED_COMMIT` with the full revision you chose. Commit that gitlink
change in the consumer repository and review its diff. Avoid editing engine files
inside the submodule; contribute engine changes upstream. Dependabot proposes
reviewed `vendor/etch` pin updates, and CI verifies those PRs without moving the
pin itself. There is no implicit plugin installation.

## CI checks your configuration

The GitHub workflow runs the `developer` profile on Linux, macOS and Windows with both
Python 3.9 and the latest stable Python 3.x. The profile currently contains the
starter Git and Etch launcher modules; add ordinary modules to that profile
rather than to the CI matrix. Each job uses a fresh temporary home and the pinned engine to check formatting,
validate declarations, diagnose repository setup, preview the developer profile
and apply it. This follows the dotfiles workflow: CI checks whether **your setup
applies successfully**, rather than testing Etch's implementation. Extend the
profile and install runner prerequisites when adding modules. Optional assertions
for application-specific outcomes belong to the consumer only when desired.
Launcher regression tests, symlink edge cases and provider internals are tested in
core Etch. The Windows consumer job also invokes the installed launcher from an
unrelated directory and verifies an unchanged second apply. The consumer's own
bootstrap scripts are checked by `.github/tests/test_installers.py`, using temporary
local Git fixtures rather than cloning hosted repositories. GitHub runs that contract
on Unix and both PowerShell hosts; GitLab runs its Unix contract.

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

## User-local launcher

The included `etch` module installs the appropriate consumer launchers and is part
of the developer profile. Launchers follow their symlinks back to the checkout;
keep that checkout and its pinned engine available. Moving the checkout requires
reapplying the module to update the links. Dangling links and cycles fail rather
than guessing a checkout. Existing files and directories are refused; `relink`
only permits replacing a different symlink.

On Unix, add `$HOME/.local/bin` to your shell's own startup configuration if it is
not already on PATH. The template does not pick a shell or edit startup files.
On Windows, the module adds the directory to user PATH; reopen your terminal.
Core Etch tests launcher behavior, while template CI applies the selected profile
in an isolated home and verifies the linked Windows launcher and second apply.

The Windows `.cmd` wrapper permits its trusted launcher script in its own PowerShell
process without changing user or machine execution policy; organization Group Policy
still takes precedence. Child provider processes inherit this session policy.
Direct `.ps1` invocation requires a session that permits scripts.
