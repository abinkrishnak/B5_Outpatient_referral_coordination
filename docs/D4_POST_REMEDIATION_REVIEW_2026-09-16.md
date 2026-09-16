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


## Additional evidence-contract remediation (2026-09-16)

The V2 prompt was strengthened after the 3/10 strict judgement review. The final-answer instructions now require the agent to compare its reason with every case `must_record` item and copy each applicable fact explicitly, including exact dates, codes, patient ids, destinations, window boundaries, and relative week counts. It also requires the agent to report a label/protocol conflict instead of performing a forbidden post-red-flag slot lookup.

This is a prompt-layer remediation, not a new evaluation result. The retained live baseline remains 57/60 automated trials (95.0%) and 3/10 strict natural-language judgement cases (30.0%). A fresh full live battery is required before claiming that the judgement rate improved.
