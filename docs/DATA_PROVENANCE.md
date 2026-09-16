# Data Provenance

`A2_reference_data/` contains the supplied Problem B fixture structure. The
team extended it with referral identifiers `REF-6001` to `REF-6025` and their
corresponding patient, appointment and slot records. The supplied rows remain
available and the complete set is checked for joins and answer-key coverage.

Run `python A2_reference_data/check_problem_b_data.py` to validate the dataset.
Run `python audit_evaluation_set.py` to validate the 40-case / 60-trial mix.

The agent receives only the data required for routing. In particular,
`lookup_patient` exposes appointment evidence but not contact details. This
reduces privacy surface and observation-token cost without changing a routing
outcome.
