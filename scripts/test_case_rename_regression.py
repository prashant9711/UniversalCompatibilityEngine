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


def run_probe(executable, path):
    exe = str(ROOT / "probes" / executable)
    command = [exe, path] if IS_WINDOWS else ["wine", exe, path]

    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
        env=ENV,
    )
    return json.loads(result.stdout)


def main():
    with tempfile.TemporaryDirectory(prefix="compat_case_") as directory:
        if IS_WINDOWS:
            windows_directory = directory
        else:
            # Wine's Z: drive maps to the Linux filesystem root.
            windows_directory = "Z:" + directory.replace("/", "\\")

        rename = run_probe("case_rename.exe", windows_directory)

        query = run_probe(
            "query_filename.exe",
            windows_directory + r"\testfile.txt",
        )

        result = {
            "rename": rename,
            "query": query,
        }

    output = ROOT / "results" / f"{ENVIRONMENT}_case_rename.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=4), encoding="utf-8")

    print(f"Environment: {ENVIRONMENT}")
    print(f"Rename: {rename}")
    print(f"Query: {query}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()