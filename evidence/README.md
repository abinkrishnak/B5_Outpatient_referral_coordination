# Evidence guide

This folder holds reproducible outputs, not source code. Read the small JSON
files and the D2-D7 documentation before opening large per-trial live results.

| File or group | Purpose |
|---|---|
| `d2_parallel_comparison.json` | Parallel versus sequential tool-call comparison. |
| `d3_guardrail_checklist.json` | Eleven scripted code-layer safety checks. |
| `d4_evaluation_audit.json` | Confirms the 40-case, 60-trial evaluation design. |
| `d5_live_*.json` | Measured live-model trials: decision, tools, tokens, cost, guardrails. |
| `d5_pilot_*.json` | Diagnostic pilots retained for transparency; not final model scores. |
| `d6_cost_to_serve.json` | Three-layer cost-to-serve calculations. |
| `d7_tool_contract_failure.json` | V1/V2 tool-contract failure and restoration evidence. |
| `v1_*.csv` | Historical teammate hand-off evidence, retained as provenance. |

The report should cite final D2-D7 files. Do not treat a pilot file as a final
model result. Rebuild derived files with the root-level scripts when input
evidence changes.

Five completed 60-trial V2 files are the final D5 comparison. Other
`d5_live_*.json` files may be incomplete provider/protocol diagnostics; check
their `complete` field before using them in D5 or D6.

Qwen supplementary evidence is currently retained as
`ProblemB_qwen_60trial_evidence.zip` at the repository root. It contains the
staged 60-trial checkpoint and batch records, including the original timeout
and transient HTTP 429 events in `retry_of` fields. Treat it as supplementary
unless it is explicitly added to the final five-model D5 comparison.
