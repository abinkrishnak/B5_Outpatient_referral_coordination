# D4 - Evaluation set and grading

## Set design

The evaluation set contains **40 isolated referral cases**: 30 booking cases and 10 negative cases (7 escalations and 3 requests for information). Negative cases receive three trials and ordinary cases one, so each model is evaluated over **60 trials**.

| Coverage | Examples |
|---|---|
| Routine, soon and urgent bookings | `REF-5602`, `REF-5631`, `REF-6006` to `REF-6015` |
| Clinical-window boundaries | `REF-6016` to `REF-6018`; `REF-6005` proves the clock is `as_of`, not `date_received` |
| Negative clinical outcomes | red flags, missing tests, specialty mismatch, future duplicate, no valid slot |
| Untrusted free text | overt instruction (`REF-5703`), fake tool output (`REF-5711`), benign false-positive control (`REF-6024`) |
| Common shortcut errors | past appointment is not a duplicate; wrong urgency band must not be booked |

## Two grading layers

### 1. Code check

`harness.code_check` compares fixed, machine-checkable facts with `expected_outcomes_B.json`: decision, single trigger, exact missing item, exact booked slot, required tool evidence, and gated-action count. It is deterministic and produces the reported trial pass rate.

For the current GPT-4.1 mini baseline:

- Prompt/tool contract: v2 before the evidence-contract remediation
- Trials: 60
- Code-check passes: 51
- Code-check pass rate: **85.0%**
- Evidence: `evidence/d5_live_openai_gpt-4.1-mini.json`

### 2. Human judgement check

Natural-language explanations are reviewed separately. The reviewer receives the complete decision record, tool evidence, fired guardrails, and the case-specific `must_record` list. A pass requires every required fact to be explicitly supported; substring matching is not used.

- Reviewer: **TAN JINGXUAN**
- Baseline sample: 10 deliberately varied cases
- Baseline judgement passes: 1
- Baseline judgement pass rate: **10.0%**
- Detailed record: `docs/JUDGEMENT_REVIEW_TEMPLATE.md`

The two percentages answer different questions and are never combined. The 85.0% code result shows how often fixed outcomes were correct. The 10.0% judgement result shows that the baseline explanations often omitted required rationale even when the structured decision was correct.

## Remediation and fair comparison

The baseline evidence remains unchanged and auditable. The system prompt has been strengthened with a decision-specific evidence contract requiring a non-empty, complete `reason` for `book`, `request_information`, and `escalate`. The judgement queue now includes the full record rather than only the reason string.

A post-remediation evaluation must:

1. use the same 40 cases and 60-trial policy;
2. use the same GPT-4.1 mini model and v2 tool contract;
3. save results under a new filename rather than overwriting the baseline;
4. repeat the same ten-case human review with TAN JINGXUAN;
5. report code-check and judgement-check pass rates separately; and
6. state the run date and exact prompt revision.

Until that rerun is completed, the project must describe the revised judgement result as **pending**, not as an achieved improvement.
