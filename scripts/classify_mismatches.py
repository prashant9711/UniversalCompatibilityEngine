import json
import sys
from pathlib import Path


def load_results(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {item["id"]: item for item in data}


def classify(reference, target):
    mismatches = []

    for case_id in sorted(set(reference) | set(target)):
        expected = reference.get(case_id)
        actual = target.get(case_id)

        if expected is None or actual is None:
            mismatches.append({
                "id": case_id,
                "category": "MISSING_TEST_CASE",
                "expected": expected,
                "actual": actual,
            })
            continue

        if expected["success"] != actual["success"]:
            category = "SUCCESS_FAILURE_MISMATCH"

        elif not expected["success"]:
            if expected.get("error_code") == actual.get("error_code"):
                continue
            category = "ERROR_CODE_MISMATCH"

        elif expected.get("attributes") != actual.get("attributes"):
            category = "ATTRIBUTE_MISMATCH"

        else:
            continue

        mismatches.append({
            "id": case_id,
            "category": category,
            "expected": expected,
            "actual": actual,
        })

    return mismatches


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python scripts/classify_mismatches.py "
            "<reference.json> <target.json>"
        )
        sys.exit(2)

    reference = load_results(sys.argv[1])
    target = load_results(sys.argv[2])

    mismatches = classify(reference, target)

    output = Path("results/classified_mismatches.json")
    output.parent.mkdir(exist_ok=True)

    output.write_text(
        json.dumps(mismatches, indent=4),
        encoding="utf-8",
    )

    print(f"Total mismatches: {len(mismatches)}")

    for mismatch in mismatches:
        print(f"{mismatch['id']}: {mismatch['category']}")


if __name__ == "__main__":
    main()