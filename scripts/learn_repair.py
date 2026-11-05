import json
from pathlib import Path

from differential_oracle import WindowsOracle, SimulatedOracle

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "results" / "learned_repair.json"


def candidate_features(path):
    return {
        "contains_angle_bracket": "<" in path or ">" in path,
        "contains_question_mark": "?" in path,
        "contains_asterisk": "*" in path,
        "ends_with_space": path.endswith(" "),
    }


class LearnedAdapter:
    def __init__(self, target, feature):
        self.target = target
        self.feature = feature

    def evaluate(self, path):
        result = self.target.evaluate(path).copy()

        features = candidate_features(path)

        if (
            not result["success"]
            and result["error_code"] == 2
            and features[self.feature]
        ):
            result["error_code"] = 123

        return result


def score(reference, adapter, paths):
    return sum(
        reference.evaluate(path) == adapter.evaluate(path)
        for path in paths
    )


def main():
    reference = WindowsOracle()
    target = SimulatedOracle(reference)

    training = [
        ">",
        "<",
        "invalid<>file.txt",
        "missing_file_92741.txt",
        "C:\\Windows",
    ]

    validation = [
        "another>invalid.txt",
        "test<file.txt",
        "missing_again.txt",
        "C:\\Windows\\System32",
        "example?.txt",
        "example*.txt",
    ]

    features = list(candidate_features("").keys())

    scores = {}

    for feature in features:
        adapter = LearnedAdapter(target, feature)
        scores[feature] = score(reference, adapter, training)

    best_feature = max(scores, key=scores.get)
    adapter = LearnedAdapter(target, best_feature)

    validation_results = []

    for path in validation:
        expected = reference.evaluate(path)
        actual = adapter.evaluate(path)

        validation_results.append({
            "path": path,
            "passed": expected == actual,
            "expected": expected,
            "actual": actual,
        })

    report = {
        "training_scores": scores,
        "selected_feature": best_feature,
        "validation": validation_results,
    }

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=4), encoding="utf-8")

    passed = sum(item["passed"] for item in validation_results)

    print("Selected feature:", best_feature)
    print(f"Validation: {passed}/{len(validation_results)}")

    for item in validation_results:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"{item['path']!r}: {status}")

    print(f"\nReport saved to {OUTPUT}")


if __name__ == "__main__":
    main()