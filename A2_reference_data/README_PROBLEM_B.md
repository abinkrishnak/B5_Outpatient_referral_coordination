# Problem B reference data

This folder contains only the data required to reproduce the Outpatient
Referral Coordination submission.

- `data_B/`: supplied Problem B records plus approved team additions.
- `expected_outcomes_B.json`: the 40-case answer key used by the harness.
- `make_fixtures_B.py`: deterministic generator containing supplied rows and
  the team-added `REF-6001` to `REF-6025` blocks.
- `B5_case_manifest.json`: concise case ownership/review manifest.

Run `python check_problem_b_data.py` before editing or submitting. It confirms
that the 40 referral IDs, patients and answer-key IDs join correctly.

Do not modify teacher-supplied rows. Make any team changes only to the added
case range, preserve the 30–50 total-case and 6–10 negative-case constraints,
and rerun `python audit_evaluation_set.py` afterwards.
