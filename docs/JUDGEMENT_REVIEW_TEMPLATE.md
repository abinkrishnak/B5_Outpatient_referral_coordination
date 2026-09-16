# D4 Human Judgement Review

## Status

**Pending human sign-off.** This file is intentionally not pre-filled by code or by a language model. A named team member must read the actual decision records, enter the review date and complete every row before submission.

- Reviewer: ______________________________
- Review date (YYYY-MM-DD): ______________
- Evidence source reviewed: `evidence/d5_raw_live_results.csv`
- Expected outcomes source: `A2_reference_data/expected_outcomes_B.json`

## Review method

Run the code check first. Then inspect the decision record for each sampled case without changing the automated result.

Mark **Yes** only when all of the following are true:

1. The stated outcome agrees with the expected outcome.
2. The reason names the required case-specific evidence from `must_record`.
3. The reasoning follows the routing order and does not claim an action that is absent from the tool trace.
4. A book decision identifies the booked slot and confirms the gate; an escalation or request-information decision states its trigger.

A judgement pass requires **Yes** in both judgement columns. Record a short, auditable reason for every **No**. Do not infer missing evidence from the answer key if the model did not state it.

## Review sheet

| Case | Expected outcome | Required evidence named? | Reason supports outcome? | Judgement pass? | Reviewer notes |
|---|---|---|---|---|---|
| REF-5602 | book | Yes / No | Yes / No | Yes / No | |
| REF-5590 | escalate | Yes / No | Yes / No | Yes / No | |
| REF-5614 | request_information | Yes / No | Yes / No | Yes / No | |
| REF-5684 | escalate | Yes / No | Yes / No | Yes / No | |
| REF-5697 | escalate | Yes / No | Yes / No | Yes / No | |
| REF-5703 | escalate | Yes / No | Yes / No | Yes / No | |
| REF-5711 | escalate | Yes / No | Yes / No | Yes / No | |
| REF-6016 | book | Yes / No | Yes / No | Yes / No | |
| REF-6018 | book | Yes / No | Yes / No | Yes / No | |
| REF-6024 | book | Yes / No | Yes / No | Yes / No | |

## Completion check

Before final submission, confirm:

- [ ] Reviewer name and date are present.
- [ ] All 10 rows have both judgement answers.
- [ ] Every failed row has a note.
- [ ] Judgement pass count and rate are reported separately from code-check accuracy.
- [ ] The completed review is committed as evidence; this blank template is not presented as completed work.

This judgement layer is deliberately human. It tests whether the written reason is supported and complete; it is not another model score and must not be fabricated from the code-check result.
