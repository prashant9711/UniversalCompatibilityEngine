import json
import sys
from pathlib import Path

RULES = {
    "ERROR_CODE_MISMATCH": {
        "possible_causes": [
            "Different path resolution behavior",
            "Different error mapping",
            "Different filesystem semantics",
        ],
        "repair_candidates": [
            "Normalize path handling",
            "Investigate Win32 error translation",
        ],
    },
    "SUCCESS_FAILURE_MISMATCH": {
        "possible_causes": [
            "Unsupported API behavior",
            "Filesystem permission differences",
            "Path normalization differences",
        ],
        "repair_candidates": [
            "Inspect API implementation",
            "Verify permissions and path handling",
        ],
    },
    "ATTRIBUTE_MISMATCH": {
        "possible_causes": [
            "Different filesystem metadata",
            "Incorrect attribute mapping",
        ],
        "repair_candidates": [
            "Normalize relevant file attribute flags",
        ],
    },
    "MISSING_TEST_CASE": {
        "possible_causes": [
            "Test execution incomplete",
            "Test collection failure",
        ],
        "repair_candidates": [
            "Rerun missing test cases",
        ],
    },
}


def diagnose(mismatches):
    findings = []

    for mismatch in mismatches:
        category = mismatch["category"]
        rule = RULES.get(category, {})

        findings.append({
            "id": mismatch["id"],
            "category": category,
            "possible_causes": rule.get("possible_causes", []),
            "repair_candidates": rule.get("repair_candidates", []),
            "verified_root_cause": False,
        })

    return findings


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/diagnose.py <mismatches.json>")
        sys.exit(2)

    source = Path(sys.argv[1])
    mismatches = json.loads(source.read_text(encoding="utf-8"))

    findings = diagnose(mismatches)

    output = Path("results/diagnosis.json")
    output.parent.mkdir(exist_ok=True)

    output.write_text(
        json.dumps(findings, indent=4),
        encoding="utf-8",
    )

    for finding in findings:
        print(f"\n{finding['id']}: {finding['category']}")

        print("Possible causes:")
        for cause in finding["possible_causes"]:
            print(f"  - {cause}")

        print("Repair candidates:")
        for repair in finding["repair_candidates"]:
            print(f"  - {repair}")

    print(f"\nDiagnosis saved to {output}")


if __name__ == "__main__":
    main()