# D7 - Controlled failure demonstrations

Both failures are created by deleting exactly one component from the working system and then restoring it. They run offline and produce machine-readable evidence; they are not imagined bad examples.

## Failure 1: repeated-action ghost loop

Run:

```bash
python demo_loop_failure.py
```

On `REF-5602`, the experiment removes only `Guardrails.check_duplicate` and replays a script that repeats independent slot checks.

| Measure | Working | Component removed | Restored |
|---|---:|---:|---:|
| Decision | book | book | book |
| Turns | 4 | 6 | 4 |
| Tool calls | 6 | 10 | 6 |
| Total tokens | 24,600 | 42,840 | 24,600 |
| Estimated scripted cost | US$0.00264 | US$0.00454 | US$0.00264 |

The decision accuracy remains unchanged, so a pass-rate table alone misses the failure. Turns, tool calls, tokens and cost expose it. Neither the eight-turn cap nor the 60,000-token ceiling fires: those controls bound damage but do not diagnose repetition.

The correct repair is **code-layer action de-duplication**. Prompt advice cannot reliably make the model remember every earlier action, while a deterministic signature set can reject an identical call immediately. Restoration must return the run to the working measurements without reducing pass rate.

## Failure 2: invalid specialty typo becomes a false no-slot result

Run:

```bash
python demo_tool_contract_failure.py
```

The controlled action is identical in all three phases:

```python
get_clinic_slots(
    specialty="OPHT",
    band="routine",
    **{"from": "2026-09-09", "to": "2026-11-04"}
)
```

The script performs the required sequence:

1. **Working baseline — V2:** closed-set validation returns `invalid_slot_query`.
2. **Component removed — V1 contract:** the same typo returns `[]`. The routing loop assigns `no_slot_in_window`, which is the wrong business meaning.
3. **Restored — V2:** `invalid_slot_query` is visible again and the safe behavior returns.

Each phase records the attempted action, observation, decision, trigger, reason, turns, tool calls, estimated tokens and a transparent offline cost estimate. The evidence also records `failure_reproduced` and `restoration_verified`. Generated evidence is written to:

- `evidence/d7_tool_contract_failure.json`

The correct repair is the **tool interface**. The specialty and urgency band have finite known vocabularies, so the interface should reject illegal values before an empty list acquires the business meaning “no availability.” A prompt can ask for exact copying but cannot make an illegal string impossible. A post-query guardrail is too late because V1's `[]` is already indistinguishable from a legitimate empty window.

## Reproduction acceptance criteria

Both failures are complete only when all of the following hold:

- the working baseline passes;
- deleting one named component reproduces the measured failure;
- the failure is visible in recorded evidence, not only in prose;
- restoring the component recovers the safe behavior;
- the correct repair layer is justified against the alternatives;
- generated JSON/CSV evidence is refreshed after the final code change.
