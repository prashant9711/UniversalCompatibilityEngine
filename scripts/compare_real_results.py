import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

native = json.loads(
    (RESULTS / "native_probe.json").read_text(encoding="utf-8")
)

wine = json.loads(
    (RESULTS / "wine_probe.json").read_text(encoding="utf-8")
)

matches = []
mismatches = []

for path in sorted(set(native) | set(wine)):
    expected = native.get(path)
    actual = wine.get(path)

    if expected == actual:
        matches.append(path)
    else:
        mismatches.append({
            "path": path,
            "windows": expected,
            "wine": actual,
        })

report = {
    "total": len(set(native) | set(wine)),
    "matches": len(matches),
    "mismatches": mismatches,
}

output = RESULTS / "real_differences.json"
output.write_text(
    json.dumps(report, indent=4, ensure_ascii=False),
    encoding="utf-8",
)

print(f"Total cases: {report['total']}")
print(f"Matches: {report['matches']}")
print(f"Mismatches: {len(mismatches)}")

for item in mismatches:
    print(f"\nPath: {item['path']!r}")
    print(f"  Windows: {item['windows']}")
    print(f"  Wine:    {item['wine']}")