import ctypes
import json
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "tests" / "controlled_cases.json"
OUTPUT = ROOT / "results" / "controlled_windows.json"
FIXTURES = ROOT / "fixtures"

INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

GetFileAttributesW = kernel32.GetFileAttributesW
GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
GetFileAttributesW.restype = wintypes.DWORD


def probe(case):
    path = case["path"]

    if case["id"] not in ("relative_directory", "parent_directory"):
        path = str(FIXTURES / path)
    else:
        path = str(FIXTURES / path)

    ctypes.set_last_error(0)
    attributes = GetFileAttributesW(path)

    if attributes == INVALID_FILE_ATTRIBUTES:
        return {
            "id": case["id"],
            "success": False,
            "error_code": ctypes.get_last_error(),
        }

    return {
        "id": case["id"],
        "success": True,
        "attributes": attributes,
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