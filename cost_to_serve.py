#!/usr/bin/env python3
"""Offline D6 baseline: measured tokens at list prices plus expected fallback."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import d6_course_costs as course

ROOT = Path(__file__).resolve().parent
F = Decimal(55) * Decimal(10) / Decimal(60)
VOLUME = 4000
FIXED_MONTHLY = Decimal(0)
INPUTS = (
    "evidence/d5_live_anthropic_claude-haiku-4.5_v2.json",
    "evidence/d5_live_deepseek_deepseek-chat-v3-0324_v2.json",
    "evidence/d5_live_google_gemini-2.5-flash_v2.json",
    "evidence/d5_live_meta-llama_llama-3.3-70b-instruct_v2.json",
    "evidence/d5_live_mistralai_mistral-small-24b-instruct-2501_v2.json",
)
GPT = "evidence/d5_live_openai_gpt-4.1-mini_v2_post_timeout_fix_full_2026-09-16.json"
MODELS = (
    "anthropic/claude-haiku-4.5",
    "deepseek/deepseek-chat-v3-0324",
    "google/gemini-2.5-flash",
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-small-24b-instruct-2501",
)


def dec(value):
    if value is None or isinstance(value, bool):
        raise ValueError("Missing or invalid numeric evidence")
    try:
        x = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Invalid number") from exc
    if not x.is_finite() or x < 0:
        raise ValueError("Negative or nonfinite numeric evidence")
    return x


def num(value):
    return float(round(value, 12))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(d, expected_model=None):
    if expected_model is not None and d.get("model") != expected_model:
        raise ValueError("Evidence model does not match expected model")
    rows = d.get("results", [])
    if not (d.get("complete") is True and d.get("full_battery_requested") is True
            and d.get("backend") == "live" and d.get("tool_contract_version") == "v2"
            and len(rows) == 60):
        raise ValueError("Expected complete live V2 60-trial evidence")
    pairs = [(r["case_id"], r["trial"]) for r in rows]
    counts = Counter(r["case_id"] for r in rows)
    if len(set(pairs)) != 60 or len(counts) != 40 or Counter(counts.values()) != Counter({1: 30, 3: 10}):
        raise ValueError("Invalid case/trial schedule")
    for r in rows:
        if type(r.get("passed")) is not bool:
            raise ValueError("Missing boolean score")
        rec = r.get("record") or {}
        if rec.get("backend") != "live" or rec.get("cost_basis") != "provider_reported":
            raise ValueError("Missing live provider cost evidence")
        tokens = [dec(rec.get(k)) for k in ("tokens_in", "tokens_out")]
        if any(x != x.to_integral_value() for x in tokens) or sum(tokens) <= 0:
            raise ValueError("Invalid token counts")
        dec(rec.get("cost_usd"))
    return set(pairs)


def model_cost(d, source, prices):
    validate(d)
    rows = d["results"]
    price = prices[d["model"]]
    pi, po = dec(price["prompt"]), dec(price["completion"])
    ledger = []
    total = bill = Decimal(0)
    inp = out = 0
    for r in rows:
        rec = r["record"]
        i, o = int(rec["tokens_in"]), int(rec["tokens_out"])
        c = Decimal(i) * pi + Decimal(o) * po
        actual = dec(rec["cost_usd"])
        inp += i
        out += o
        total += c
        bill += actual
        ledger.append({"case_id": r["case_id"], "trial": r["trial"], "passed": r["passed"],
                       "tokens_in": i, "tokens_out": o, "list_price_tokens_usd": num(c),
                       "provider_reported_usd": num(actual)})
    passed = sum(r["passed"] for r in rows)
    p = Decimal(passed) / 60
    l1 = total / 60
    l2 = (1 - p) * F
    monthly = (l1 + l2) * VOLUME + FIXED_MONTHLY
    # Reuse the original Class 5 pure functions and independently reconcile Decimal.
    course.PRICES = {"audit": {"in": float(pi * 1000000), "out": float(po * 1000000), "cached_in": float(pi * 1000000)}}
    assert abs(course.variable_cost("audit", inp, 0, out) - float(total)) < 1e-9
    assert abs(course.monthly(float(l1), float(p), float(F), VOLUME, float(FIXED_MONTHLY)) - float(monthly)) < 1e-8
    sensitivity = []
    for delta in (Decimal("-.1"), Decimal(0), Decimal(".1")):
        rate = min(Decimal(1), max(Decimal(0), p + delta))
        cost = l1 + (1 - rate) * F
        sensitivity.append({"assumed_success_rate": num(rate), "requested_delta_percentage_points": num(delta * 100),
                            "clipped": rate != p + delta, "expected_total_per_referral_usd": num(cost),
                            "monthly_total_usd": num(cost * VOLUME + FIXED_MONTHLY)})
    old_monthly = (bill / 60 + (1 - p) * Decimal("9.17")) * VOLUME
    return {"model": d["model"], "source": source, "created_utc": d.get("created_utc"),
            "trials": 60, "cases": 40, "code_check_passed": passed,
            "code_check_success_rate": num(p), "code_check_failures": 60 - passed,
            "tokens_in": inp, "tokens_out": out, "per_trial": ledger,
            "layer_1": {"basis": "recorded tokens at dated list prices; no assumed caching discount",
                        "list_token_total_usd": num(total), "variable_per_referral_usd": num(l1),
                        "extra_tool_retrieval_per_referral_usd": 0},
            "layer_2": {"fallback_cost_per_failure_usd": num(F), "expected_fallback_per_referral_usd": num(l2)},
            "layer_3": {"fixed_monthly_usd": num(FIXED_MONTHLY), "scope": "Additional paid prototype services only; full production fixed costs unknown"},
            "expected_total_per_referral_usd": num(l1 + l2),
            "monthly": {"referrals": VOLUME, "variable_usd": num(l1 * VOLUME), "fallback_usd": num(l2 * VOLUME),
                        "fixed_usd": num(FIXED_MONTHLY), "total_usd": num(monthly)},
            "provider_comparison": {"recorded_battery_usd": num(bill), "per_recorded_trial_usd": num(bill / 60),
                                    "old_provider_and_rounded_fallback_monthly_usd": num(old_monthly),
                                    "new_baseline_minus_old_monthly_usd": num(monthly - old_monthly),
                                    "list_repricing_monthly_effect_usd": num((total - bill) / 60 * VOLUME),
                                    "exact_labour_monthly_effect_usd": num((1-p)*(F-Decimal("9.17"))*VOLUME),
                                    "note": "Recorded response charges, not a full account invoice. No measured cache-saving claim."},
            "sensitivity": sensitivity}


def build(root=ROOT):
    snapshot = load(root / "evidence/d6_price_snapshot.json")
    hashes = {}
    schedules = []
    def read(path, model):
        raw = (root / path).read_bytes()
        hashes[path] = hashlib.sha256(raw).hexdigest()
        d = json.loads(raw)
        schedules.append(validate(d, model))
        return model_cost(d, path, snapshot["models"])
    models = [read(path, model) for path, model in zip(INPUTS, MODELS)]
    separate = read(GPT, "openai/gpt-4.1-mini")
    if len({e["model"] for e in models}) != 5 or any(s != schedules[0] for s in schedules):
        raise ValueError("Model or trial schedule mismatch")
    cheapest = min(models, key=lambda x: x["layer_1"]["variable_per_referral_usd"])
    best = min(models, key=lambda x: x["expected_total_per_referral_usd"])
    c, e = dec(cheapest["layer_1"]["variable_per_referral_usd"]), dec(best["expected_total_per_referral_usd"])
    pstar = 1 - (e - c) / F
    return {"schema_version": 3, "status": "COMPLETE_FIVE_MODEL_COST_CALCULATION_WITH_STATED_LIMITATIONS",
            "reviewed_upstream_commit": "96c36139e483409acea577dc7f5e364540d722ca",
            "method": "Class 5 baseline: measured tokens times dated list prices; (1-p)*55*10/60; monthly fixed K",
            "source_sha256": hashes, "prices": snapshot, "paid_model_calls_this_calculation": 0,
            "assumptions": {"currency": "USD", "monthly_referrals": VOLUME, "fallback_hourly_usd": 55,
                "fallback_minutes": 10, "fixed_monthly_usd": 0,
                "fixed_scope": "Abin's Sep 14 prototype-only paid-service confirmation; production maintenance, monitoring, recurring eval and equipment budgets not established",
                "p_scope": "Raw automated code-check proxy, not clinical accuracy or human-judgement pass rate",
                "mix": "30 ordinary cases once; 10 negative cases three times; not production prevalence",
                "cache_reasoning": "No assumed cache discount; recorded output tokens used without adding estimated hidden reasoning tokens",
                "model_selection": "DeepSeek is minimum observed proxy cost in final five, not an approval to deploy"},
            "models": models, "recommended_model": best["model"],
            "recommended_model_separate": separate,
            "supplementary_qwen": {"source": "ProblemB_qwen_60trial_evidence.zip", "included_in_final_five": False},
            "break_even": {"cheap_model": cheapest["model"], "dear_model": best["model"],
                          "required_cheap_success_rate": num(pstar),
                          "observed_cheap_success_rate": cheapest["code_check_success_rate"], "formula": "1-(E-C)/F"},
            "limitations": ["No run-time commit or prompt hashes in the live records; same v2 label and schedule alone do not prove all settings identical.",
                           "Human judgement is separate; the 3/10 sample belongs to separate GPT evidence and its exact run mapping needs confirmation.",
                           "Exact paired B prefix and D observation-growth token measurements remain unavailable; character estimates are not measured tokens.",
                           "Monthly per-user spending limit is not evidenced. Existing caps are 8 turns and 60000 tokens per run.",
                           "Failure-only labour proxy excludes routine labour for correct clinical escalation; full production cost is not established."]}


def render(data):
    lines = ["# D6 Cost to serve", "", "Baseline uses recorded input/output tokens at dated list prices, not provider-reported charges. The provider view is retained separately for reconciliation.", "",
             "## Three layers", "", "1. Variable per referral: input tokens × input list price + output tokens × output list price, averaged over 60 trials. Extra paid prototype tool/retrieval fees are zero.",
             "2. Expected fallback per referral: (1 − automated success rate) × (55 × 10/60). The exact labour cost is $9.166666…; $9.17 is rounded.",
             "3. Fixed monthly K: $0 additional paid prototype services under the stated assumption. This does not cover unmeasured production maintenance, monitoring, recurring evaluation or equipment.",
             "", "Monthly = 4,000 × (Layer 1 + Layer 2) + K. These are scoped benchmark scenarios, not clinical deployment quotations.",
             "", "## Final five model comparison", "", "| Model | Code passes | Input tokens | Output tokens | List USD per referral | Expected USD per referral | Monthly USD |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for m in data["models"]:
        lines.append(f'| {m["model"]} | {m["code_check_passed"]}/60 | {m["tokens_in"]} | {m["tokens_out"]} | {m["layer_1"]["variable_per_referral_usd"]:.9f} | {m["expected_total_per_referral_usd"]:.9f} | {m["monthly"]["total_usd"]:,.2f} |')
    lines += ["", "All five files contain 40 cases and 60 unique scheduled trials, with live usage, provider costs and boolean verdicts. Llama uses the newly completed scored JSON, not the earlier staged ZIP. GPT-4.1 mini remains separate; Qwen remains supplementary.",
              "", "## Reconciliation with Abin previous table", "", "| Model | Recorded API USD for battery | Previous monthly USD | New baseline monthly USD | Difference USD |",
              "|---|---:|---:|---:|---:|"]
    for m in data["models"]:
        p=m["provider_comparison"]
        lines.append(f'| {m["model"]} | {p["recorded_battery_usd"]:.6f} | {p["old_provider_and_rounded_fallback_monthly_usd"]:,.2f} | {m["monthly"]["total_usd"]:,.2f} | {p["new_baseline_minus_old_monthly_usd"]:+.6f} |')
    lines += ["", "Differences combine list-price repricing and the exact labour formula. JSON separates those two effects; displayed rounding can differ by one cent when subtracting rounded totals. A difference from provider charges does not prove a caching benefit.", "",
              "## Sensitivity and break even", "", "| Model | p minus 10 points monthly USD | Base monthly USD | p plus 10 points monthly USD |",
              "|---|---:|---:|---:|"]
    for m in data["models"]:
        s=m["sensitivity"]
        lines.append(f'| {m["model"]} | {s[0]["monthly_total_usd"]:,.2f} | {s[1]["monthly_total_usd"]:,.2f} | {s[2]["monthly_total_usd"]:,.2f} |')
    b=data["break_even"]
    lines += ["", f'Mistral needs {b["required_cheap_success_rate"]:.4%} success to match DeepSeek, versus its observed {b["observed_cheap_success_rate"]:.4%}. Formula: p* = 1 − (E − C)/F; C is cheap-model tokens only and E includes the comparison model fallback.',
              "", "An unclipped 10-percentage-point change shifts monthly fallback by $3,666.67. DeepSeek remains lowest if all five rates shift together by the same ±10 points; independently varying rates can reverse rankings. This is scenario analysis, not a confidence interval.",
              "", "## Four levers and limits", "", "- B: docs/D2_TOOL_LAYER.md reports 5,189 → 5,080 system-prompt characters; its characters/4 tokens are estimates, not exact paired B measurements.",
              "- T: evidence/d2_parallel_comparison.json records scripted grouping of the same six calls from six turns to four; input-token estimates fall from 42,000 to 24,000. These are not live token savings.",
              "- D: paired final-version observation-growth token measurements remain unavailable.",
              "- P: historical Gemini Flash-Lite V1/V2 automated passes are 49/60 → 48/60; lower token use does not establish an all-in cost improvement.",
              ""]
    lines += ["- "+s for s in data["limitations"]]
    lines += ["", "## Reproduce", "", "Run python cost_to_serve.py to regenerate; python cost_to_serve.py --check verifies without writing. Run python -m unittest -v test_cost_to_serve. No key, network or paid model call is needed.",
              "", "Schema v3: monthly projections live under monthly; layer_3 now correctly contains fixed_monthly_usd. Provider amounts are under provider_comparison. Consumers of the earlier schema must use these names.",
              "", "The Class 5 pure functions in d6_course_costs.py are reused and cross-checked with Decimal arithmetic. Each raw evidence file has a SHA256 in the output.",
              "", f'Price source: {data["prices"]["source"]}; snapshot checked {data["prices"]["checked_utc"]}. No caching discount is assumed.',
              "", f'Reviewed source commit: {data["reviewed_upstream_commit"]}.', ""]
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args=p.parse_args()
    data=build()
    outputs={ROOT/"evidence/d6_cost_to_serve.json":json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
             ROOT/"docs/D6_COST_TO_SERVE.md":render(data)}
    for path,text in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8")!=text:
                p.exit(1,"Stale output: "+str(path)+"\n")
        else:
            path.write_text(text,encoding="utf-8")
    print("D6 checked" if args.check else "D6 JSON and documentation regenerated")


if __name__ == "__main__":
    main()
