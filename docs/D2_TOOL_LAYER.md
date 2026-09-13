# D2 - Tool layer

## D2(a): final Problem B tool set

The agent sees five tools. `as_of()` remains ordinary code used to insert the
evaluation clock into the system prompt; it is not an agent-callable tool.

| Tool | Why the task fails without it | Why it is not confusable | Cost and design decision |
|---|---|---|---|
| `get_referral` | No other tool resolves the initial referral ID into specialty, patient, tests and clinical summary. | It is the only entry-point lookup. | Must run first and alone; all later calls depend on its IDs. |
| `check_referral_criteria` | Cannot identify red flags, specialty mismatch, missing tests, urgency band or legal window. | It applies the specialty protocol; it is not a patient or slot lookup. | Deliberately bundles protocol facts which are always required together, avoiding three extra turns. |
| `lookup_patient` | Cannot detect a future same-specialty appointment. | It is the only appointment-history lookup. | Returns only appointment evidence. Contact and date-of-birth data were removed because neither changes a routing outcome. |
| `get_clinic_slots` | A complete referral cannot be booked without a real, free slot in its clinical window and urgency band. | It is the only availability source. | Called only after all early-exit checks pass. A band is mandatory, preventing date-only booking. |
| `book_slot` | The assignment requires a simulated gated action on a valid booking path. | It is the sole write-like action. | Called last, once, and only through the autonomy gate. |

## D2(b): V1 to V2 contract experiment

Target tool: `get_clinic_slots`.

| Version | Arguments / behaviour | Safety consequence |
|---|---|---|
| V1 | `specialty: str`, `band: str`; an unknown value returns `[]`. | A typo such as `OPHT` is indistinguishable from genuinely having no slot, inviting a false escalation. |
| V2 | `specialty: Literal["OPH", "CARD", "ORT", "DER", "ENT", "NEU"]`; `band: Literal["urgent", "soon", "routine"]`; runtime validation returns a structured `invalid_slot_query` observation. | A typo cannot masquerade as no availability. The agent receives the allowed values and can correct it. |

The active contract is V2 (`TOOL_CONTRACT_VERSION = "v2"`). In an offline
contract check, V1 returned `[]` for specialty `OPHT`; V2 returned
`invalid_slot_query` with the permitted specialty and band values. The 40-case
scripted evaluation remains 60/60 code-check passes under V2.

Prompt-size audit after minimising `lookup_patient`:

| Version | System prompt characters | Approximate tokens (characters / 4) |
|---|---:|---:|
| V1 | 5,189 | 1,297 |
| V2 | 5,080 | 1,270 |

This is only a prompt-size estimate. It is not measured model usage.

### Required live experiment - not yet claimed as complete

Use one inexpensive fixed model for both versions. Keep the same 40 cases,
60 trials, temperature, autonomy setting, and evaluation date. Change only
`TOOL_CONTRACT_VERSION`; record pass rate, negative-case pass rate, invalid
slot-query attempts, input/output token usage, and cost. The scripted backend
cannot demonstrate that a live model obeys either descriptor.

## D2(c): dependency rule

Calls may share a turn only when neither needs the other’s output.

- `get_referral` is alone because it supplies the identifiers.
- `check_referral_criteria` and `lookup_patient` can run together.
- Slot queries may be grouped only after criteria supplies the urgency band and
  window.
- `book_slot` is always alone and last.

`REF-5602` demonstrates the intended grouped shape: six tool calls in four
turns. The final D2(c) report table must compare that run with the same calls
executed one-per-turn, then show that the decision and code check are unchanged.
