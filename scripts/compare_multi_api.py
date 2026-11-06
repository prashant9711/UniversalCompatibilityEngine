import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

native = json.loads(
    (RESULTS / "native_multi_api.json").read_text(encoding="utf-8")
)
wine = json.loads(
    (RESULTS / "wine_multi_api.json").read_text(encoding="utf-8")
)

report = {
    "total": 0,
    "matches": 0,
    "mismatches": [],
    "execution_errors": [],
    "by_api": {},
}

for api in sorted(set(native) | set(wine)):
    native_cases = native.get(api, {})
    wine_cases = wine.get(api, {})

    api_matches = 0
    api_mismatches = 0

    for path in sorted(set(native_cases) | set(wine_cases)):
        expected = native_cases.get(path)
        actual = wine_cases.get(path)

        report["total"] += 1

        if (
            expected is None
            or actual is None
            or "execution_error" in expected
            or "execution_error" in actual
        ):
            report["execution_errors"].append({
                "api": api,
                "path": path,
                "windows": expected,
                "wine": actual,
            })
        elif expected == actual:
            report["matches"] += 1
            api_matches += 1
        else:
            report["mismatches"].append({
                "api": api,
                "path": path,
                "windows": expected,
                "wine": actual,
            })
            api_mismatches += 1

    report["by_api"][api] = {
        "matches": api_matches,
        "mismatches": api_mismatches,
    }

output = RESULTS / "multi_api_differences.json"
output.write_text(
    json.dumps(report, indent=4, ensure_ascii=False),
    encoding="utf-8",
)

print(f"Total tests: {report['total']}")
print(f"Matches: {report['matches']}")
print(f"Mismatches: {len(report['mismatches'])}")
print(f"Execution errors: {len(report['execution_errors'])}")

for api, counts in report["by_api"].items():
    print(f"\n{api}:")
    print(f"  Matches: {counts['matches']}")
    print(f"  Mismatches: {counts['mismatches']}")

for item in report["mismatches"]:
    print(f"\nMismatch: {item['api']} — {item['path']!r}")
    print(f"  Windows: {item['windows']}")
    print(f"  Wine:    {item['wine']}")

for item in report["execution_errors"]:
    print(f"\nExecution issue: {item['api']} — {item['path']!r}")
    print(f"  Windows: {item['windows']}")
    print(f"  Wine:    {item['wine']}")