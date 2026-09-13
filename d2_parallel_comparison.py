#!/usr/bin/env python3
"""D2(c): compare one scripted trajectory grouped versus sequential.

The tool calls and their arguments are identical in both runs. Only the turn
grouping changes, so any cost or reliability difference is attributable to
parallelising independent calls rather than changing the task.
"""
import copy
import json

from agent import run_case
from backends import SCRIPTS
from harness import code_check, load_key

CASE_ID = "REF-5602"


def sequentialise(steps):
    """Split every multi-call turn into one-call turns without changing calls."""
    expanded = []
    for move in steps:
        if "final" in move:
            expanded.append(copy.deepcopy(move))
            continue
        calls = move.get("calls") or [(move["tool"], move["args"])]
        for number, call in enumerate(calls, start=1):
            expanded.append({"thought": "%s [sequential call %d/%d]"
                             % (move.get("thought", ""), number, len(calls)),
                             "calls": [copy.deepcopy(call)]})
    return expanded


def run_with(steps):
    original = SCRIPTS[CASE_ID]
    try:
        SCRIPTS[CASE_ID] = steps
        return run_case(CASE_ID)
    finally:
        SCRIPTS[CASE_ID] = original


def summary(record, expected):
    passed, failures = code_check(record, expected)
    return {
        "decision": record["decision"],
        "code_check_pass": passed,
        "code_check_failures": failures,
        "turns": record["turns"],
        "tool_calls": len(record["evidence"]),
        "tool_sequence": record["evidence"],
        "tokens_in_estimated": record["tokens_in"],
        "tokens_out_estimated": record["tokens_out"],
        "cost_usd_estimated": record["cost_usd"],
    }


def main():
    grouped_steps = copy.deepcopy(SCRIPTS[CASE_ID])
    grouped = run_with(grouped_steps)
    sequential = run_with(sequentialise(grouped_steps))
    expected = load_key()[CASE_ID]
    result = {
        "case_id": CASE_ID,
        "backend": "scripted",
        "method": "Same six tool calls and arguments; only independent-call grouping differs.",
        "grouped": summary(grouped, expected),
        "sequential": summary(sequential, expected),
    }
    result["turn_reduction"] = sequential["turns"] - grouped["turns"]
    result["input_token_reduction_pct_estimated"] = round(
        100 * (sequential["tokens_in"] - grouped["tokens_in"])
        / sequential["tokens_in"], 1)
    print(json.dumps(result, indent=2))
    with open("evidence/d2_parallel_comparison.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)


if __name__ == "__main__":
    main()
