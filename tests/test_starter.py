"""Independent consumer copy, recursive clone, and Python-only runtime."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StarterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="etch consumer ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git_command = shutil.which("git")
        self.assertIsNotNone(self.git_command, "Git is required to construct fixtures")
        self.git_env = dict(
            os.environ,
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_NAME="Template test",
            GIT_AUTHOR_EMAIL="test@example.invalid",
            GIT_COMMITTER_NAME="Template test",
            GIT_COMMITTER_EMAIL="test@example.invalid",
        )
        self.bin = self.root / "bin"
        self.bin.mkdir()
        (self.bin / "python3").symlink_to(
            Path(getattr(sys, "_base_executable", sys.executable)).resolve()
        )
        self.home = self.root / "home"
        self.home.mkdir()
        self.env = dict(os.environ, PATH=str(self.bin), HOME=str(self.home), PYTHONNOUSERSITE="1")
        for key in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
            self.env.pop(key, None)

    def git(self, cwd: Path, *args: str) -> str:
        return subprocess.run(
            [self.git_command, "-c", "protocol.file.allow=always", "-c", "core.hooksPath=/dev/null", *args],
            cwd=cwd, env=self.git_env, check=True, capture_output=True, text=True,
        ).stdout.strip()

    def consumer(self) -> Path:
        # Preserve the Git tree/gitlink but create unrelated consumer history.
        source = self.root / "new consumer"
        self.git(self.root, "clone", "--no-hardlinks", str(ROOT), str(source))
        self.git(source, "checkout", "--orphan", "consumer-main")
        self.git(source, "commit", "-m", "Own the template files")
        self.git(source, "remote", "remove", "origin")
        self.assertEqual(self.git(source, "rev-list", "--count", "HEAD"), "1")
        expected = self.git(ROOT, "rev-parse", "HEAD:vendor/etch")
        self.assertEqual(self.git(source, "rev-parse", "HEAD:vendor/etch"), expected)
        mirror = self.root / "engine.git"
        self.git(self.root, "clone", "--bare", str(ROOT / "vendor/etch"), str(mirror))
        clone = self.root / "recursive clone"
        # Fixture-only URL rewrite avoids network without changing .gitmodules.
        self.git(self.root, "-c", "url.{}.insteadOf=https://github.com/rm-industries/etch.git".format(mirror.as_uri()), "clone", "--recurse-submodules", str(source), str(clone))
        self.assertEqual(self.git(clone / "vendor/etch", "rev-parse", "HEAD"), expected)
        return clone

    def run_install(self, consumer: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(consumer / "install"), *args], cwd=self.root, env=self.env,
            capture_output=True, text=True, timeout=30,
        )

    def test_consumer_clone_plan_apply_and_second_run(self) -> None:
        consumer = self.consumer()
        plan = self.run_install(consumer)
        self.assertEqual(plan.returncode, 0, plan.stderr)
        self.assertIn("CHANGE", plan.stdout)
        self.assertFalse((self.home / ".gitconfig").exists())
        first = self.run_install(consumer, "apply", "--profile", "developer")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual((self.home / ".gitconfig").resolve(), consumer / "modules/git/files/gitconfig")
        second = self.run_install(consumer, "apply", "--profile", "developer")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("SKIPPED", second.stdout)
        self.assertNotIn("CHANGED", second.stdout)
        result = self.run_install(consumer, "doctor", "missing module")
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing modules: missing module", result.stderr)
        result = self.run_install(consumer, "--unknown-option")
        self.assertEqual(result.returncode, 2)

    def test_missing_engine_is_actionable(self) -> None:
        consumer = self.root / "uninitialized"
        consumer.mkdir()
        shutil.copy2(ROOT / "install", consumer / "install")
        result = self.run_install(consumer)
        self.assertEqual(result.returncode, 1)
        self.assertIn("git submodule update --init --recursive", result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
