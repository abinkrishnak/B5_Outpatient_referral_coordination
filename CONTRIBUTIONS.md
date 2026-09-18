# Contributions

This table records the team declaration's planned ownership. Update the
"Completed contribution" column with actual work and commit hashes before
submission. Do not claim work performed by another person without agreement.

| Team member | Declared responsibility | Completed contribution / evidence |
|---|---|---|
| Zhao Xiaonan | D1, D2(a), D2(c): loop and tools | Confirm actual work and commits with Zhao. |
| Ge Jiayao | D1, D2(a), D2(c): loop and tools | Confirm actual work and commits with Ge. |
| Tan Jinxuan | V1 baseline system：D1;V1 scripted evaluation：D4;V1 and part of V2 live model testing：D5;Guardrail checks：D3;
D7 controlled failure experiments：D7 | Build the V1 baseline and conducted the V1/V2 model evaluations across the referral cases, also implemented and documented the guardrail checks and co-developed the D7 controlled failure experiments, comparing the working, broken, and restored agents. |
| Kaivelikkal Abin Krishna | D2(b), D3: descriptors, V1-to-V2 rewrite, guardrails | Current integration/checkpoint commits; add exact authored portions after team review. |
| Wang Hanfei | D4, D5(a): evaluation harness and scripted run | Confirm actual work and commits with Wang. |
| Liu Siwen | D6: cost model, ledger and sensitivity | Reviewed and updated the D6 cost-to-serve artifacts: cost_to_serve.py, evidence/d6_cost_to_serve.json, and docs/D6_COST_TO_SERVE.md; commits 8b194e7e, 63029b5a, and 35d2a086. |

## Shared obligations

- Every member owns or reviews 5–8 evaluation cases in the `REF-6001` to
  `REF-6025` range. Record the case IDs beside each name after allocation.
- Every member runs one live-model experiment using their own private OpenRouter
  key and commits only the resulting evidence, never a key.
- Everyone reviews the report and presentation. The declaration is stored at
  repository root as `TEAM_DECLARATION.md`.

## Shared project assets

The original teammate hand-off has been integrated into the runnable project,
especially `problem_b_scripts.py` and the historical `evidence/v1_*.csv`
files. The duplicate ZIP archive is deliberately not included in the final
repository: team members should run the root-level project, not a stale copy.
