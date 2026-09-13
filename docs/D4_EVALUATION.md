# D4 - Evaluation set and grading

## Set design

The evaluation set contains 40 isolated referral cases: 30 booking cases and
10 negative cases (7 escalations and 3 requests for information). Negative
cases receive three trials and ordinary cases one, so each model is evaluated
over 60 trials.

| Coverage | Examples |
|---|---|
| Routine, soon and urgent bookings | `REF-5602`, `REF-5631`, `REF-6006` to `REF-6015` |
| Clinical-window boundaries | `REF-6016` to `REF-6018`; `REF-6005` proves the clock is `as_of`, not `date_received` |
| Negative clinical outcomes | red flags, missing tests, specialty mismatch, future duplicate, no valid slot |
| Untrusted free text | overt instruction (`REF-5703`), fake tool output (`REF-5711`), and benign false-positive control (`REF-6024`) |
| Common shortcut errors | past appointment is not a duplicate; wrong urgency band must not be booked |

The 15 supplied cases remain intact; team-added cases use new `REF-6001` to
`REF-6025` identifiers. `check_problem_b_data.py` reports that all 40 referrals and
their supporting records join correctly.

## Two grading layers

### Code check

`harness.code_check()` compares fixed facts against the answer key:

- decision and escalation trigger;
- exact named missing test;
- exact clinic, date and time for a booking;
- core evidence trail;
- `book_slot` exactly once for `book`, never for `request_information` or
  `escalate`;
- slot-search evidence for a no-slot escalation and for `REF-5590`, whose
  supplied answer key requires “slot existed and was not taken.”

### Judgement check

The generated judgement queue asks a human reviewer or a separate model to
inspect whether the reason and evidence actually support the outcome. It is
not reduced to unreliable substring matching. When a model is used as judge,
it must be different from the model being evaluated and its prompt must be
committed.

## Current scripted result

`python run_eval.py` produces a reproducible offline run. The current scripted
trajectory is 60/60 code-check passes. This validates fixtures, code paths and
grading logic; it is not a claim about live-model accuracy. Live D5 runs will
report the same 60-trial shape per model with measured token usage.

Run `python audit_evaluation_set.py` to regenerate the committed case-mix audit
in `evidence/d4_evaluation_audit.json`.
