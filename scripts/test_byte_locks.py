import json
import os
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = platform.system() == "Windows"
ENVIRONMENT = "native" if IS_WINDOWS else "wine"

ENV = os.environ.copy()
if not IS_WINDOWS:
    ENV["WINEDEBUG"] = "-all"

EXE = str(ROOT / "probes" / "byte_lock.exe")
PATH = r"fixtures\existing.txt"


def command(offset, length, hold_ms):
    args = [EXE, PATH, str(offset), str(length), str(hold_ms)]
    return args if IS_WINDOWS else ["wine", *args]


def test_lock(name, second_offset):
    holder = subprocess.Popen(
        command(0, 100, 15000),
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=ENV,
    )

    try:
        ready_line = holder.stdout.readline()
        if not ready_line:
            raise RuntimeError("Holder exited without producing output")

        ready = json.loads(ready_line)

        if ready.get("lock_success") is not True:
            raise RuntimeError(f"First lock failed: {ready}")

        second = subprocess.run(
            command(second_offset, 100, 0),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
            env=ENV,
        )

        result = json.loads(second.stdout)

        if holder.poll() is not None:
            raise RuntimeError("First process exited before comparison")

        return result

    finally:
        if holder.poll() is None:
            holder.terminate()

        try:
            holder.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            holder.kill()
            holder.communicate()


results = {
    "overlapping": test_lock("overlapping", 50),
    "non_overlapping": test_lock("non_overlapping", 100),
}

output = ROOT / "results" / f"{ENVIRONMENT}_byte_locks.json"
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(results, indent=4), encoding="utf-8")

print(f"Environment: {ENVIRONMENT}")
for name, result in results.items():
    print(f"{name}: {result}")
print(f"Saved: {output}")