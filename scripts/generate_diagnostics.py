import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def generate(mismatches):
    experiments = []

    for mismatch in mismatches:
        if mismatch["category"] != "SUCCESS_FAILURE_MISMATCH":
            continue

        case_id = mismatch["id"]

        experiments.extend([
            {
                "id": f"{case_id}_absolute",
                "source_case": case_id,
                "variant": "absolute_path",
            },
            {
                "id": f"{case_id}_relative",
                "source_case": case_id,
                "variant": "relative_path",
            },
            {
                "id": f"{case_id}_forward_slash",
                "source_case": case_id,
                "variant": "forward_slash",
            },
            {
                "id": f"{case_id}_backslash",
                "source_case": case_id,
                "variant": "backslash",
            },
        ])

    return experiments


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_diagnostics.py <mismatches.json>")
        sys.exit(2)

    mismatches = json.loads(
        Path(sys.argv[1]).read_text(encoding="utf-8")
    )

    experiments = generate(mismatches)

    output = ROOT / "tests" / "diagnostic_cases.json"
    output.parent.mkdir(exist_ok=True)

    output.write_text(
        json.dumps(experiments, indent=4),
        encoding="utf-8",
    )

    print(f"Generated {len(experiments)} diagnostic experiments")

    for experiment in experiments:
        print(f"{experiment['id']}: {experiment['variant']}")

    print(f"\nSaved to {output}")


if __name__ == "__main__":
    main()