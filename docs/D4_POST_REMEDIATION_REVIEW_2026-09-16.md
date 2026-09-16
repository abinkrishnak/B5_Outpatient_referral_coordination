# D4 Post-remediation human judgement review

- Reviewer: **TAN JINGXUAN**
- Review date: **2026-09-16**
- Model: openai/gpt-4.1-mini
- Tool contract: v2
- Evidence: evidence/d5_live_openai_gpt-4.1-mini_v2_post_remediation_2026-09-16.json
- Automated code result: **57/60 trials (95.0%)**
- Human judgement result: **3/10 cases (30.0%)**

## Judgement decision

The 10 sampled decision records were checked against every item in must_record. A case passes only when the final reason explicitly supports every required fact and does not claim an action missing from the tool trace.

Passed cases: REF-5614, REF-5703, REF-5711.

The remaining cases are recorded as not passing the strict evidence check because one or more required facts were implicit or missing from the final reason. The detailed rows are in the CSV evidence file.

## Important label/protocol conflict

REF-5590 is a red-flag case. The protocol says a red flag must stop the run before slot queries. Its expected human-judgement label also asks for evidence that an urgent slot existed and was not taken. Those requirements conflict: proving the slot existed would require a slot lookup after the red-flag stop. We therefore do not change the safe routing behavior merely to satisfy the conflicting label. This is reported as a dataset/label conflict.

## Status

The automated code check is strong at 95%, but the sampled natural-language evidence is not yet submission-ready at 30%. The result should be reported honestly; no claim of 100% human-judgement quality is made.

## Post-remediation pilot evidence (2026-09-16)

A 5-case pilot produces 9 trials because negative cases are repeated three times. It completed with **6/9 trials passed (66.7%)**. The only failures were the three REF-5590 red-flag trials, all asking for the contradictory slot-not-taken evidence. No new failure was observed in the other pilot cases. The complete retained live baseline remains **57/60 (95.0%)**; the interrupted full rerun is not counted.

The pilot therefore supports the safety of the remediation but is not a replacement for a completed full live battery.

## REF-5590 resolution (2026-09-16)

REF-5590 is resolved as a protocol-safe pass with a label-conflict exception. The red flag sudden visual loss requires escalation to the triage nurse and stopping before any slot query. The conflicting slot-not-taken item is retained as a dataset issue, not treated as an agent failure.

## Timeout protection verification (2026-09-16)

The live transport was changed to one bounded 45-second request per model call. The battery now catches a transport timeout, records it as live_timeout, and continues to the next trial instead of hanging the notebook or inventing a clinical decision. A 5-case pilot completed 9 trials: 6/9 passed. The only three failures were the already documented REF-5590 label/protocol conflict; no timeout record and no new case failure appeared.

Pilot evidence: evidence/d5_live_openai_gpt-4.1-mini_v2_timeout_patch_pilot_2026-09-16.json. A completed full post-fix battery is still required before claiming a new 40-case live result.

## Full post-timeout-fix live battery (2026-09-16)

The complete 40-case battery finished after the bounded transport change: 60 trials, 57 passed (95.0%), median 4 turns, worst case 4 turns, zero step-cap hits, and measured cost US$0.1473. The only three failed trials were REF-5590 repeats. They are covered by the recorded label/protocol conflict resolution: the red-flag rule requires stopping before slot lookup, while the supplied must_record item asks for post-stop slot evidence. No timeout failure occurred.

Final live evidence: evidence/d5_live_openai_gpt-4.1-mini_v2_post_timeout_fix_full_2026-09-16.json.

