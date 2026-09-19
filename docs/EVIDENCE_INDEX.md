# Evidence Index

| Report claim | Reproduce | Evidence |
|---|---|---|
| Problem B needs an agent and a booking gate | Read D0 | `D0_FOUNDATION.md` |
| ReAct loop and five tools | `python run_eval.py REF-5602` | `D1_AGENT_ARCHITECTURE.md`, `D2_TOOL_LAYER.md` |
| Parallel calls reduce turns | `python d2_parallel_comparison.py` | `evidence/d2_parallel_comparison.json` |
| V2 poka-yoke prevents silent invalid slot queries | `python demo_tool_contract_failure.py` | `evidence/d7_tool_contract_failure.json` |
| Guardrails block unsafe bookings | `python run_guardrail_checklist.py` | `evidence/d3_guardrail_checklist.json` |
| Evaluation set is 40 cases / 60 trials | `python audit_evaluation_set.py` | `evidence/d4_evaluation_audit.json` |
| Scripted backend is reproducible | `python run_eval.py` | `results.json` |
| Five live models were compared | `python summarize_live_results.py` | completed `evidence/d5_live_*.json` files |
| DeepSeek has lowest scoped baseline cost among the final five; GPT remains separate | `python cost_to_serve.py` | `evidence/d6_cost_to_serve.json`, `docs/D6_COST_TO_SERVE.md` |
| Loop-control failure increases cost without changing answer | `python demo_loop_failure.py` | `docs/D7_FAILURES.md` |

Only complete 60-trial live files support D5 and D6 claims. Incomplete provider
diagnostics are not cited as quality results.
