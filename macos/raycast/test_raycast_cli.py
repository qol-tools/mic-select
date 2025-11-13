#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

CLI_SCRIPT = Path(__file__).parent / "raycast_cli.py"


def run_cli(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(CLI_SCRIPT)] + args,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def test_cli_list_command():
    exit_code, stdout, stderr = run_cli(["list", "--limit", "5"])

    assert exit_code == 0, f"Expected exit code 0, got {exit_code}. stderr: {stderr}"

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}\nOutput: {stdout}")

    assert "sources" in data, f"Missing 'sources' key in output: {data}"
    assert isinstance(data["sources"], list), "sources should be a list"

    for source in data["sources"]:
        assert "name" in source, f"Source missing 'name' field: {source}"
        assert "index" in source, f"Source missing 'index' field: {source}"
        assert isinstance(source["name"], str), "name should be a string"
        assert isinstance(source["index"], int), "index should be an integer"

    print(f"✓ list command test passed. Found {len(data['sources'])} sources")


def test_cli_list_with_query():
    exit_code, stdout, stderr = run_cli(["list", "--query", "mic", "--limit", "10"])

    assert exit_code == 0, f"Expected exit code 0, got {exit_code}. stderr: {stderr}"

    data = json.loads(stdout)
    assert "sources" in data
    print(f"✓ list with query test passed. Found {len(data['sources'])} sources")


def test_cli_list_limit():
    exit_code, stdout, stderr = run_cli(["list", "--limit", "3"])

    assert exit_code == 0, f"Expected exit code 0, got {exit_code}. stderr: {stderr}"

    data = json.loads(stdout)
    assert len(data["sources"]) <= 3, f"Expected max 3 sources, got {len(data['sources'])}"
    print(f"✓ list limit test passed. Got {len(data['sources'])} sources (max 3)")


def test_cli_switch_command_validation():
    exit_code, stdout, stderr = run_cli(["switch"])

    assert exit_code != 0, "Expected non-zero exit code for switch without --name"
    print("✓ switch validation test passed")


def test_cli_switch_command():
    exit_code, stdout, stderr = run_cli(["list", "--limit", "1"])
    assert exit_code == 0, "Failed to get list of sources"

    data = json.loads(stdout)
    if not data["sources"]:
        print("⊘ Skipping switch test - no audio sources available")
        return

    source_name = data["sources"][0]["name"]
    exit_code, stdout, stderr = run_cli(["switch", "--name", source_name])

    assert exit_code == 0, f"Expected exit code 0, got {exit_code}. stderr: {stderr}"

    try:
        result = json.loads(stdout)
    except json.JSONDecodeError:
        if '"error"' in stdout or '"success": false' in stdout:
            print(f"⊘ Switch test - source unavailable: {source_name}")
            return
        raise

    assert "success" in result or "error" in result, f"Unexpected response format: {result}"

    if "success" in result:
        assert isinstance(result["success"], bool), "success should be boolean"
        print(f"✓ switch command test passed. Switched to: {source_name}")
    else:
        print(f"⊘ Switch returned error (expected for some sources): {result.get('error')}")


def test_cli_no_command():
    exit_code, stdout, stderr = run_cli([])

    assert exit_code != 0, "Expected non-zero exit code when no command provided"
    assert "error" in stdout.lower() or "usage" in stderr.lower() or "no command" in stdout.lower(), \
        f"Expected error message, got: stdout={stdout}, stderr={stderr}"
    print("✓ no command test passed")


def test_cli_invalid_command():
    exit_code, stdout, stderr = run_cli(["invalid_command"])

    assert exit_code != 0, "Expected non-zero exit code for invalid command"
    print("✓ invalid command test passed")


def test_json_output_format():
    exit_code, stdout, stderr = run_cli(["list", "--limit", "1"])

    assert exit_code == 0

    data = json.loads(stdout)

    assert stdout.strip().startswith("{") or stdout.strip().startswith("["), \
        "Output should start with JSON"
    assert stdout.strip().endswith("}") or stdout.strip().endswith("]"), \
        "Output should end with JSON"

    print("✓ JSON format test passed")


def main():
    tests = [
        test_cli_list_command,
        test_cli_list_with_query,
        test_cli_list_limit,
        test_cli_switch_command_validation,
        test_cli_switch_command,
        test_cli_no_command,
        test_cli_invalid_command,
        test_json_output_format,
    ]

    print(f"Running {len(tests)} tests for raycast_cli.py\n")

    passed = 0
    failed = 0

    for test in tests:
        try:
            print(f"Running {test.__name__}...")
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
        print()

    print(f"\n{'='*60}")
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print(f"{'='*60}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
