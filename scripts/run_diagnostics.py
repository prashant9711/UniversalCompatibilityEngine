import ctypes
import json
import os
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"

CASES = ROOT / "tests" / "controlled_cases.json"
EXPERIMENTS = ROOT / "tests" / "diagnostic_cases.json"
OUTPUT = ROOT / "results" / "diagnostic_results.json"

INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

GetFileAttributesW = kernel32.GetFileAttributesW
GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
GetFileAttributesW.restype = wintypes.DWORD


def build_path(original, variant):
    absolute = FIXTURES / original

    if variant == "absolute_path":
        return str(absolute.resolve())

    if variant == "relative_path":
        return os.path.relpath(absolute, ROOT)

    if variant == "forward_slash":
        return str(absolute).replace("\\", "/")

    if variant == "backslash":
        return str(absolute).replace("/", "\\")

    raise ValueError(f"Unknown variant: {variant}")


def execute(experiment, cases):
    source = cases[experiment["source_case"]]

    path = build_path(source["path"], experiment["variant"])

    ctypes.set_last_error(0)
    attributes = GetFileAttributesW(path)

    result = {
        "id": experiment["id"],
        "source_case": experiment["source_case"],
        "variant": experiment["variant"],
        "path": path,
    }

    if attributes == INVALID_FILE_ATTRIBUTES:
        result["success"] = False
        result["error_code"] = ctypes.get_last_error()
    else:
        result["success"] = True
        result["attributes"] = attributes

    return result


def main():
    cases = {
        case["id"]: case
        for case in json.loads(CASES.read_text(encoding="utf-8"))
    }

    experiments = json.loads(
        EXPERIMENTS.read_text(encoding="utf-8")
    )

    # Relative paths are interpreted relative to the process directory.
    os.chdir(ROOT)

    results = [execute(experiment, cases) for experiment in experiments]

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        json.dumps(results, indent=4),
        encoding="utf-8",
    )

    for result in results:
        status = "SUCCESS" if result["success"] else "ERROR"
        print(f"{result['id']:<35} {status}")

    print(f"\nResults saved to {OUTPUT}")


if __name__ == "__main__":
    main()