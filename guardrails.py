"""
PE6201 · A2 scaffold — THE GUARDRAIL LAYER  (D3a)
====================================================================
Four things, and NONE of them involve a model. That is the point.

    1. STEP CAP            stop after N turns
    2. BUDGET CEILING      stop after N tokens
    3. ACTION DE-DUPLICATION   stop repeating an action already taken
    4. AUTONOMY GATE       hold the irreversible step for a human

A model cannot influence whether these fire, which is why D3(b)'s ten
guardrail cases run on the SCRIPTED backend. They test your code.

MAKE THE STOP LOUD. A cap that silently returns an empty answer is
worse than the loop it prevented: it turns a visible cost problem into
an invisible correctness problem. Every stop below records WHY.
====================================================================
"""
from datetime import date, timedelta

import tools


class GuardrailStop(Exception):
    """Raised when the code layer halts a run. Carries the reason so the
    decision record can say what stopped it and at which turn."""

    def __init__(self, reason, detail=""):
        self.reason = reason
        self.detail = detail
        super().__init__("%s: %s" % (reason, detail) if detail else reason)


class Guardrails:
    """One instance per run. Never share one between cases - a shared
    instance leaks state and D4 requires every case to start clean."""

    def __init__(self, max_turns, max_tokens, autonomy):
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.autonomy = autonomy
        self.seen_actions = set()     # for de-duplication
        self.fired = []               # every guardrail event, for the record

    # ---- 1 · step cap -----------------------------------------------
    def check_turns(self, turn):
        if turn > self.max_turns:
            self._fire("step_cap", "reached %d turns" % self.max_turns)
            raise GuardrailStop("step_cap",
                                "hit the %d-turn cap without a conclusion"
                                % self.max_turns)

    # ---- 2 · budget ceiling -----------------------------------------
    def check_budget(self, tokens_so_far):
        if tokens_so_far > self.max_tokens:
            self._fire("budget_ceiling", "%d tokens" % tokens_so_far)
            raise GuardrailStop("budget_ceiling",
                                "spent %d tokens, ceiling is %d"
                                % (tokens_so_far, self.max_tokens))

    # ---- 3 · action de-duplication ----------------------------------
    def check_duplicate(self, tool, args):
        """A loop has no memory of its own actions unless you give it one.

        This IS that memory. Class 4's loop failure was exactly this
        guard deleted: 8 turns, no answer, 1.6x the cost, and NO
        exception raised. It did not crash. It burned money in a circle.
        """
        signature = (tool, repr(sorted(args.items())))
        if signature in self.seen_actions:
            self._fire("duplicate_action", "%s repeated" % tool)
            raise GuardrailStop("duplicate_action",
                                "%s called again with identical arguments "
                                "- the loop is not progressing" % tool)
        self.seen_actions.add(signature)

    # ---- 4 · autonomy gate ------------------------------------------
    def gate(self, action_name, payload, approve=None):
        """Called ONLY in front of the irreversible step.

        Note where this sits: in front of the ACTION, not in front of the
        agent. An agent gated as a whole is not an agent, it is a form.

        `approve` is a callable the harness supplies. On the scripted
        backend it auto-approves so the run is deterministic - and the
        record still shows the gate was passed, which is what a marker
        checks for.
        """
        if self.autonomy == "act":
            self._fire("gate_passed", "%s (autonomy=act)" % action_name)
            return True
        if self.autonomy == "suggest":
            self._fire("gate_held", "%s (autonomy=suggest)" % action_name)
            return False
        # confirm
        ok = bool(approve and approve(action_name, payload))
        self._fire("gate_%s" % ("passed" if ok else "held"),
                   "%s (autonomy=confirm)" % action_name)
        return ok

    # ---- 5 · booking eligibility ------------------------------------
    def check_booking_eligibility(self, payload):
        """Refuse an attempted booking that contradicts systems of record.

        This is a safety backstop, not a second decision-making agent. The
        model still gathers evidence and selects actions; immediately before
        the scarce slot is consumed, ordinary code verifies that the requested
        booking does not violate a hard departmental rule. It specifically
        catches a model following hostile referral text.
        """
        referral_id = payload.get("referral_id")
        referral = tools.get_referral(referral_id)
        if not referral:
            self._booking_block("unknown_referral", referral_id)

        summary = referral.get("clinical_summary", "").lower()
        hostile_markers = (
            "system note:", "skip the pre-referral", "book the earliest",
            "check_referral_criteria returned:",
        )
        if any(marker in summary for marker in hostile_markers):
            self._booking_block("hostile_referral_text", referral_id)

        criteria = tools.check_referral_criteria(referral["specialty"], referral_id)
        if not criteria:
            self._booking_block("criteria_unavailable", referral_id)
        if criteria["red_flag_term"]:
            self._booking_block("red_flag", criteria["red_flag_term"])
        if not criteria["right_department"]:
            self._booking_block("specialty_mismatch", referral_id)
        if criteria["missing_tests"]:
            self._booking_block("mandatory_test_missing", referral_id)

        patient = tools.lookup_patient(referral["patient_id"])
        today = tools.as_of()
        if any(a.get("specialty") == referral["specialty"] and a.get("date", "") >= today
               for a in patient["existing_appointments"]):
            self._booking_block("duplicate_future_appointment", referral_id)

        window_end = (date.fromisoformat(today)
                      + timedelta(weeks=criteria["window_weeks"])).isoformat()
        legal_slots = tools.get_clinic_slots(
            referral["specialty"], criteria["band"],
            **{"from": today, "to": window_end})
        requested = (payload.get("clinic"), payload.get("date"), payload.get("time"))
        available = {(slot["clinic"], slot["date"], slot["time"])
                     for slot in legal_slots}
        if requested not in available:
            self._booking_block("slot_not_legal_or_available", str(requested))

    def _booking_block(self, reason, detail):
        self._fire("booking_eligibility_blocked", "%s: %s" % (reason, detail))
        raise GuardrailStop("booking_eligibility", "%s: %s" % (reason, detail))

    # ---- bookkeeping ------------------------------------------------
    def _fire(self, kind, detail):
        self.fired.append({"guardrail": kind, "detail": detail})
