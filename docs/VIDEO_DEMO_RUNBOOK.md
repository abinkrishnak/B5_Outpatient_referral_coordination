# Five Minute Video Demonstration Runbook

## Purpose

Show a marker one coherent argument: Problem B needs a single ReAct loop because the required checks depend on what the referral reveals; the tool and guardrail layers make that loop safe; the evaluation and cost model show what the team would deploy and what it would not.

## Timing and speakers

| Time | Speaker | Screen or slide | What to say |
|---|---|---|---|
| 0:00-0:35 | Zhao Xiaonan | Title and one referral journey | Introduce outpatient referral coordination. Booking is the irreversible action, so the system must inspect referral facts before acting. State that the design is a single ReAct agent, not a multi-agent system. |
| 0:35-1:15 | Ge Jiayao | ReAct loop and five tools | Explain the loop: retrieve referral, check criteria, look up patient, search slots, then book only after approval. State why a fixed workflow cannot predict the number of slot searches. |
| 1:15-1:55 | Tan Jinxuan | V1 versus V2 and guardrail visual | Show the V1 typo risk and the V2 constrained descriptor. State the 42.9% token reduction from parallel independent checks and the 12/12 guardrail result. |
| 1:55-2:35 | Wang Hanfei | Evaluation coverage chart | Explain the 40 referrals and 60 trials: ordinary cases run once; negative cases run three times. Show prompt injection, missing-test and boundary-day coverage. Mention that explanation review is separate from code checks. |
| 2:35-3:30 | Kaivelikkal Abin Krishna | Live scripted negative-case run: REF-5703 | Run the scripted case live. Point out the hostile instruction, the real criteria check, escalation to a triage nurse and the absence of `book_slot`. Do not use REF-5590 for the live demo because it distracts from the clearer injection demonstration. |
| 3:30-4:10 | Liu Siwen | Cost table | State the three layers: tokens, expected nurse fallback and monthly scale. Explain why fallback dominates. Recommend DeepSeek Chat V3 within the final five: 85.0% and $5,508.49 per month at 4,000 referrals. |
| 4:10-5:00 | Wang Hanfei | Limitations and closing slide | State the REF-5590 early-exit tension, the 9/10 early-exit review result and what the team would not deploy: autonomous live booking without human confirmation. Close with the evidence-backed recommendation. |

## Slides and visuals

Use six slides plus the terminal demonstration. Keep the visual style clinical and simple: white background, navy headings, one teal accent, large numbers, and no dense code screenshots.

1. **Outpatient referral coordination** - one referral enters, one safe decision leaves.
2. **Single ReAct loop** - show read tools feeding the loop and `book_slot` behind the confirmation gate.
3. **Tool design and safety** - V1 typo compared with V2 constraint; 12/12 guardrails; 42.9% token reduction.
4. **Evaluation evidence** - 40 referrals, 60 trials, negative-case families and the five-model comparison.
5. **Cost to serve** - DeepSeek compared with Mistral, showing why the fallback layer outweighs raw token price.
6. **Deployment boundary** - recommended configuration, confirmation gate, REF-5590 limitation and what remains human-owned.

## Recording checklist

- Keep the total duration at or below five minutes.
- Every member speaks audibly on camera or voice-over.
- Demonstrate a real scripted run using `python run_eval.py` or a focused scripted negative case.
- Show the final numbers only once and keep them consistent with D5 and D6.
- Do not show API keys, patient data outside the provided fictional fixtures, terminal paths or failed provider-error logs.
- Put the final shareable recording URL in `VIDEO_LINK.txt` inside the submission archive.
