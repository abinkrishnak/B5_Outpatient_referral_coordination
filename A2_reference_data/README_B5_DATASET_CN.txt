B5 Problem B — D4 Evaluation Dataset Draft

What is included
- 40 evaluation cases total
- 15 teacher-shipped cases (unchanged)
- 25 added draft cases (REF-6001 to REF-6025)
- 10 negative cases total (the teacher-shipped set already contains 10 negatives)
- expected_outcomes_B.json contains 40 labels / answer keys
- make_fixtures_B.py contains additions only in the EXTRA_* blocks
- data_B/ has been regenerated from the generator
- check_problem_b_data.py result: “Problem B data valid.”

Important assignment rule
Every team member must write evaluation cases. Therefore, treat REF-6001–REF-6025 as a READY DRAFT / template for the team to review, edit by replacing team-added rows if needed, and explicitly allocate/own cases. Do not claim one person authored everyone’s required 5–8 cases.

Do not change teacher-shipped rows. Add/replace only team-added rows with new IDs.

Added-case design
REF-6001–6004: ordinary routine bookings across four shipped specialties
REF-6005: a positive clock case proving the booking window starts from as_of, not date_received
REF-6006–6010: soon-band bookings across the five shipped specialties
REF-6011–6015: urgent bookings (including a DER urgent slot added in EXTRA_CLINIC_SLOTS)
REF-6016–6018: boundary bookings on the last legal day, using a new allowed specialty NEU
REF-6019–6023: past same-specialty appointments that must NOT be treated as duplicates
REF-6024: a positive hostile-text false-positive control using normal clinical wording
REF-6025: a longer ordinary booking with two mandatory tests

Why no extra negative cases?
The 15 shipped cases already contain 10 negative cases (REQUEST INFORMATION or ESCALATE). The assignment guide asks for 6–10 negatives in a 30–50 case evaluation set, so the 25 additions are positive BOOK cases to keep the total at 10.
