import json
from pathlib import Path

from differential_oracle import WindowsOracle, SimulatedOracle
from learn_repair import candidate_features

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "results" / "multi_rule_repair.json"


class MultiRuleAdapter:
    def __init__(self, target, features):
        self.target = target
        self.features = features

    def evaluate(self, path):
        result = self.target.evaluate(path).copy()
        path_features = candidate_features(path)

        if (
            not result["success"]
            and result["error_code"] == 2
            and any(path_features[name] for name in self.features)
        ):
            result["error_code"] = 123

        return result


def accuracy(reference, target, features, paths):
    adapter = MultiRuleAdapter(target, features)

    return sum(
        adapter.evaluate(path) == reference.evaluate(path)
        for path in paths
    )


def learn(reference, target, training):
    available = list(candidate_features("").keys())
    selected = []

    best_score = accuracy(reference, target, selected, training)

    while available:
        candidates = [
            (
                accuracy(reference, target, selected + [feature], training),
                feature,
            )
            for feature in available
        ]

        score, feature = max(candidates)

        if score <= best_score:
            break

        selected.append(feature)
        available.remove(feature)
        best_score = score

    return selected


def main():
    reference = WindowsOracle()
    target = SimulatedOracle(reference)

    training = [
        ">",
        "<",
        "invalid<>file.txt",
        "example?.txt",
        "example*.txt",
        "missing_file_92741.txt",
        "C:\\Windows",
    ]

    validation = [
        "another>invalid.txt",
        "test<file.txt",
        "new?.txt",
        "new*.txt",
        "missing_again.txt",
        "C:\\Windows\\System32",
    ]

    selected = learn(reference, target, training)
    adapter = MultiRuleAdapter(target, selected)

    results = [
        {
            "path": path,
            "passed": (
                adapter.evaluate(path) == reference.evaluate(path)
            ),
        }
        for path in validation
    ]

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "selected_features": selected,
                "validation": results,
            },
            indent=4,
        ),
        encoding="utf-8",
    )

    passed = sum(item["passed"] for item in results)

    print("Selected features:", selected)
    print(f"Validation: {passed}/{len(results)}")

    for item in results:
        print(f"{item['path']!r}: {'PASS' if item['passed'] else 'FAIL'}")


if __name__ == "__main__":
    main()