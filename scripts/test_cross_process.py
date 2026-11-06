import json
import os
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
IS_WINDOWS = platform.system() == "Windows"

ENV = os.environ.copy()
if not IS_WINDOWS:
    ENV["WINEDEBUG"] = "-all"


def command(executable):
    exe = str(ROOT / "probes" / executable)
    return [exe] if IS_WINDOWS else ["wine", exe]


def run():
    path = r"fixtures\existing.txt"

    holder = subprocess.Popen(
        command("hold_file.exe") + [path],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=ENV,
    )

    try:
        # Wait until the first process confirms it holds the file.
        ready_line = holder.stdout.readline()
        ready = json.loads(ready_line)

        if ready.get("success") is not True:
            raise RuntimeError(f"Holder failed: {ready}")

        # Attempt to open the file while the holder is active.
        blocked = subprocess.run(
            command("create_file.exe") + [path],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
            env=ENV,
        )

        blocked_result = json.loads(blocked.stdout)

    finally:
        # Release the file by terminating the holder.
        if holder.poll() is None:
            holder.terminate()
        holder.communicate(timeout=10)

    # Confirm the file can be opened after the holder exits.
    released = subprocess.run(
        command("create_file.exe") + [path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
        env=ENV,
    )

    released_result = json.loads(released.stdout)

    result = {
        "blocked": blocked_result,
        "released": released_result,
    }

    environment = "native" if IS_WINDOWS else "wine"
    RESULTS.mkdir(exist_ok=True)

    output = RESULTS / f"{environment}_cross_process.json"
    output.write_text(json.dumps(result, indent=4), encoding="utf-8")

    print(f"Environment: {environment}")
    print(f"Blocked: {blocked_result}")
    print(f"Released: {released_result}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    run()