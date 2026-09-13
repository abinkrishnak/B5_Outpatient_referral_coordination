#!/usr/bin/env python3
"""D7 second failure: remove V2's slot-query constraint and observe the lie.

The working V2 tool rejects the typo ``OPHT``.  V1 removes only that
poka-yoke constraint; it returns an empty list, which a ReAct agent could
mistake for the real business outcome ``no_slot_in_window``.  No model or
network is involved, so the tool-layer failure is reproducible exactly.
"""
import json
import os

import config
import tools

ARGS = {"specialty": "OPHT", "band": "routine",
        "from": "2026-09-09", "to": "2026-11-04"}


def call_as(version):
    original = config.TOOL_CONTRACT_VERSION
    config.TOOL_CONTRACT_VERSION = version
    try:
        return tools.get_clinic_slots(**ARGS)
    finally:
        config.TOOL_CONTRACT_VERSION = original


def main():
    v2 = call_as("v2")
    v1 = call_as("v1")
    evidence = {
        "failure": "specialty_typo_silent_empty_result",
        "deleted_component": "V2 closed-set specialty validation",
        "attempted_args": ARGS,
        "working_v2_result": v2,
        "broken_v1_result": v1,
        "why_accuracy_alone_is_insufficient": (
            "Both results are valid Python values. Only V2 distinguishes an "
            "invalid query from a real empty slot window."),
        "correct_fix_layer": "tool interface (poka-yoke constraint)",
        "wrong_fix_layers": [
            "prompt: a model can still misspell a string",
            "guardrail after slot search: it sees an empty result too late",
        ],
        "restoration_verified": isinstance(v2, dict) and
                                v2.get("error") == "invalid_slot_query",
    }
    os.makedirs("evidence", exist_ok=True)
    path = "evidence/d7_tool_contract_failure.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(evidence, fh, indent=2)
    print("V1 (broken): %r" % v1)
    print("V2 (restored): %r" % v2)
    print("Wrote %s" % path)
    if not evidence["restoration_verified"]:
        raise SystemExit("V2 restoration did not reject the invalid specialty.")


if __name__ == "__main__":
    main()
