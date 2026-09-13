#!/usr/bin/env python3
"""Summarise the controlled D2(b) V1-versus-V2 descriptor experiment."""
import argparse
import json


def read(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def metrics(data):
    rows = data["results"]
    return {
        "model": data["model"],
        "contract": data["tool_contract_version"],
        "trials": len(rows),
        "passes": sum(1 for r in rows if r["passed"]),
        "pass_rate": round(100 * sum(1 for r in rows if r["passed"]) / len(rows), 1),
        "tokens_in": sum(r["record"]["tokens_in"] for r in rows),
        "tokens_out": sum(r["record"]["tokens_out"] for r in rows),
        "cost_usd": round(sum(r["record"]["cost_usd"] for r in rows), 6),
        "guardrail_stops": sum(1 for r in rows if r["record"]["stopped_by"]),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("v1")
    parser.add_argument("v2")
    args = parser.parse_args()
    one, two = metrics(read(args.v1)), metrics(read(args.v2))
    if one["model"] != two["model"]:
        raise SystemExit("Use the same model for V1 and V2.")
    print("D2(b) descriptor comparison - model: %s" % one["model"])
    for row in (one, two):
        print("%-2s  %d/%d passes (%s%%) | in %d | out %d | $%.6f | guard stops %d"
              % (row["contract"], row["passes"], row["trials"], row["pass_rate"],
                 row["tokens_in"], row["tokens_out"], row["cost_usd"],
                 row["guardrail_stops"]))


if __name__ == "__main__":
    main()
