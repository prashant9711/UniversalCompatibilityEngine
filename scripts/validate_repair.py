import random

from differential_oracle import WindowsOracle, SimulatedOracle
from discover_features import repair

reference = WindowsOracle()
target = SimulatedOracle(reference)

selected = ["<", ">", "?", "*"]
features = {char: char for char in selected}

random.seed(2026)

characters = "abcdefghijklmnopqrstuvwxyz0123456789<>?*._-"
paths = [
    "".join(random.choices(characters, k=random.randint(1, 25)))
    for _ in range(1000)
]

baseline_correct = 0
repaired_correct = 0
regressions = []
remaining_failures = []

for path in paths:
    expected = reference.evaluate(path)
    original = target.evaluate(path)
    corrected = repair(original, path, selected, features)

    baseline_correct += original == expected
    repaired_correct += corrected == expected

    if original == expected and corrected != expected:
        regressions.append(path)

    if corrected != expected:
        remaining_failures.append(path)

print(f"Cases: {len(paths)}")
print(f"Baseline correct: {baseline_correct}")
print(f"Repaired correct: {repaired_correct}")
print(f"Regressions: {len(regressions)}")
print(f"Remaining failures: {len(remaining_failures)}")
print("Example failures:", remaining_failures[:5])