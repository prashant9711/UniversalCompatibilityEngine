import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINE = os.environ.get("UCE_WINE_BINARY", "wine")
PROBE = ROOT / "probes/test_replace_casing.exe"


class TestWineReplacementCasing(unittest.TestCase):
    def run_replacement(self, mode, expected_name):
        with tempfile.TemporaryDirectory() as directory:
            windows_path = "Z:" + directory.replace("/", chr(92))

            result = subprocess.run(
                [WINE, str(PROBE), windows_path, mode],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "WINEDEBUG": "-all"},
            )

            self.assertEqual(result.returncode, 0, result.stderr)

            data = json.loads(result.stdout.strip().splitlines()[-1])
            self.assertTrue(data["rename_success"], data)
            self.assertEqual(data["error"], 0)
            self.assertEqual(data["actual_name"], expected_name)

            files = list(Path(directory).iterdir())
            self.assertEqual(len(files), 1, files)
            self.assertEqual(files[0].name, expected_name)
            self.assertEqual(files[0].read_text(), "SOURCE_DATA_123")

    def test_different_casing(self):
        self.run_replacement("different", "TARGET.txt")

    def test_matching_casing(self):
        self.run_replacement("matching", "target.txt")


if __name__ == "__main__":
    unittest.main()
