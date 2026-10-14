#!/usr/bin/env bash
# Both CI services exercise the consumer's actual profile and promised state.
set -euo pipefail

cd -- "$(dirname -- "$0")/.."
repo_dir=$(pwd -P)
ci_home=$(mktemp -d)
trap 'rm -rf -- "$ci_home"' EXIT

# Isolate each engine process from the runner's home and preserve argument boundaries.
run_etch() {
  env HOME="$ci_home" "$repo_dir/etch" "$@"
}

run_etch format --check
run_etch validate
python3 -S scripts/verify-launcher.py
run_etch plan --profile developer
run_etch apply --profile developer
run_etch doctor --profile developer

# Extend these assertions alongside your modules; a successful apply alone is insufficient.
test -L "$ci_home/.gitconfig"
test "$(readlink "$ci_home/.gitconfig")" = "$repo_dir/modules/git/files/gitconfig"
test "$(git config --file "$ci_home/.gitconfig" --get init.defaultBranch)" = main

run_etch apply --profile developer | tee "$ci_home/second-apply.log"
if grep -Eq '^[[:space:]]*(CHANGED|FAILED|BLOCKED)([[:space:]]|$)' "$ci_home/second-apply.log"; then
  echo "Second apply did not preserve the expected declarative state." >&2
  exit 1
fi
