"""Exercise the real consumer launcher in an isolated checkout with spaces."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="etch launcher ") as directory:
    temp = Path(directory)
    consumer = temp / "checkout with spaces"
    consumer.mkdir()
    for name in ("etch", "defaults.conf"):
        shutil.copy2(root / name, consumer / name)
    for name in ("modules", "profiles"):
        shutil.copytree(root / name, consumer / name)
    (consumer / "vendor").symlink_to(root / "vendor", target_is_directory=True)
    home = temp / "home"
    home.mkdir()
    bins = temp / "bin with spaces"
    bins.mkdir()
    absolute = bins / "etch"
    absolute.symlink_to(consumer / "etch")
    relative = bins / "relative"
    relative.symlink_to(os.path.relpath(consumer / "etch", bins))
    chain = bins / "chain"
    chain.symlink_to("relative")
    env = dict(
        os.environ,
        HOME=str(home),
        PATH=str(bins) + os.pathsep + os.environ.get("PATH", ""),
    )

    def run(command: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [command, *args],
            cwd=temp,
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
        )

    for launcher in (
        str(consumer / "etch"),
        str(absolute),
        str(relative),
        str(chain),
        "etch",
    ):
        for args in ((), ("validate",), ("plan", "--profile", "developer")):
            result = run(launcher, *args)
            assert result.returncode == 0, result.stdout + result.stderr
            if not args or args[0] == "plan":
                assert "Plan:" in result.stdout and str(consumer) in result.stdout, (
                    result.stdout
                )
        forwarded = run(launcher, "apply", "--profile", "does not exist")
        assert forwarded.returncode == 1, forwarded.stdout + forwarded.stderr
        assert "does not exist" in forwarded.stderr, forwarded.stderr
    assert not (home / ".gitconfig").exists(), (
        "Preview/validation mutated the user home"
    )
    for name, target in (
        ("dangling", "missing"),
        ("cycle-a", "cycle-b"),
        ("cycle-b", "cycle-a"),
    ):
        (bins / name).symlink_to(target)
    for name in ("dangling", "cycle-a"):
        result = subprocess.run(
            ["/bin/sh", str(bins / name)],
            cwd=temp,
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode != 0 and result.stderr, result.stdout + result.stderr
print(
    "Launcher checks passed: direct/PATH/symlinks, spaces, arguments, exit status, defaults and broken/cyclic links."
)
