import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

data = json.loads(
    (RESULTS / "controlled_windows.json").read_text(encoding="utf-8")
)

successes = sum(1 for item in data if item["success"])
errors = len(data) - successes

report = {
    "engine": "Universal Compatibility Engine",
    "platform": "Windows",
    "total_cases": len(data),
    "successful_api_calls": successes,
    "api_errors": errors,
    "results": data,
}

output = RESULTS / "report.json"
output.write_text(json.dumps(report, indent=4), encoding="utf-8")

print(f"Total cases: {len(data)}")
print(f"Successful calls: {successes}")
print(f"API errors: {errors}")
print(f"Report saved to {output}")