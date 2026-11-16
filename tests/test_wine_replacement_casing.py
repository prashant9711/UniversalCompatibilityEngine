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
    def test_replacement_preserves_data_without_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            windows_path = "Z:" + directory.replace("/", "\\")

            result = subprocess.run(
                [WINE, str(PROBE), windows_path],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "WINEDEBUG": "-all"},
            )

            self.assertEqual(result.returncode, 0, result.stderr)

            data = json.loads(result.stdout.strip().splitlines()[-1])
            self.assertTrue(data["rename_success"], data)

            files = list(Path(directory).iterdir())
            self.assertEqual(len(files), 1, files)
            self.assertEqual(files[0].read_text(), "SOURCE_DATA_123")
            self.assertEqual(files[0].name.lower(), "target.txt")
            self.assertEqual(
                data["actual_name"],
                files[0].name,
                "Wine's reported filename differs from the actual filename"
            )


if __name__ == "__main__":
    unittest.main()
