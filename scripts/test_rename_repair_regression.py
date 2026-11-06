import json
import os
import platform
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = platform.system() == "Windows"
ENVIRONMENT = "native" if IS_WINDOWS else "wine"

ENV = os.environ.copy()
if not IS_WINDOWS:
    ENV["WINEDEBUG"] = "-all"


def run_probe(executable, directory):
    exe = str(ROOT / "probes" / executable)
    command = [exe, directory] if IS_WINDOWS else ["wine", exe, directory]

    process = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
        env=ENV,
    )

    return json.loads(process.stdout)


def windows_path(directory):
    if IS_WINDOWS:
        return directory
    return "Z:" + directory.replace("/", "\\")


def main():
    with tempfile.TemporaryDirectory(prefix="uce_original_") as original_dir:
        original = run_probe(
            "case_rename.exe",
            windows_path(original_dir),
        )

        original_filename = run_probe(
            "query_filename.exe",
            windows_path(original_dir) + r"\testfile.txt",
        )

    with tempfile.TemporaryDirectory(prefix="uce_repaired_") as repaired_dir:
        repaired = run_probe(
            "test_uce_rename.exe",
            windows_path(repaired_dir),
        )

    result = {
        "original": {
            "rename": original,
            "query": original_filename,
        },
        "repaired": repaired,
    }

    output = ROOT / "results" / f"{ENVIRONMENT}_rename_repair.json"
    output.parent.mkdir(exist_ok=True)

    output.write_text(
        json.dumps(result, indent=4),
        encoding="utf-8",
    )

    print(f"Environment: {ENVIRONMENT}")
    print(f"Original filename: {original_filename.get('actual_name')}")
    print(f"Repaired filename: {repaired.get('actual_name')}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()