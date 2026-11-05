import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"
OUTPUT = ROOT / "tests" / "controlled_cases.json"


def main():
    if FIXTURES.exists():
        shutil.rmtree(FIXTURES)

    FIXTURES.mkdir(parents=True)

    (FIXTURES / "existing.txt").write_text(
        "Universal Compatibility Engine\n",
        encoding="utf-8",
    )

    (FIXTURES / "empty.txt").touch()

    (FIXTURES / "folder").mkdir()

    (FIXTURES / "folder" / "nested.txt").write_text(
        "Nested file\n",
        encoding="utf-8",
    )

    (FIXTURES / "unicode_测试.txt").write_text(
        "Unicode test\n",
        encoding="utf-8",
    )

    cases = [
        {"id": "existing_file", "path": "existing.txt"},
        {"id": "empty_file", "path": "empty.txt"},
        {"id": "existing_directory", "path": "folder"},
        {"id": "nested_file", "path": "folder/nested.txt"},
        {"id": "unicode_file", "path": "unicode_测试.txt"},
        {"id": "missing_file", "path": "missing.txt"},
        {"id": "missing_directory", "path": "missing/file.txt"},
        {"id": "relative_directory", "path": "."},
        {"id": "parent_directory", "path": ".."},
        {"id": "invalid_characters", "path": "invalid<>file.txt"},
    ]

    OUTPUT.parent.mkdir(exist_ok=True)

    OUTPUT.write_text(
        json.dumps(cases, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Created {len(cases)} controlled test cases")
    print(f"Fixtures: {FIXTURES}")


if __name__ == "__main__":
    main()