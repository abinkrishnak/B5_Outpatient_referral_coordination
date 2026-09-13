#!/usr/bin/env python3
"""D4 audit: report case mix and verify the answer key is usable."""
from collections import Counter
import json

from harness import load_cases, load_key, _is_negative


def main():
    case_ids = load_cases()
    key = load_key()
    missing_labels = sorted(set(case_ids) - set(key))
    extra_labels = sorted(set(key) - set(case_ids))
    negative = [case_id for case_id in case_ids if _is_negative(key.get(case_id))]
    families = Counter(key[case_id].get("family", "unlabelled") for case_id in case_ids)
    report = {
        "cases": len(case_ids),
        "negative_cases": len(negative),
        "ordinary_cases": len(case_ids) - len(negative),
        "trials_per_model": len(case_ids) + 2 * len(negative),
        "missing_labels": missing_labels,
        "extra_labels": extra_labels,
        "outcomes": dict(Counter(key[case_id]["expected_decision"] for case_id in case_ids)),
        "families": dict(sorted(families.items())),
    }
    assert not missing_labels and not extra_labels, report
    assert 30 <= report["cases"] <= 50, report
    assert 6 <= report["negative_cases"] <= 10, report
    with open("evidence/d4_evaluation_audit.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
