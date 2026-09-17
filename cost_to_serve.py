#!/usr/bin/env python3
"""D6: three-layer, evidence-backed cost-to-serve model for Problem B.

Layer 1 is measured API spend.  Layer 2 prices observed evaluation failures
at the supplied US$9.17 triage-nurse fallback cost.  Layer 3 projects the
per-referral expected cost over the fixed 4,000-referral monthly volume.
"""
import json
import os

FAILURE_FALLBACK_USD = 9.17
MONTHLY_REFERRALS = 4000
# D5 final comparison: five distinct model families.  GPT-4.1 mini remains
# separate recommended-model evidence and is intentionally not part of this
# required five-family cost comparison.
INPUTS = (
    "evidence/d5_live_anthropic_claude-haiku-4.5_v2.json",
    "evidence/d5_live_deepseek_deepseek-chat-v3-0324_v2.json",
    "evidence/d5_live_google_gemini-2.5-flash_v2.json",
    "evidence/d5_live_meta-llama_llama-3.3-70b-instruct_v2.json",
    "evidence/d5_live_mistralai_mistral-small-24b-instruct-2501_v2.json",
)
EXPECTED_TRIALS = 60


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if (not data.get("complete") or not data.get("full_battery_requested") or
            len(data.get("results", [])) != EXPECTED_TRIALS):
        raise ValueError(
            "%s is not a completed %s-trial battery; do not use pilot or "
            "partial evidence in D6" % (path, EXPECTED_TRIALS))
    return data


def model_cost(data, source):
    rows = data["results"]
    trials = len(rows)
    failures = sum(1 for row in rows if not row["passed"])
    variable_total = sum(row["record"]["cost_usd"] for row in rows)
    variable_per_referral = variable_total / trials
    failure_rate = failures / trials
    fallback_per_referral = failure_rate * FAILURE_FALLBACK_USD
    total_per_referral = variable_per_referral + fallback_per_referral
    return {
        "model": data["model"],
        "source": source,
        "trials": trials,
        "code_check_failures": failures,
        "code_check_failure_rate": round(failure_rate, 6),
        "layer_1": {
            "measured_variable_total_usd": round(variable_total, 6),
            "measured_variable_per_referral_usd": round(variable_per_referral, 6),
        },
        "layer_2": {
            "fallback_cost_per_failure_usd": FAILURE_FALLBACK_USD,
            "expected_fallback_per_referral_usd": round(fallback_per_referral, 6),
        },
        "layer_3": {
            "monthly_referrals": MONTHLY_REFERRALS,
            "monthly_variable_usd": round(MONTHLY_REFERRALS * variable_per_referral, 2),
            "monthly_expected_fallback_usd": round(MONTHLY_REFERRALS * fallback_per_referral, 2),
            "monthly_total_usd": round(MONTHLY_REFERRALS * total_per_referral, 2),
        },
        "expected_total_per_referral_usd": round(total_per_referral, 6),
        "sensitivity": [
            {
                "assumed_success_rate": round(rate, 4),
                "expected_total_per_referral_usd": round(
                    variable_per_referral + (1 - rate) * FAILURE_FALLBACK_USD, 6),
                "monthly_total_usd": round(MONTHLY_REFERRALS * (
                    variable_per_referral + (1 - rate) * FAILURE_FALLBACK_USD), 2),
            }
            for rate in (max(0, 1 - failure_rate - .10),
                         1 - failure_rate,
                         min(1, 1 - failure_rate + .10))
        ],
    }


def break_even(cheap, dear):
    """Success rate the lower-variable-cost model needs to match the dear one."""
    cheap_var = cheap["layer_1"]["measured_variable_per_referral_usd"]
    dear_var = dear["layer_1"]["measured_variable_per_referral_usd"]
    dear_success = 1 - dear["code_check_failure_rate"]
    required = dear_success - (dear_var - cheap_var) / FAILURE_FALLBACK_USD
    return {
        "cheap_model": cheap["model"],
        "dear_model": dear["model"],
        "required_cheap_success_rate": round(required, 6),
        "observed_cheap_success_rate": round(1 - cheap["code_check_failure_rate"], 6),
        "formula": "p_cheap = p_dear - (dear_variable - cheap_variable) / failure_cost",
    }


def main():
    results = [model_cost(load(path), path) for path in INPUTS]
    raw_cheapest = min(results,
                       key=lambda item: item["layer_1"]["measured_variable_per_referral_usd"])
    recommended = min(results,
                      key=lambda item: item["expected_total_per_referral_usd"])
    payload = {
        "method": "Layer 1 measured D5 API spend + Layer 2 observed code-check failure rate times $9.17 + Layer 3 4,000 referrals/month",
        "caution": "The raw code-check failure rate is intentionally conservative: it includes the documented REF-5590 early-exit versus answer-key conflict.",
        "final_model_families": ["Anthropic", "DeepSeek", "Google", "Meta", "Mistral"],
        "recommended_model": recommended["model"],
        "models": results,
        "break_even": break_even(raw_cheapest, recommended),
    }
    os.makedirs("evidence", exist_ok=True)
    path = "evidence/d6_cost_to_serve.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    for result in results:
        print("%s: L1 $%.6f/ref | L2 $%.6f/ref | total $%.6f/ref | monthly $%.2f"
              % (result["model"],
                 result["layer_1"]["measured_variable_per_referral_usd"],
                 result["layer_2"]["expected_fallback_per_referral_usd"],
                 result["expected_total_per_referral_usd"],
                 result["layer_3"]["monthly_total_usd"]))
    print("Wrote %s" % path)


if __name__ == "__main__":
    main()
