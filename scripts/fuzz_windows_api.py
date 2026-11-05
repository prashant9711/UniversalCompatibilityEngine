import ctypes
import json
import random
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"
OUTPUT = ROOT / "results" / "fuzz_windows.json"

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
api = kernel32.GetFileAttributesW
api.argtypes = [wintypes.LPCWSTR]
api.restype = wintypes.DWORD

INVALID_ATTRIBUTES = 0xFFFFFFFF

SEED = 42
TEST_COUNT = 100

BASE_PATHS = [
    "existing.txt",
    "empty.txt",
    "folder",
    "folder/nested.txt",
    "unicode_测试.txt",
    "missing.txt",
]

SUFFIXES = [
    "",
    ".",
    " ",
    "..",
    "/",
    "\\",
    ":",
    "*",
    "?",
]


def generate_cases():
    rng = random.Random(SEED)
    cases = []

    for index in range(TEST_COUNT):
        base = rng.choice(BASE_PATHS)
        suffix = rng.choice(SUFFIXES)

        cases.append({
            "id": f"fuzz_{index:04d}",
            "base": base,
            "suffix": suffix,
            "path": base + suffix,
        })

    return cases


def probe(case):
    path = str(FIXTURES / case["path"])

    ctypes.set_last_error(0)
    attributes = api(path)

    result = {
        **case,
        "success": attributes != INVALID_ATTRIBUTES,
    }

    if result["success"]:
        result["attributes"] = attributes
    else:
        result["error_code"] = ctypes.get_last_error()

    return result


def main():
    cases = generate_cases()
    results = [probe(case) for case in cases]

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        json.dumps(results, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    successful = sum(result["success"] for result in results)

    print(f"Seed: {SEED}")
    print(f"Generated tests: {len(results)}")
    print(f"Successful API calls: {successful}")
    print(f"API errors: {len(results) - successful}")
    print(f"Results saved to {OUTPUT}")


if __name__ == "__main__":
    main()