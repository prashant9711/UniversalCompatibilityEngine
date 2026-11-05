import json
from pathlib import Path

from differential_oracle import WindowsOracle, SimulatedOracle

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "results" / "repair_validation.json"


class ErrorMappingAdapter:
    def __init__(self, target, mapping):
        self.target = target
        self.mapping = mapping

    def evaluate(self, path):
        result = self.target.evaluate(path).copy()

        if not result["success"]:
            key = (path, result["error_code"])

            if key in self.mapping:
                result["error_code"] = self.mapping[key]

        return result


def synthesize(reference, target, training_paths):
    mapping = {}

    for path in training_paths:
        expected = reference.evaluate(path)
        actual = target.evaluate(path)

        if (
            not expected["success"]
            and not actual["success"]
            and expected["error_code"] != actual["error_code"]
        ):
            mapping[(path, actual["error_code"])] = expected["error_code"]

    return mapping


def validate(reference, adapter, paths):
    results = []

    for path in paths:
        expected = reference.evaluate(path)
        actual = adapter.evaluate(path)

        results.append({
            "path": path,
            "passed": expected == actual,
            "expected": expected,
            "actual": actual,
        })

    return results


def main():
    reference = WindowsOracle()
    target = SimulatedOracle(reference)

    training_paths = [">"]

    validation_paths = [
        ">",
        "<",
        "missing_file_92741.txt",
        "C:\\Windows",
        "C:\\Windows\\System32",
        "invalid<>file.txt",
    ]

    mapping = synthesize(reference, target, training_paths)
    adapter = ErrorMappingAdapter(target, mapping)

    results = validate(reference, adapter, validation_paths)

    report = {
        "training_paths": training_paths,
        "mapping": [
            {
                "path": path,
                "from_error": source,
                "to_error": destination,
            }
            for (path, source), destination in mapping.items()
        ],
        "validation": results,
    }

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=4), encoding="utf-8")

    passed = sum(result["passed"] for result in results)

    print(f"Generated mappings: {len(mapping)}")
    print(f"Validation: {passed}/{len(results)} passed")

    for result in results:
        print(f"{result['path']!r}: {'PASS' if result['passed'] else 'FAIL'}")

    print(f"\nReport saved to {OUTPUT}")


if __name__ == "__main__":
    main()