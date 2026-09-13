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
