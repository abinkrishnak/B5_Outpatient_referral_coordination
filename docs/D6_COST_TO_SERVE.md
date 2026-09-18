# D6 - Cost to serve

The model uses the three layers required for Problem B. It deliberately uses
measured D5 API costs rather than scripted token estimates.

1. **Layer 1 — variable inference cost:** total provider-reported cost divided
   by all completed trials.
2. **Layer 2 — expected fallback:** observed code-check failure rate multiplied
   by the supplied US$9.17 triage-nurse cost for a failed referral.
3. **Layer 3 — monthly scale:** per-referral values multiplied by the fixed
   4,000 referrals per month.

Run:

```powershell
python cost_to_serve.py
```

The committed `evidence/d6_cost_to_serve.json` retains raw counts and all
intermediate quantities. The raw failure rate is conservative because it
includes the documented REF-5590 conflict: operational policy correctly exits
early for a red flag, while that answer-key row additionally requests
slot-not-taken evidence. Do not remove this row silently; state the sensitivity
in the report.

The key business finding is expected to be that model-token cost is tiny next
to human fallback cost. Therefore a small accuracy or safety improvement can
be economically worthwhile even when its inference cost is higher.

## Completed-model result 

| Model | Layer 1 / referral | Layer 2 / referral | Expected total / referral | Monthly total at 4,000 |
|---|---:|---:|---:|---:|
| Claude Haiku 4.5 | $0.012277 | $1.834000 | $1.846277 | $7,385.11 |
| DeepSeek Chat V3 | $0.001624 | $1.375500 | **$1.377124** | **$5,508.49** |
| Gemini 2.5 Flash | $0.003163 | $1.681167 | $1.684329 | $6,737.32 |
| Llama 3.3 70B Instruct | $0.001073 | $2.292500 | $2.293573 | $9,174.29 |
| Mistral Small 24B | $0.000250 | $5.807667 | $5.807917 | $23,231.67 |

DeepSeek Chat V3 is the lowest expected-cost option in the required,
five-family comparison. Its slightly higher raw API cost than Mistral is
overwhelmed by the lower expected human-triage fallback cost. GPT-4.1 mini is
retained separately as supplementary recommended-model evidence and is not
part of this family-distinct D6 table.

## Sensitivity and break-even

The committed JSON includes each model at its observed success rate and at
plus/minus 10 percentage points. This is the required sensitivity: a 10-point
success-rate change shifts expected cost by $0.917 per referral, or $3,668 per
month at 4,000 referrals. It dwarfs the measured Layer 1 differences.

For the lower-variable-cost Mistral Small 24B to match DeepSeek Chat V3, it
would need a success rate of 84.99%, rather than its observed 36.67%. The
break-even formula is `p_cheap = p_dear - (dear_variable - cheap_variable) /
failure_cost`. This supports the model choice without claiming that a one-run
pass-rate difference is statistically conclusive.
