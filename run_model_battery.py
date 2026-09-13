#!/usr/bin/env python3
"""Run the opt-in D5 live model battery through OpenRouter.

This file is deliberately separate from run_eval.py: a marker must be able
to run the latter offline with no API key and no network.  A live battery is
an experiment, not the reproducibility test.

Examples (PowerShell):
  $env:OPENROUTER_API_KEY = "..."       # never put the key in a file
  python run_model_battery.py --model provider/model --pilot 5 --max-cost 0.25
  python run_model_battery.py --model provider/model --full --synthetic-approval --max-cost 2
"""
import argparse
import json
import os
import re
from datetime import datetime, timezone

import config
from agent import run_case
from harness import (_is_negative, code_check, load_cases, load_key,
                     prepare_judgement_check, report)


def safe_filename(model):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", model).strip("_")


def run_one_model(model, case_limit, full, synthetic_approval, max_cost):
    """Run a bounded battery and write one evidence file for one model."""
    config.BACKEND = "live"
    config.MODEL = model
    if not config.API_KEY and not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("No OPENROUTER_API_KEY found. Set it only in this terminal session.")
    if not synthetic_approval:
        raise SystemExit("The battery requires --synthetic-approval: these are local fixtures, not real bookings.")

    key = load_key()
    cases = load_cases()
    if not full:
        cases = cases[:case_limit]

    results, judgement_queue = [], []
    stopped_for_cost = False
    # The fixtures' book_slot is a no-op.  Explicit consent is still required
    # because a real deployment must not silently turn confirm into act.
    approve = (lambda action, payload: True) if synthetic_approval else None

    for cid in cases:
        trials = 3 if _is_negative(key[cid]) else 1
        for trial in range(1, trials + 1):
            record = run_case(cid, approve=approve)
            passed, fails = code_check(record, key[cid])
            results.append({"case_id": cid, "trial": trial, "passed": passed,
                            "fails": fails, "record": record,
                            "family": key[cid].get("family")})
            if trial == 1:
                judgement_queue.append(prepare_judgement_check(record, key[cid]))
            if sum(r["record"]["cost_usd"] for r in results) >= max_cost:
                stopped_for_cost = True
                break
        if stopped_for_cost:
            break

    summary = report(results)
    payload = {
        "experiment": "D5 live model battery",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "backend": "live",
        "tool_contract_version": config.TOOL_CONTRACT_VERSION,
        "autonomy": config.AUTONOMY,
        "synthetic_approval": synthetic_approval,
        "full_battery_requested": full,
        "expected_trials_if_complete": 60 if full else None,
        "max_cost_usd": max_cost,
        "stopped_for_cost": stopped_for_cost,
        "complete": full and not stopped_for_cost and len(results) == 60,
        "summary": summary,
        "results": results,
        "judgement_queue": judgement_queue,
        "notes": [
            "tokens_in/tokens_out are API response usage, not estimates.",
            "cost_basis says whether OpenRouter reported cost or configured prices were used.",
            "Synthetic approval is allowed only because book_slot is a no-op local fixture.",
        ],
    }
    os.makedirs("evidence", exist_ok=True)
    path = os.path.join("evidence", "d5_live_%s.json" % safe_filename(model))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=str)
    print("Wrote %s" % path)
    if stopped_for_cost:
        print("Stopped at the user-set cost ceiling; do not report this as a completed battery.")
    return payload


def main():
    parser = argparse.ArgumentParser(description="D5 OpenRouter model battery")
    parser.add_argument("--model", action="append", required=True,
                        help="OpenRouter model string; repeat for each model")
    parser.add_argument("--pilot", type=int, default=5,
                        help="number of cases in a cheap preflight (default: 5)")
    parser.add_argument("--full", action="store_true",
                        help="run all 40 cases / 60 trials per model")
    parser.add_argument("--synthetic-approval", action="store_true",
                        help="allow no-op fixture bookings after the confirm gate")
    parser.add_argument("--max-cost", type=float, required=True,
                        help="hard stop after this much measured/fallback cost per model")
    args = parser.parse_args()
    if args.pilot < 1 or args.max_cost <= 0:
        raise SystemExit("--pilot and --max-cost must be positive.")

    for model in args.model:
        print("\nD5 live battery: %s" % model)
        run_one_model(model, args.pilot, args.full,
                      args.synthetic_approval, args.max_cost)


if __name__ == "__main__":
    main()
