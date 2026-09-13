# D1 - Single ReAct agent architecture

## Architecture

This system has one decision-maker and one hand-written control loop:

```text
user task -> Thought -> Action(s) -> Observation(s) -> repeat -> Final
```

`agent.run_case()` owns the loop. It calls one backend for the next move,
executes the requested local tools, appends their observed results to the
transcript, and repeats until the backend returns a final decision or a
code-level guardrail stops the run. No framework owns the loop and no agent
calls another agent.

The user task is explicit: for example, `Process referral REF-5602. Use tools
to gather ground truth before concluding.` This makes the live backend receive
both the operating instructions and the referral identifier.

## Worked trace: REF-5602

| Turn | Thought-driven action(s) | Observation | Why the next action varies |
|---|---|---|---|
| 1 | `get_referral(REF-5602)` | Patient `P-1180`, specialty `OPH`, tests and clinical summary | The referral supplies the identifiers needed for every other check. |
| 2 | `check_referral_criteria(...)` and `lookup_patient(...)` in parallel | No red flag, no missing test, routine band; no future OPH appointment | These reads are independent, so grouping them saves one model turn. |
| 3 | Two independent `get_clinic_slots(...)` window queries in parallel | No early routine slot; `OPH-C2` has a valid routine slot on 2026-10-14 | The derived urgency band and clinical window determine whether a legal slot exists. |
| 4 | `book_slot(...)` after the `confirm` gate | Simulated booking confirmation | This is the only irreversible action; the gate is immediately before it. |
| Final | `book` decision | Records evidence, reason, slot, cost and guardrail events | No further tool action is needed. |

The run has six tool calls but four turns. Parallel tool calls do not create
multiple agents; they are independent actions selected by the same ReAct loop.

## D1 compliance checklist

- One ReAct loop: yes - `agent.py`.
- Thought, action(s), observation(s), repeat, final: yes.
- Several tools and more than one call in a turn: yes.
- Ground truth after every action: yes - each tool reads deterministic fixture data.
- Vendor-neutral live model configuration: yes - `config.py` and `backends.py`.
- Framework-owned loop or multi-agent system: no.
- Irreversible real-world booking: no - `book_slot` is a simulated local result.

## Important limitation

The 40-case scripted backend validates deterministic code paths, not live-model
reasoning quality. Live D2(b) and D5 runs are still required to measure whether
an actual model follows the prompt, chooses correct tools, and uses tokens as
reported.
