# PE6201 A2 Applied AI System

## Problem B Outpatient Referral Coordination

This repository contains a single, hand-written ReAct agent for coordinating
outpatient referrals. It uses local fixture data only and keeps the one
irreversible action, `book_slot`, behind a human confirmation gate.

The submission uses a five-tool V2 poka-yoke contract, a 40-referral
evaluation set (60 scheduled trials), code-layer safety checks, five completed
live-model evaluations, and a three-layer cost-to-serve model.

## Submission results

| Measure | Result |
|---|---:|
| Offline scripted evaluation | 60/60 code-check passes |
| Evaluation set | 40 referrals, 60 trials |
| Code-layer safety checklist | 11/11 passes |
| V1 versus V2 experiment | V2: 48/60, $0.048662 |
| Completed V2 live models | 5 distinct families |
| Recommended final-comparison model | DeepSeek Chat V3: 51/60 (85.0%) |
| Expected monthly cost at 4,000 referrals | $5,508.49 |

Read [the results dashboard](docs/RESULTS_DASHBOARD.md) first. It presents
the D0-D7 evidence, model comparison, cost model and controlled failures.

## Important evidence boundary

Automated code checks and human judgement are reported separately. The named
human review records 3/10 strict explanation passes after remediation; this is
not merged into the automated score. REF-5590 remains a documented
label-versus-protocol conflict: the safe red-flag rule requires immediate
escalation, while the supplied label also requests proof of a later slot lookup.

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

The loop is deliberately not a framework or multi-agent system. The model
chooses the next tool action; ordinary code enforces step, budget,
de-duplication, eligibility and autonomy controls.

## Reproduce the submission

Run from the repository root. These commands use no network and require no
API key.

```powershell
python run_eval.py
python audit_evaluation_set.py
python run_guardrail_checklist.py
python d2_parallel_comparison.py
python summarize_live_results.py
python cost_to_serve.py
python demo_loop_failure.py
python demo_tool_contract_failure.py
```

`config.py` is committed with the safe scripted backend. Live model runs are
opt-in through `run_model_battery.py`; API keys are requested only through a
hidden terminal prompt and must never be committed.

## Repository map

| Location | Purpose |
|---|---|
| `agent.py`, `tools.py`, `guardrails.py` | Production agent, tool contract and safety controls |
| `backends.py`, `prompt.py`, `config.py` | Vendor-neutral live adapter and model protocol |
| `harness.py`, `run_eval.py` | Evaluation and reproducibility |
| `A2_reference_data/` | Professor-provided data plus Problem B extensions |
| `docs/` | D0-D7 design and evidence notes |
| `evidence/` | Reproducible machine-readable experiment outputs |
| `results.json` | Current scripted evaluation output |
| `ProblemB_Team_Runbook.ipynb` | Optional guided walkthrough |

## Evidence conventions

Only `complete: true` files with 60 trials count in the final D5 model and D6
cost comparisons. Incomplete provider/protocol runs are retained locally as
diagnostics and are never reported as model-quality results.

## Team declaration

The submitted team declaration is retained as `TEAM_DECLARATION.docx`.
`CONTRIBUTIONS.md` records the agreed work allocation and is intentionally kept
separate from the technical evidence.
