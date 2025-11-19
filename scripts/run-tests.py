#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path


def has_python_tests(target: Path) -> bool:
    """Check if directory has Python test indicators."""
    return (
        (target / "requirements.txt").exists()
        or (target / "pyproject.toml").exists()
        or (target / "pytest.ini").exists()
        or any(target.glob("test_*.py"))
        or (target / "tests").is_dir()
    )


def has_test_config(target: Path) -> bool:
    """Check if directory has any test configuration."""
    return (
        (target / "package.json").exists()
        or (target / "pytest.ini").exists()
        or (target / "tests").is_dir()
        or (target / "Makefile").exists()
    )


def should_skip_dir(path: Path) -> bool:
    """Check if directory should be skipped based on platform."""
    if sys.platform == "linux" and path.name == "macos":
        return True
    if sys.platform == "darwin" and path.name == "linux":
        return True
    return False


def discover_and_run_subdirs(target: Path) -> int:
    """Discover and run tests in subdirectories."""
    subdirs = [d for d in target.iterdir() if d.is_dir() and not d.name.startswith(".")]

    if not subdirs:
        print("❌ No tests found.")
        return 1

    exit_code = 0
    for sub in sorted(subdirs):
        if should_skip_dir(sub):
            continue

        if not has_test_config(sub):
            continue

        print(f"\n📂 Entering {sub.name}...")
        code = run_tests(sub, recurse=True)
        if code != 0:
            exit_code = code

    return exit_code


def run_python_tests(target: Path, recurse: bool) -> int:
    """Run Python tests and optionally recurse into subdirs."""
    print(f"► [Python] Running pytest in {target.name}...")
    exit_code = subprocess.run([sys.executable, "-m", "pytest", "-v"], cwd=target).returncode

    if not recurse:
        return exit_code

    subdirs = [d for d in target.iterdir() if d.is_dir() and not d.name.startswith(".")]
    for sub in sorted(subdirs):
        if should_skip_dir(sub):
            continue

        if not has_test_config(sub):
            continue

        print(f"\n📂 Entering {sub.name}...")
        code = run_tests(sub, recurse=True)
        if code != 0:
            exit_code = code

    return exit_code


def run_tests(target: Path, recurse: bool = True) -> int:
    """Detect project type and run appropriate tests."""
    target = target.resolve()

    if not target.exists():
        print(f"❌ Error: Directory '{target}' does not exist.")
        return 1

    if (target / "package.json").exists():
        print(f"► [Node] Running tests in {target.name}...")
        return subprocess.run(["npm", "test"], cwd=target).returncode

    if (target / "Cargo.toml").exists():
        print(f"► [Rust] Running tests in {target.name}...")
        return subprocess.run(["cargo", "test"], cwd=target).returncode

    if (target / "go.mod").exists():
        print(f"► [Go] Running tests in {target.name}...")
        return subprocess.run(["go", "test", "./..."], cwd=target).returncode

    if has_python_tests(target):
        return run_python_tests(target, recurse)

    if (target / "test.sh").exists():
        print(f"► [Script] Running ./test.sh in {target.name}...")
        return subprocess.run(["./test.sh"], cwd=target).returncode

    if (target / "Makefile").exists() and target != Path.cwd():
        print(f"► [Make] Delegating to Makefile in {target.name}...")
        return subprocess.run(["make", "test"], cwd=target).returncode

    print(f"ℹ️  No config found in {target.name}, searching subdirectories...")
    return discover_and_run_subdirs(target)


def parse_args(args: list[str]) -> tuple[Path, list[Path]]:
    """Parse command line arguments into base dir and targets."""
    if not args:
        return Path("."), []

    base_dir = Path(args[0])
    if not base_dir.exists():
        print(f"❌ Error: Directory '{args[0]}' does not exist.")
        sys.exit(1)

    if len(args) == 1:
        return base_dir, []

    targets = []
    for subdir in args[1:]:
        target = base_dir / subdir
        if not target.exists():
            print(f"❌ Error: Directory '{target}' does not exist.")
            sys.exit(1)
        targets.append(target)

    return base_dir, targets


def run_single_target(target: Path, recurse: bool = False) -> int:
    """Run tests for a single target directory."""
    print(f"\n{'='*60}")
    try:
        rel_path = target.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        rel_path = target
    print(f"Testing: {rel_path}")
    print("=" * 60)
    return run_tests(target, recurse=recurse)


def main() -> int:
    """Main entry point."""
    base_dir, targets = parse_args(sys.argv[1:])

    if not targets:
        return run_tests(base_dir, recurse=True)

    exit_code = 0
    for target in targets:
        code = run_single_target(target, recurse=False)
        if code != 0:
            exit_code = code

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
