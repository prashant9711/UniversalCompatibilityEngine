import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "tests" / "filesystem_cases.json"
OUTPUT = ROOT / "results" / "filesystem_windows.json"


def probe(case):
    path = case["path"]

    try:
        info = os.stat(path)

        return {
            "id": case["id"],
            "success": True,
            "is_directory": os.path.isdir(path),
            "size": info.st_size,
        }

    except OSError as error:
        return {
            "id": case["id"],
            "success": False,
            "error_type": type(error).__name__,
            "winerror": getattr(error, "winerror", None),
        }


def main():
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    results = [probe(case) for case in cases]

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        json.dumps(results, indent=4),
        encoding="utf-8",
    )

    for result in results:
        status = "SUCCESS" if result["success"] else "ERROR"
        print(f"{result['id']:<25} {status}")

    print(f"\nResults saved to {OUTPUT}")


if __name__ == "__main__":
    main()