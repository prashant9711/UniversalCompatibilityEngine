import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "tests" / "applications.json"
OUTPUT = ROOT / "results" / "batch_windows.json"


def run_test(test):
    command = [test["executable"], *test.get("args", [])]
    start = time.perf_counter()

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=30,
            check=False,
        )

        checks = {
            "exit_code": result.returncode == test["expected_exit_code"]
        }

        if "expected_stdout_contains" in test:
            checks["stdout_contains"] = (
                test["expected_stdout_contains"] in result.stdout
            )

        if test.get("expected_stdout_nonempty"):
            checks["stdout_nonempty"] = bool(result.stdout.strip())

        passed = all(checks.values())

        return {
            "id": test["id"],
            "status": "PASS" if passed else "FAIL",
            "checks": checks,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": time.perf_counter() - start,
        }

    except (OSError, subprocess.TimeoutExpired) as error:
        return {
            "id": test["id"],
            "status": "ERROR",
            "error": str(error),
            "execution_time": time.perf_counter() - start,
        }

def main():
    tests = json.loads(CONFIG.read_text(encoding="utf-8"))["tests"]
    results = [run_test(test) for test in tests]

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(results, indent=4), encoding="utf-8")

    print("\nUniversal Compatibility Engine - Windows Tests")
    print("=" * 50)

    for result in results:
        print(f"{result['id']:<20} {result['status']}")

    print(f"\nResults saved to {OUTPUT}")


if __name__ == "__main__":
    main()