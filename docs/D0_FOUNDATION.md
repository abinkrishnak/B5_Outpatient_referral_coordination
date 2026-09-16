# D0 Foundation

## Placement on the Class 4 ladder

Problem B is rung 7, an agent. It retrieves records through tools, chooses the
next action based on observations, loops until it can conclude, and can cause a
real-world effect through `book_slot`. It is not RAG or agentic RAG because
the system decides which data to retrieve and has a gated write-like action.

## Workflow and ground-truth tests

The workflow contains conditional routing: red flag, specialty mismatch,
missing mandatory test and future appointment are early exits; only a referral
that passes all four can enter slot search and booking. The required facts are
available as structured records at machine speed, so a tool-using loop is
appropriate. Human confirmation remains mandatory at the irreversible booking
step because the referral contains untrusted free text, patient data and an
external appointment effect.

## What good looks like

1. Retrieve the referral before applying routing policy.
2. Stop on the first safety or completeness failure.
3. Search only slots in the correct urgency band and legal window.
4. Book exactly one eligible slot only after confirmation.
5. Record the decision, trigger, evidence, turns, tokens and cost.

This framing follows Class 4's ladder, machine-speed ground-truth test and
pre-code workflow test. The automation boundary is the confirmation gate, not
the reasoning loop.
