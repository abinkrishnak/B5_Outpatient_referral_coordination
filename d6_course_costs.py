"""Three pure functions from the PE6201 Class 5 cost-to-serve notebook.
Source notebook SHA256: aef03ffef6fe3cce1fb2128a53d75e92f5517d163f2cb378cc9c0b02dccb93c4
Only these functions are reused; no notebook code or API call is executed.
"""
PRICES = {}

def variable_cost(tier, fresh_in=0, cached_in=0, out=0, retrieval_usd=0.0, tool_usd=0.0):
    "LAYER 1 — per-task variable cost, US dollars."
    p = PRICES[tier]
    assert fresh_in >= 0 and cached_in >= 0 and out >= 0, "token counts cannot be negative"
    return (fresh_in / 1e6 * p["in"]
            + cached_in / 1e6 * p["cached_in"]
            + out / 1e6 * p["out"]
            + retrieval_usd + tool_usd)

def cost_per_successful_task(var_usd, success_rate, failure_usd):
    "LAYER 1 + LAYER 2. The number to quote."
    assert 0.0 <= success_rate <= 1.0, "success rate is a probability, not a percentage"
    assert failure_usd >= 0, "a failure cannot cost less than nothing"
    return var_usd + (1.0 - success_rate) * failure_usd

def monthly(var_usd, success_rate, failure_usd, volume, fixed_monthly_usd=0.0):
    "Everything, for a month."
    return cost_per_successful_task(var_usd, success_rate, failure_usd) * volume + fixed_monthly_usd
