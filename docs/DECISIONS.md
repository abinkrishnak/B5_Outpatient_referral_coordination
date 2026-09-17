# Project decisions

## D0-01: Red-flag slot-query ambiguity

**Date:** 2026-09-13  
**Status:** documented design decision

The A2 brief's Problem B worked escalation (`REF-5590`) requires the record to
state that an urgent slot existed and was deliberately not taken. The supplied
answer key carries the same requirement. A later explanatory paragraph says
that escalation should have `slots_queried = 0`.

The project treats the supplied answer key as the executable grading contract
for `REF-5590`: the scripted trace queries slots and records that the available
slot was not booked. For other escalation families, it uses early exit unless a
case's answer key explicitly requires slot evidence. This retains safety (no
booking occurs), keeps the run reproducible, and avoids changing supplied data.
