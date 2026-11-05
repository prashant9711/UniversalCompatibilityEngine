import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "results" / "diagnostic_results.json"
OUTPUT = ROOT / "results" / "diagnostic_analysis.json"


def behavior(result):
    if result["success"]:
        return ("success", result.get("attributes"))

    return ("failure", result.get("error_code"))


def analyze(results):
    groups = defaultdict(list)

    for result in results:
        groups[result["source_case"]].append(result)

    findings = []

    for source_case, experiments in groups.items():
        observed = {behavior(item) for item in experiments}

        consistent = len(observed) == 1

        findings.append({
            "source_case": source_case,
            "experiments_run": len(experiments),
            "consistent_behavior": consistent,
            "path_representation_sensitive": not consistent,
            "conclusion": (
                "No path-representation differences observed "
                "in this environment."
                if consistent
                else "Path-representation-dependent behavior detected."
            ),
            "observations": [
                {
                    "variant": item["variant"],
                    "success": item["success"],
                    "attributes": item.get("attributes"),
                    "error_code": item.get("error_code"),
                }
                for item in experiments
            ],
        })

    return findings


def main():
    results = json.loads(INPUT.read_text(encoding="utf-8"))
    findings = analyze(results)

    OUTPUT.write_text(
        json.dumps(findings, indent=4),
        encoding="utf-8",
    )

    for finding in findings:
        print(f"\nCase: {finding['source_case']}")
        print(f"Experiments: {finding['experiments_run']}")
        print(f"Consistent behavior: {finding['consistent_behavior']}")
        print(f"Conclusion: {finding['conclusion']}")

    print(f"\nAnalysis saved to {OUTPUT}")


if __name__ == "__main__":
    main()