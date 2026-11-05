import subprocess
import json
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def test_application(executable, args=None):
    args = args or []
    command = [str(executable), *args]

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

        return {
            "application": str(executable),
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": time.perf_counter() - start,
        }

    except subprocess.TimeoutExpired:
        return {
            "application": str(executable),
            "error": "Timeout",
            "execution_time": time.perf_counter() - start,
        }

    except OSError as error:
        return {
            "application": str(executable),
            "error": str(error),
            "execution_time": time.perf_counter() - start,
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_runner.py <application> [args...]")
        sys.exit(1)

    executable = Path(sys.argv[1]).resolve()
    result = test_application(executable, sys.argv[2:])

    output = RESULTS / "windows.json"
    output.write_text(json.dumps(result, indent=4), encoding="utf-8")

    print(json.dumps(result, indent=4))