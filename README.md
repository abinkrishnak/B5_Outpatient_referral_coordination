# PE6201 A2 Applied AI System

This repository contains one hand-written ReAct agent for outpatient referral coordination. It uses local fixture data and keeps the irreversible `book_slot` action behind a human confirmation gate.

The final design exposes five model-visible tools: four read tools (`get_referral`, `lookup_patient`, `check_referral_criteria` and `get_clinic_slots`) plus the gated write-like action `book_slot`. The evaluation set contains 40 referrals and 60 scheduled trials.

## Submission results

| Measure | Result |
|---|---:|
| Offline scripted evaluation | 60/60 code-check passes |
| Evaluation set | 40 referrals, 60 trials |
| Guardrail suite | 12/12 passed, including 3 malicious free-text cases |
| V1 versus V2 experiment | V2: 48/60, $0.048662 |
| Completed V2 live models | 5 |
| Recommended-model code check | GPT-4.1 mini: 51/60 (85.0%) |
| Baseline human judgement sample | 1/10 (10.0%); remediation rerun pending |
| Expected monthly cost at 4,000 referrals | $5,510.17 |

Read [the results dashboard](docs/RESULTS_DASHBOARD.md) for the consolidated D0-D7 evidence.

## Current evidence status

- D0 documents rungs 1-7, the workflow test, ground-truth boundary and reliability arithmetic.
- D3 is complete: the final script and committed evidence show 12/12 deterministic checks, including three malicious free-text attack classes.
- D4 has a named human reviewer, **TAN JINGXUAN**. The pre-remediation ten-case judgement review is committed at 1/10. The strengthened evidence-contract prompt and full-record judgement queue are committed; the same-model post-remediation rerun and review remain pending.
- D7 is complete: both controlled baseline -> component removed -> restored experiments and their generated evidence are committed.

## Architecture

```mermaid
flowchart LR
  R[Referral ID] --> A[Single ReAct loop]
  A --> T[Four read tools]
  T --> A
  A --> G{Confirm gate}
  G -->|approved only| B[book_slot]
  G -->|held| E[Escalate or suggest]
  B --> F[Final record]
```

The model chooses the next tool action. Ordinary code enforces the step cap, budget ceiling, action de-duplication, booking eligibility and autonomy gate.

## Reproduce the technical evidence

Run from the repository root. These commands use no network and require no API key:

```powershell
python run_eval.py
python audit_evaluation_set.py
python run_guardrail_checklist.py
python d2_parallel_comparison.py
python demo_loop_failure.py
python demo_tool_contract_failure.py
```

`config.py` is committed with the safe scripted backend. Live model runs are opt-in through `run_model_battery.py`. API keys must never be committed.

## Repository map

| Location | Purpose |
|---|---|
| `agent.py`, `tools.py`, `guardrails.py` | Agent loop, tool contracts and deterministic controls |
| `backends.py`, `prompt.py`, `config.py` | Scripted/live adapters and model protocol |
| `harness.py`, `run_eval.py` | Evaluation and reproducibility |
| `A2_reference_data/` | Professor-provided records plus labelled Problem B extensions |
| `docs/` | D0-D7 design and evidence notes |
| `evidence/` | Machine-readable experiment outputs |
| `results.json` | Current scripted evaluation output |
| `ProblemB_Team_Runbook.ipynb` | Optional guided walkthrough |

## Evidence conventions

Only `complete: true` live files with 60 trials count in final D5 comparisons. Pilot and incomplete provider/protocol files are diagnostics, not model-quality results. Derived JSON/CSV files must be regenerated whenever their source script changes. Baseline evidence is never overwritten; a remediation rerun must use a new evidence filename and record the exact prompt revision and run date.
