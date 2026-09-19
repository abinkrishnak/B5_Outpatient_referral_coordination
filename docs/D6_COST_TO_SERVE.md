# D6 Cost to serve

Baseline uses recorded input/output tokens at dated list prices, not provider-reported charges. The provider view is retained separately for reconciliation.

## Three layers

1. Variable per referral: input tokens × input list price + output tokens × output list price, averaged over 60 trials. Extra paid prototype tool/retrieval fees are zero.
2. Expected fallback per referral: (1 − automated success rate) × (55 × 10/60). The exact labour cost is $9.166666…; $9.17 is rounded.
3. Fixed monthly K: $0 additional paid prototype services under the stated assumption. This does not cover unmeasured production maintenance, monitoring, recurring evaluation or equipment.

Monthly = 4,000 × (Layer 1 + Layer 2) + K. These are scoped benchmark scenarios, not clinical deployment quotations.

## Final five model comparison

| Model | Code passes | Input tokens | Output tokens | List USD per referral | Expected USD per referral | Monthly USD |
|---|---:|---:|---:|---:|---:|---:|
| anthropic/claude-haiku-4.5 | 48/60 | 449676 | 57385 | 0.012276683 | 1.845610017 | 7,382.44 |
| deepseek/deepseek-chat-v3-0324 | 51/60 | 417556 | 21236 | 0.002093750 | 1.377093750 | 5,508.38 |
| google/gemini-2.5-flash | 49/60 | 415475 | 28444 | 0.003262542 | 1.683818097 | 6,735.27 |
| meta-llama/llama-3.3-70b-instruct | 45/60 | 414337 | 16631 | 0.000779260 | 2.292445927 | 9,169.78 |
| mistralai/mistral-small-24b-instruct-2501 | 22/60 | 270648 | 18616 | 0.000250361 | 5.805805917 | 23,223.22 |

All five files contain 40 cases and 60 unique scheduled trials, with live usage, provider costs and boolean verdicts. Llama uses the newly completed scored JSON, not the earlier staged ZIP. GPT-4.1 mini remains separate; Qwen remains supplementary.

## Reconciliation with Abin previous table

| Model | Recorded API USD for battery | Previous monthly USD | New baseline monthly USD | Difference USD |
|---|---:|---:|---:|---:|
| anthropic/claude-haiku-4.5 | 0.736601 | 7,385.11 | 7,382.44 | -2.666667 |
| deepseek/deepseek-chat-v3-0324 | 0.097416 | 5,508.49 | 5,508.38 | -0.119400 |
| google/gemini-2.5-flash | 0.189767 | 6,737.32 | 6,735.27 | -2.045411 |
| meta-llama/llama-3.3-70b-instruct | 0.064365 | 9,174.29 | 9,169.78 | -4.507292 |
| mistralai/mistral-small-24b-instruct-2501 | 0.015020 | 23,231.67 | 23,223.22 | -8.444332 |

Differences combine list-price repricing and the exact labour formula. JSON separates those two effects; displayed rounding can differ by one cent when subtracting rounded totals. A difference from provider charges does not prove a caching benefit.

## Sensitivity and break even

| Model | p minus 10 points monthly USD | Base monthly USD | p plus 10 points monthly USD |
|---|---:|---:|---:|
| anthropic/claude-haiku-4.5 | 11,049.11 | 7,382.44 | 3,715.77 |
| deepseek/deepseek-chat-v3-0324 | 9,175.04 | 5,508.38 | 1,841.71 |
| google/gemini-2.5-flash | 10,401.94 | 6,735.27 | 3,068.61 |
| meta-llama/llama-3.3-70b-instruct | 12,836.45 | 9,169.78 | 5,503.12 |
| mistralai/mistral-small-24b-instruct-2501 | 26,889.89 | 23,223.22 | 19,556.56 |

Mistral needs 84.9799% success to match DeepSeek, versus its observed 36.6667%. Formula: p* = 1 − (E − C)/F; C is cheap-model tokens only and E includes the comparison model fallback.

An unclipped 10-percentage-point change shifts monthly fallback by $3,666.67. DeepSeek remains lowest if all five rates shift together by the same ±10 points; independently varying rates can reverse rankings. This is scenario analysis, not a confidence interval.

## Four levers and limits

- B: docs/D2_TOOL_LAYER.md reports 5,189 → 5,080 system-prompt characters; its characters/4 tokens are estimates, not exact paired B measurements.
- T: evidence/d2_parallel_comparison.json records scripted grouping of the same six calls from six turns to four; input-token estimates fall from 42,000 to 24,000. These are not live token savings.
- D: paired final-version observation-growth token measurements remain unavailable.
- P: historical Gemini Flash-Lite V1/V2 automated passes are 49/60 → 48/60; lower token use does not establish an all-in cost improvement.

- No run-time commit or prompt hashes in the live records; same v2 label and schedule alone do not prove all settings identical.
- Human judgement is separate; the 3/10 sample belongs to separate GPT evidence and its exact run mapping needs confirmation.
- Exact paired B prefix and D observation-growth token measurements remain unavailable; character estimates are not measured tokens.
- Monthly per-user spending limit is not evidenced. Existing caps are 8 turns and 60000 tokens per run.
- Failure-only labour proxy excludes routine labour for correct clinical escalation; full production cost is not established.

## Reproduce

Run python cost_to_serve.py to regenerate; python cost_to_serve.py --check verifies without writing. Run python -m unittest -v test_cost_to_serve. No key, network or paid model call is needed.

Schema v3: monthly projections live under monthly; layer_3 now correctly contains fixed_monthly_usd. Provider amounts are under provider_comparison. Consumers of the earlier schema must use these names.

The Class 5 pure functions in d6_course_costs.py are reused and cross-checked with Decimal arithmetic. Each raw evidence file has a SHA256 in the output.

Price source: https://openrouter.ai/api/v1/models; snapshot checked 2026-09-17T13:51:46.180823+00:00. No caching discount is assumed.

Reviewed source commit: 96c36139e483409acea577dc7f5e364540d722ca.
