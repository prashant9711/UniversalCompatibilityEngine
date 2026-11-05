import json
import string
from pathlib import Path

from differential_oracle import WindowsOracle, SimulatedOracle

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "results" / "discovered_features.json"


def discover_features(paths):
    characters = set("".join(paths))

    return {
        f"contains_{ord(char)}": char
        for char in sorted(characters)
        if char in string.punctuation
    }


def repair(target_result, path, selected, features):
    result = target_result.copy()

    if (
        not result["success"]
        and result["error_code"] == 2
        and any(features[name] in path for name in selected)
    ):
        result["error_code"] = 123

    return result


def score(reference, target, paths, selected, features):
    return sum(
        repair(target.evaluate(path), path, selected, features)
        == reference.evaluate(path)
        for path in paths
    )


def learn(reference, target, training):
    features = discover_features(training)

    selected = []
    remaining = list(features)

    best_score = score(reference, target, training, selected, features)

    while remaining:
        candidates = [
            (
                score(
                    reference,
                    target,
                    training,
                    selected + [name],
                    features,
                ),
                name,
            )
            for name in remaining
        ]

        candidate_score, candidate = max(candidates)

        if candidate_score <= best_score:
            break

        selected.append(candidate)
        remaining.remove(candidate)
        best_score = candidate_score

    return features, selected


def main():
    reference = WindowsOracle()
    target = SimulatedOracle(reference)

    training = [
        "invalid<file.txt",
        "invalid>file.txt",
        "invalid?file.txt",
        "invalid*file.txt",
        "missing_file.txt",
        "C:\\Windows",
    ]

    counterexamples = [
        "another_missing.txt",
        "ordinary.document.txt",
        "not_found.txt",
        "C:\\Windows\\System32",
        "different<file.txt",
        "different>file.txt",
        "different?file.txt",
        "different*file.txt",
    ]

    for iteration in range(5):
        features, selected = learn(reference, target, training)

        failures = [
            path
            for path in counterexamples
            if repair(
                target.evaluate(path), path, selected, features
            ) != reference.evaluate(path)
        ]

        print(f"Iteration {iteration + 1}")
        print("Selected:", [features[name] for name in selected])
        print("Counterexample failures:", len(failures))

        if not failures:
            break

        training.extend(path for path in failures if path not in training)

    report = {
        "selected_characters": [features[name] for name in selected],
        "training_count": len(training),
        "counterexample_failures": failures,
    }

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=4), encoding="utf-8")

    print("\nFinal selected characters:")
    print([features[name] for name in selected])


if __name__ == "__main__":
    main()