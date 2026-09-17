# D4 Report Evidence Table

| Evaluation design | Result | What it demonstrates |
|---|---:|---|
| Unique referral cases | 40 | Coverage includes routine, soon and urgent bookings; missing tests; red flags; duplicate appointments; no-slot cases; prompt injection; and boundary-day cases. |
| Scheduled trials per model | 60 | Thirty ordinary cases run once and ten negative/safety cases run three times to check consistent safe behaviour. |
| Scripted regression result | 60/60 | The deterministic reference policy passed every machine-checkable trial after the current remediation. |
| Median turns | 3.5 | The agent normally reaches an outcome in a short ReAct trace. |
| Worst-case turns | 4 | The step cap was not reached in the scripted regression run. |
| D2 parallel comparison | 6 to 4 turns | Independent checks reduced estimated input tokens from 42,000 to 24,000 for REF-5602, a 42.9% reduction. |
| D2 V1 versus V2 | 49/60 vs 48/60 on Gemini Flash-Lite | V2 reduced input tokens by 7.4% and cost by 5.6%; it is retained because constrained arguments prevent silent invalid clinic/specialty inputs. |
| D3 guardrail checklist | 12/12 passed | The implementation blocks unsafe or malformed actions, applies the autonomy gate before booking, and handles hostile free text safely. |
| Human rationale review | 10/10 records contain the label-required facts; 9/10 early-exit compliant | Wang Hanfei's review found all required explanation facts in the supplied records. REF-5590 is separately reported because it made an avoidable post-red-flag slot lookup to obtain label-required evidence. |

## Caption for the report

**Table X. Evaluation evidence for the outpatient referral agent.** Automated checks establish whether decisions, required tools and booked slots are correct. Human review separately checks whether the final explanation makes the safety and routing rationale understandable. REF-5590 is reported separately because it meets the label's evidence requirement only by making an avoidable post-red-flag slot lookup.
