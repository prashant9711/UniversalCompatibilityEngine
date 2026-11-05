import json
import sys
from pathlib import Path


def load_results(filename):
    data = json.loads(Path(filename).read_text(encoding="utf-8"))
    return {item["id"]: item for item in data}


def compare(reference, target):
    differences = []

    for case_id in sorted(set(reference) | set(target)):
        expected = reference.get(case_id)
        actual = target.get(case_id)

        if expected is None or actual is None:
            differences.append({
                "id": case_id,
                "reason": "Missing test case",
                "windows": expected,
                "target": actual,
            })
            continue

        fields = (
            ("success", "attributes")
            if expected["success"] and actual["success"]
            else ("success", "error_code")
        )

        for field in fields:
            if expected.get(field) != actual.get(field):
                differences.append({
                    "id": case_id,
                    "field": field,
                    "windows": expected.get(field),
                    "target": actual.get(field),
                })

    return differences


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/compare_results.py <windows.json> <target.json>")
        sys.exit(1)

    reference = load_results(sys.argv[1])
    target = load_results(sys.argv[2])

    differences = compare(reference, target)

    print(f"Compared {len(set(reference) | set(target))} scenarios")
    print(f"Differences found: {len(differences)}")

    for difference in differences:
        print(json.dumps(difference, indent=2))

    sys.exit(1 if differences else 0)


if __name__ == "__main__":
    main()