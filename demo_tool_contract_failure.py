#!/usr/bin/env python3
"""D7 failure 2: controlled removal and restoration of a tool constraint.

This deterministic experiment isolates one component: V2's closed-set
validation for slot-query specialty and band. The same invalid action is sent
through a tiny routing loop three times:

    working V2 -> delete constraint (V1) -> restore V2

No network or model is needed, so the failure is exactly reproducible. The
experiment records the agent-level decision record and instrumentation, not
only the raw Python return value.
"""
import json
import os

import config
import tools

ARGS = {
    "specialty": "OPHT",
    "band": "routine",
    "from": "2026-09-09",
    "to": "2026-11-04",
}
EXPECTED_TRIGGER = "invalid_slot_query"


def estimated_tokens(value):
    """Transparent deterministic estimate used only by this offline demo."""
    return max(1, round(len(json.dumps(value, sort_keys=True)) / 4))


def run_trial(version, phase):
    """Run one isolated routing trial under one tool-contract version."""
    original = config.TOOL_CONTRACT_VERSION
    try:
        config.TOOL_CONTRACT_VERSION = version
        observation = tools.get_clinic_slots(**ARGS)
    finally:
        config.TOOL_CONTRACT_VERSION = original

    action = {"tool": "get_clinic_slots", "args": ARGS}
    tokens_in = estimated_tokens(action)
    tokens_out = estimated_tokens(observation)

    if isinstance(observation, dict) and observation.get("error") == EXPECTED_TRIGGER:
        decision = "escalate"
        trigger = EXPECTED_TRIGGER
        reason = (
            "The slot query is invalid because specialty OPHT is outside the "
            "closed set. Correct the value from the referral before retrying."
        )
    else:
        decision = "escalate"
        trigger = "no_slot_in_window"
        reason = (
            "No slots were returned, so the agent incorrectly treated a typo "
            "as genuine unavailability."
        )

    total_tokens = tokens_in + tokens_out
    estimated_cost = (
        (tokens_in / 1_000_000) * config.PRICE_IN
        + (tokens_out / 1_000_000) * config.PRICE_OUT
    )
    return {
        "phase": phase,
        "tool_contract_version": version,
        "deleted_component": (
            "none" if version == "v2"
            else "closed-set specialty and urgency-band validation"
        ),
        "attempted_action": action,
        "observation": observation,
        "decision": decision,
        "trigger": trigger,
        "reason": reason,
        "expected_trigger": EXPECTED_TRIGGER,
        "pass": trigger == EXPECTED_TRIGGER,
        "turns": 1,
        "tool_calls": 1,
        "tokens_in_estimated": tokens_in,
        "tokens_out_estimated": tokens_out,
        "total_tokens_estimated": total_tokens,
        "estimated_cost_usd": round(estimated_cost, 8),
        "token_method": "serialized_characters_divided_by_4",
    }


def main():
    working = run_trial("v2", "working_baseline")
    broken = run_trial("v1", "component_removed")
    restored = run_trial("v2", "component_restored")

    evidence = {
        "failure_id": "F2",
        "failure": "specialty_typo_silent_empty_result",
        "layer": "tool interface",
        "controlled_change": (
            "Remove only V2 closed-set validation; keep the action and routing "
            "logic unchanged, then restore the validation."
        ),
        "expected_safe_behaviour": (
            "Expose invalid_slot_query instead of reporting an empty legal window."
        ),
        "runs": [working, broken, restored],
        "working_pass_rate": int(working["pass"]),
        "broken_pass_rate": int(broken["pass"]),
        "restored_pass_rate": int(restored["pass"]),
        "failure_reproduced": working["pass"] and not broken["pass"],
        "restoration_verified": restored["pass"],
        "failure_visible_in": [
            "trigger",
            "reason",
            "structured tool observation",
        ],
        "correct_fix_layer": (
            "Tool interface: the finite vocabulary is known and can be enforced "
            "before an empty list acquires business meaning."
        ),
        "why_other_layers_are_wrong": {
            "prompt": (
                "A prompt can request exact copying but cannot make an illegal "
                "string impossible."
            ),
            "post_query_guardrail": (
                "After the V1 tool returns [], the typo is already indistinguishable "
                "from genuine no availability."
            ),
        },
        "scope_note": (
            "This is an offline deterministic agent-routing reproduction. Token "
            "and cost fields are transparent estimates, not provider billing."
        ),
    }

    os.makedirs("evidence", exist_ok=True)
    path = "evidence/d7_tool_contract_failure.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(evidence, fh, indent=2)

    for run in evidence["runs"]:
        print(
            "{phase:<20} contract={tool_contract_version} pass={pass} "
            "trigger={trigger} turns={turns} calls={tool_calls} "
            "tokens={total_tokens_estimated}".format(**run)
        )
    print("Wrote %s" % path)

    if not evidence["failure_reproduced"]:
        raise SystemExit("Failure 2 was not reproduced.")
    if not evidence["restoration_verified"]:
        raise SystemExit("Failure 2 restoration was not verified.")


if __name__ == "__main__":
    main()
