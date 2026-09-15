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
| Gemini 2.5 Flash Lite | $0.000811 | $1.834000 | $1.834811 | $7,339.24 |
| Gemini 2.5 Flash | $0.003238 | $1.528333 | $1.531572 | $6,126.29 |
| GPT-4.1 mini | $0.002042 | $1.375500 | $1.377542 | $5,510.17 |
| GPT-4o mini | $0.000790 | $5.196333 | $5.197123 | $20,788.49 |
| Llama 3.3 70B Instruct | $0.001044 | $2.598167 | $2.599210 | $10,396.84 |

GPT-4.1 mini is the lowest expected-cost option in this measured experiment.
Its small additional inference cost is overwhelmed by the lower expected
human-triage fallback cost.
