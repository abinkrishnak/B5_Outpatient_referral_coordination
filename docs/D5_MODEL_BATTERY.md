# D5 - Reproducibility and live model battery

## D5(a): free reproducibility

`python run_eval.py` remains the marker-facing command. It uses the scripted
backend by default, needs neither a key nor a network connection, and produces
the D4 60-trial result. This is a test of fixtures, tool wiring, guardrails and
the deterministic code check; it is **not** a model-quality claim.

## D5(b): measured live experiment

`run_model_battery.py` is deliberately separate and opt-in. It uses the single
vendor-neutral `config.MODEL` string and the one OpenRouter adapter in
`backends.py`. For every API response it records `prompt_tokens` and
`completion_tokens`; when OpenRouter returns `usage.cost`, that provider value
is used. Otherwise the record states that configured per-token prices supplied
the cost. Neither is described as an estimate.

Run a small preflight first, then a complete battery only when the result is
parseable and the spend is acceptable. In PowerShell, without putting a key in
a file or chat:

```powershell
$env:OPENROUTER_API_KEY = Read-Host "OpenRouter key"
python check_openrouter_credit.py
python run_model_battery.py --model provider/model --pilot 5 --synthetic-approval --max-cost 0.25
python run_model_battery.py --model provider/model --full --synthetic-approval --max-cost 2
```

Repeat `--model` to compare models. A completed full run contains 60 trials:
30 ordinary cases once and 10 negative cases three times. Each model produces
its own `evidence/d5_live_<model>_<contract>.json`, including raw records, code-check
results, judgement queue, token counts, turn counts, cost basis and whether the
user-set budget stopped the run.

The OpenRouter adapter allows a 90-second read and retries bounded transient
transport/provider-capacity failures. An exhausted timeout or HTTP failure
produces no valid battery result: retain any earlier pilot under a
`d5_pilot_...` filename and rerun the full battery from the beginning.
Because a response could be lost after the provider processed it, provider-
reported cost (and the key's credit check) remains the final cost authority.

`--synthetic-approval` is required for a full benchmark because `AUTONOMY` is
`confirm`. It is acceptable only here: the supplied `book_slot` is a no-op
fixture. In a real service, an operator must approve the exact booking payload;
the live agent defaults to holding the gate if no approval callback is given.

## Comparison rules

Keep the following fixed while comparing models: 40-case dataset, answer key,
prompt/tool-contract version, temperature zero, guardrail settings, trial
schedule and autonomy setting. Report each model's completed trial count,
code-check pass rate, median/worst turns, total input/output tokens, total
cost, and negative-case pass rate. Read the judgement queue separately; do not
mistake the automated code check for a prose-quality review.

The D2 V1-vs-V2 descriptor experiment is a separate paired experiment: use
one model, all other settings fixed, and change only `--tool-contract`. Then
run `compare_tool_contracts.py` over the two evidence files.

## Completed V2 battery

All five completed runs used the same 40 cases / 60 trials, V2 tool contract,
temperature zero, evaluation date, synthetic fixture approval and guardrails.
They span five distinct model families, as required. Only completed 60-trial
evidence is included below.

| Model | Pass rate | Median turns | Measured cost |
|---|---:|---:|---:|
| Claude Haiku 4.5 (Anthropic) | 48/60 (80.0%) | 3.5 | US$0.736601 |
| DeepSeek Chat V3 (DeepSeek) | **51/60 (85.0%)** | 4.0 | US$0.097416 |
| Gemini 2.5 Flash (Google) | 49/60 (81.7%) | 4.0 | US$0.189767 |
| Llama 3.3 70B Instruct (Meta) | 45/60 (75.0%) | 4.0 | US$0.064365 |
| Mistral Small 24B (Mistral) | 22/60 (36.7%) | 1.0 | US$0.015020 |

DeepSeek Chat V3 is the recommended model in the required five-family
comparison: it has the highest measured code-check pass rate and the lowest
expected cost after the human-fallback layer is applied. Mistral is the
cheapest raw API option but the weakest on the evaluation set, demonstrating
why token price alone is not a safe deployment criterion. GPT-4.1 mini is
retained as a separate supplementary recommended-model evaluation, not as one
of the five required family-distinct comparison rows.
