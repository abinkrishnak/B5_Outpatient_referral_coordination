#!/usr/bin/env python3
"""Print a compact table from final D5 live evidence files.

Pilot files and the V1 descriptor experiment are intentionally excluded. This
is a reading aid; raw per-trial evidence remains in evidence/d5_live_*.json.
"""
import glob
import json
import os


def final_files():
    paths = glob.glob("evidence/d5_live_*.json")
    return sorted(path for path in paths if not path.endswith("_v1.json"))


def main():
    rows = []
    for path in final_files():
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        results = data.get("results", [])
        if len(results) != 60:
            continue
        summary = data["summary"]
        rows.append((data["model"], summary["passed"], summary["trials"],
                     100 * summary["pass_rate"], summary["median_turns"],
                     summary["cost_usd"], os.path.basename(path)))
    if not rows:
        raise SystemExit("No completed 60-trial V2 live evidence files found.")
    print("model | pass rate | median turns | total cost | evidence")
    print("-|-|-|-|-")
    for model, passed, trials, rate, turns, cost, path in rows:
        print("%s | %d/%d (%.1f%%) | %s | $%.6f | %s"
              % (model, passed, trials, rate, turns, cost, path))


if __name__ == "__main__":
    main()
