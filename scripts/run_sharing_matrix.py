import itertools
import json
import os
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
EXE = ROOT / "probes" / "sharing_matrix.exe"

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000

ACCESS = {
    "read": GENERIC_READ,
    "write": GENERIC_WRITE,
}

SHARE = {
    "none": 0,
    "read": 1,
    "write": 2,
    "read_write": 3,
}

def main():
    is_windows = platform.system() == "Windows"
    environment = "native" if is_windows else "wine"

    results = {}

    for (access1, value1), (share1, share_value1), \
        (access2, value2), (share2, share_value2) in itertools.product(
            ACCESS.items(), SHARE.items(),
            ACCESS.items(), SHARE.items()
        ):

        test_id = f"{access1}_{share1}__{access2}_{share2}"

        command = [
            str(EXE),
            r"fixtures\existing.txt",
            str(value1),
            str(share_value1),
            str(value2),
            str(share_value2),
        ]

        if not is_windows:
            command.insert(0, "wine")

        try:
            process = subprocess.run(
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
            results[test_id] = json.loads(process.stdout)

        except Exception as exc:
            results[test_id] = {"execution_error": str(exc)}

    RESULTS.mkdir(exist_ok=True)

    output = RESULTS / f"{environment}_sharing_matrix.json"
    output.write_text(
        json.dumps(results, indent=4),
        encoding="utf-8",
    )

    print(f"Environment: {environment}")
    print(f"Tests executed: {len(results)}")
    print(f"Execution errors: {sum('execution_error' in r for r in results.values())}")
    print(f"Saved: {output}")

if __name__ == "__main__":
    main()