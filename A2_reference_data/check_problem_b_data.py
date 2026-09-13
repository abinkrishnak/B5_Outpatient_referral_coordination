#!/usr/bin/env python3
"""Validate the final Problem B-only reference data without changing it."""
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data_B"


def rows(name):
    with (DATA / name).open(encoding="utf-8") as fh:
        return json.load(fh)


def main():
    referrals = rows("referrals.json")
    patients = rows("patients.json")
    slots = rows("clinic_slots.json")
    specialties = rows("specialties.json")
    with (HERE / "expected_outcomes_B.json").open(encoding="utf-8") as fh:
        outcomes = json.load(fh)
    referral_ids = [r["referral_id"] for r in referrals]
    patient_ids = {p["patient_id"] for p in patients}
    outcome_ids = [o["case_id"] for o in outcomes]
    assert len(referral_ids) == 40 and len(set(referral_ids)) == 40
    assert set(referral_ids) == set(outcome_ids)
    assert all(r["patient_id"] in patient_ids for r in referrals)
    assert all(s["capacity_remaining"] >= 0 for s in slots)
    assert all(s["code"] for s in specialties)
    print("Problem B data valid: 40 referrals, %d patients, %d slots, %d outcomes."
          % (len(patients), len(slots), len(outcomes)))


if __name__ == "__main__":
    main()
