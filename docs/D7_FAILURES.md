# D7 - Controlled failure demonstrations

Both demonstrations are deletions from the working system and run offline.
They are not imagined bad examples.

## Failure 1: repeated-action ghost loop

Run `python demo_loop_failure.py`. On `REF-5602`, remove only
`Guardrails.check_duplicate` and replay a script that repeats independent
checks. The decision remains `book`, but turns rise from 4 to 6, tool calls
from 6 to 10, tokens from 24,600 to 42,840 and estimated scripted cost from
US$0.00264 to US$0.00454. Neither the eight-turn cap nor the 60,000-token
ceiling fires. Therefore a pass-rate table alone misses the fault; per-run
turn, token and cost instrumentation detects it. The correct repair is code
layer action de-duplication, because prompt advice cannot reliably make a
model remember an earlier action.

## Failure 2: silent typo becomes false “no slots”

Run `python demo_tool_contract_failure.py`. Remove only V2's closed-set
validation and query `specialty="OPHT"`. Loose V1 returns `[]`, which is
indistinguishable to an agent from a true no-slot-in-window result. Restored
V2 returns structured `invalid_slot_query` evidence naming the invalid value
and allowed specialties. The correct repair is the tool interface: a prompt
can be ignored and a later guardrail sees the ambiguous empty result too late.

The accompanying JSON evidence proves that restoration rejects the typo.
