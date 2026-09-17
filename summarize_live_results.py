#!/usr/bin/env python3
"""Print a compact table from final D5 live evidence files.

Pilot files and the V1 descriptor experiment are intentionally excluded. This
is a reading aid; raw per-trial evidence remains in evidence/d5_live_*.json.
"""
import json
import os

FINAL_MODELS = (
    "anthropic/claude-haiku-4.5",
    "deepseek/deepseek-chat-v3-0324",
    "google/gemini-2.5-flash",
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-small-24b-instruct-2501",
)
EXPECTED_TRIALS = 60

def main():
    rows_by_model = {}
    for filename in os.listdir("evidence"):
        if not (filename.startswith("d5_live_") and filename.endswith(".json")):
            continue
        path = os.path.join("evidence", filename)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if data.get("model") not in FINAL_MODELS:
            continue
        results = data.get("results", [])
        if (not data.get("complete") or not data.get("full_battery_requested")
                or len(results) != EXPECTED_TRIALS):
            continue
        summary = data["summary"]
        rows_by_model[data["model"]] = (
            data["model"], summary["passed"], summary["trials"],
            100 * summary["pass_rate"], summary["median_turns"],
            summary["cost_usd"], os.path.basename(path))
    missing = [model for model in FINAL_MODELS if model not in rows_by_model]
    if missing:
        raise SystemExit("Missing completed final evidence for: %s"
                         % ", ".join(missing))
    print("model | pass rate | median turns | total cost | evidence")
    print("-|-|-|-|-")
    for model in FINAL_MODELS:
        model, passed, trials, rate, turns, cost, path = rows_by_model[model]
        print("%s | %d/%d (%.1f%%) | %s | $%.6f | %s"
              % (model, passed, trials, rate, turns, cost, path))


if __name__ == "__main__":
    main()
