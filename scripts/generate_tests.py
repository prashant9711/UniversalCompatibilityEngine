import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "tests" / "filesystem_cases.json"

CASES = [
    {"id": "empty_path", "path": ""},
    {"id": "nonexistent_file", "path": "missing_file_92741.txt"},
    {"id": "relative_path", "path": "."},
    {"id": "parent_directory", "path": ".."},
    {"id": "windows_directory", "path": "C:\\Windows"},
    {"id": "system32_directory", "path": "C:\\Windows\\System32"},
    {"id": "unicode_path", "path": "测试文件.txt"},
    {"id": "long_filename", "path": "a" * 250 + ".txt"},
    {"id": "invalid_characters", "path": "invalid<>file.txt"},
    {"id": "trailing_space", "path": "example.txt "},
]

OUTPUT.parent.mkdir(exist_ok=True)

OUTPUT.write_text(
    json.dumps(CASES, indent=4, ensure_ascii=False),
    encoding="utf-8",
)

print(f"Generated {len(CASES)} filesystem test cases")