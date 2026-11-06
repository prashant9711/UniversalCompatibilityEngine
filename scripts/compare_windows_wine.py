import json
import os
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

TESTS = {
    "GetFileAttributesW": {
        "executable": "file_attributes.exe",
        "paths": [
            "fixtures\\existing.txt",
            "fixtures\\EXISTING.TXT",
            "fixtures\\folder\\nested.txt",
            "fixtures\\missing.txt",
            "invalid<>file.txt",
        ],
    },
    "CreateFileW": {
        "executable": "create_file.exe",
        "paths": [
            "fixtures\\existing.txt",
            "fixtures\\empty.txt",
            "fixtures\\folder\\nested.txt",
            "fixtures\\missing.txt",
            "invalid<>file.txt",
        ],
    },
    "FileSharing": {
    "executable": "file_sharing.exe",
    "paths": [
        "fixtures\\existing.txt",
        "fixtures\\empty.txt",
        "fixtures\\folder\\nested.txt",
        "fixtures\\missing.txt",
    ],
    },
}


def run_probe(executable, path, is_windows):
    exe = ROOT / "probes" / executable

    command = (
        [str(exe), path]
        if is_windows
        else ["wine", str(exe), path]
    )

    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
        check=True,
        env={
            **os.environ,
            **({} if is_windows else {"WINEDEBUG": "-all"}),
        },
    )

    return json.loads(result.stdout)


def main():
    is_windows = platform.system() == "Windows"
    environment = "native" if is_windows else "wine"

    results = {}

    for api, config in TESTS.items():
        results[api] = {}

        for path in config["paths"]:
            try:
                results[api][path] = run_probe(
                    config["executable"], path, is_windows
                )
            except Exception as exc:
                results[api][path] = {
                    "execution_error": str(exc)
                }

    RESULTS.mkdir(exist_ok=True)

    output = RESULTS / f"{environment}_multi_api.json"
    output.write_text(
        json.dumps(results, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Environment: {environment}")
    print(f"APIs tested: {len(TESTS)}")
    print(f"Total tests: {sum(len(v) for v in results.values())}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()