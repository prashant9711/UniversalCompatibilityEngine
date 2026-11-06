import json
import os
import platform
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = platform.system() == "Windows"

CASES = [
    ("Report.TXT", "report.txt"),
    ("DATA.json", "data.JSON"),
    ("HelloWorld.txt", "helloworld.txt"),
    ("UPPERCASE.TXT", "uppercase.txt"),
    ("mixedCase.log", "MIXEDCASE.LOG"),
]

def main():
    results = []

    for original, target in CASES:
        with tempfile.TemporaryDirectory(prefix="uce_matrix_") as directory:
            windows_dir = (
                directory if IS_WINDOWS
                else "Z:" + directory.replace("/", "\\")
            )

            exe = str(ROOT / "probes" / "test_generic_rename.exe")

            command = (
                [exe, windows_dir, original, target]
                if IS_WINDOWS
                else ["wine", exe, windows_dir, original, target]
            )

            env = os.environ.copy()
            env["WINEDEBUG"] = "-all"

            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=env,
                timeout=30,
            )

            try:
                result = json.loads(process.stdout)
            except json.JSONDecodeError:
                result = {"error": process.stderr}

            actual = result.get("actual_name")
            passed = (
                process.returncode == 0
                and result.get("rename_success") is True
                and actual == target
                and (Path(directory) / target).is_file()
            )

            results.append({
                "original": original,
                "target": target,
                "actual": actual,
                "passed": passed,
            })

            print(
                f"{'PASS' if passed else 'FAIL'}: "
                f"{original} -> {target} "
                f"(actual: {actual})"
            )

    environment = "native" if IS_WINDOWS else "wine"
    output = ROOT / "results" / f"{environment}_generic_rename_matrix.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")

    passed_count = sum(r["passed"] for r in results)
    print(f"\n{passed_count}/{len(results)} passed")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()