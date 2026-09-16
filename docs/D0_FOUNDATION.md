# D0 Foundation

## Placement on the Class 4 ladder

Problem B is an agent use case, but the design deliberately keeps deterministic work below the agent boundary.

| Rung | Alternative | Decision for this project |
|---|---|---|
| 1 | Plain language model response | Rejected: the answer needs current patient, referral, rule and slot records. |
| 2 | Prompted / structured response | Useful for the final decision record, but insufficient for retrieval and booking. |
| 3 | Retrieval-augmented generation (RAG) | Rejected as the core design: the sources are structured systems of record, not a document corpus. |
| 4 | Tool-using workflow | Retained for deterministic checks and gated execution. |
| 5 | Conditional workflow | Retained for the ordered red-flag, department, mandatory-test and duplicate checks. |
| 6 | Agentic retrieval | Partly relevant because the model chooses which structured lookup to call next, but retrieval alone cannot complete the task. |
| 7 | Agent | Selected: the model observes tool results, chooses the next action, may loop during slot search, and can request a gated real-world action. |

The solution is therefore a small ReAct agent surrounded by deterministic tools and guardrails. Calling it an agent does not mean every step should be probabilistic.

## Pre-code workflow test

The referral path has conditional routing:

1. Fetch the referral.
2. Apply the referral criteria in order: hostile instruction, red flag, wrong department, missing mandatory test.
3. Check the patient record for an existing future same-specialty appointment.
4. Stop at the first triggered rule; otherwise search the correct urgency band and time window.
5. Ask for confirmation before the irreversible `book_slot` action.
6. Produce a structured decision record with evidence and operational metrics.

This cannot be a single fixed sequence because the next useful action depends on observations. For example, an incomplete referral must stop before slot search, while a routine referral may need several slot queries before an eligible date appears.

## Ground-truth and machine-speed test

The authoritative facts come from structured reference records: referrals, patients, specialties, urgency bands, contacts and clinic slots. The agent is not asked to invent those facts. Tools retrieve or calculate them at machine speed; the model is responsible for routing and explanation. Human confirmation remains mandatory for booking because it changes an external appointment state and the input contains untrusted clinical free text.

## Why this is not ordinary RAG

Ordinary RAG retrieves passages and drafts an answer. This system selects among typed tools, applies stop conditions, can perform several dependent actions, and can propose a write operation. The retrieval is agent-directed, but the safety-critical rules and the write gate remain deterministic.

## Reliability arithmetic

The live evaluation contains 60 labelled cases. V2 passed 51, so the observed end-to-end pass rate is:

```text
P = 51 / 60 = 0.85
```

Using the assignment's simple independence approximation, if a typical successful run has `T = 4` model turns and each turn succeeds with probability `s`, then `P ≈ s^T`. Therefore:

```text
s ≈ P^(1/T) = 0.85^(1/4) ≈ 0.960
```

This shows why reducing unnecessary turns matters. Keeping the same estimated per-turn reliability:

- at `T = 3`, predicted end-to-end reliability is about `0.960^3 ≈ 0.885`;
- at `T = 8`, it falls to about `0.960^8 ≈ 0.722`.

This is a diagnostic model, not a causal claim: turns are not truly independent, cases differ in difficulty, and the 60-case battery is finite. It is still useful for explaining the value of parallel independent lookups, compact tool returns and early stopping.

## What good looks like

1. Retrieve ground truth before deciding.
2. Stop on the first safety or completeness failure.
3. Never query slots after a terminal red flag or incomplete referral.
4. Search only the correct urgency band and legal window.
5. Book exactly one eligible slot only after explicit confirmation.
6. Record the decision, trigger, evidence, turns, tokens, latency, guardrail events and cost basis.
