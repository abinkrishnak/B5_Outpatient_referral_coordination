"""
PE6201 · A2 scaffold — THE AGENT LOOP  (D1)
====================================================================
    thought -> action -> observation -> repeat -> final

That is the whole of ReAct, and it is hand-rolled here on purpose. No
framework owns your loop: when it misbehaves you need to be able to
read the twelve lines that did it.

WHAT MAKES THIS AN AGENT RATHER THAN A WORKFLOW: the number of steps is
decided by the DATA, not by you. A one-line claim with a live policy is
a short run. A four-line claim with a pre-authorisation to chase is a
long one. You did not write that branch - the record did.

--------------------------------------------------------------------
INSTRUMENTATION IS NOT OPTIONAL

Every run records turns, tokens, cost, every tool call and every
guardrail event. D6's cost model and D7's loop failure both need
numbers that were captured WHILE THE RUN HAPPENED. A team that adds
instrumentation afterwards has to run the whole battery again.

You cannot report a failure you had no way of noticing.
====================================================================
"""
import time
import re

import config
import prompt
import tools
from backends import make_backend
from guardrails import Guardrails, GuardrailStop


def run_case(case_id, problem=None, approve=None, verbose=False):
    """Run ONE case from a clean state and return the decision record.

    ISOLATION (D4): everything this function needs is created inside it.
    No case may depend on a previous one having run - so no module-level
    counters, no shared guardrail object, no leftover transcript.
    """
    problem = problem or config.PROBLEM
    started = time.time()

    guards = Guardrails(config.MAX_TURNS, config.MAX_TOKENS_PER_RUN,
                        config.AUTONOMY)
    # WHAT THE MODEL IS TOLD. On the scripted backend these are ignored -
    # the moves are pre-written, so no prompt is ever sent. On the live
    # backend this IS the experiment D2(b) measures: the descriptors and
    # the routing rules, assembled by prompt.build_system_prompt().
    #     python3 run_eval.py --prompt      to see the exact text
    backend = make_backend(
        case_id,
        tool_descriptors=[tools.descriptors()[n] for n in tools.REGISTRY[problem]
                          if n in tools.descriptors()],
        system_prompt=prompt.build_system_prompt(problem))

    # The live model needs an explicit task, not only its operating manual.
    # ScriptedBackend already knows case_id because it replays a fixture, which
    # could otherwise hide this gap until an expensive live evaluation.
    item_name = "referral" if problem == "B" else "claim"
    transcript = [{"role": "user",
                   "content": "Process %s %s. Use tools to gather "
                              "ground truth before concluding."
                              % (item_name, case_id)}]
    evidence = []        # every tool actually called, in order

    # TURNS ARE TOOL-CALLING TURNS. The concluding move - where the agent
    # writes its decision record - is bookkeeping, not a turn. This is the
    # same convention Appendix A uses: CLM-8842 is "turns": 4 with EIGHT
    # tool calls, because the gated action is a turn like any other and
    # the write-up afterwards is not. Count them any other way and your
    # D2(c) arithmetic stops agreeing with the brief.
    turns = 0
    iterations = 0       # loop-safety only; never reported
    tokens_in = tokens_out = 0
    stopped_by = None

    # Scripted fixtures auto-approve so the free reproducibility check can
    # exercise the booking path. A LIVE run defaults to *no approval*: the
    # caller must explicitly supply an approval function (the D5 synthetic
    # battery does so only against these local fixtures).
    if approve is None:
        approve = (lambda action, payload: True) if backend.name == "scripted" \
            else (lambda action, payload: False)

    try:
        while True:
            iterations += 1
            if iterations > config.MAX_TURNS + 2:
                raise GuardrailStop("step_cap", "loop did not terminate")

            move = backend.next_move(transcript)
            ti, to = backend.token_estimate(transcript)
            tokens_in, tokens_out = tokens_in + ti, tokens_out + to
            guards.check_budget(tokens_in + tokens_out)

            if verbose:
                label = ("conclude" if "final" in move else "turn %d" % (turns + 1))
                print("  %-9s · %s" % (label, move.get("thought", "")[:88]))

            # ---- conclude -------------------------------------------
            if "final" in move:
                record = dict(move["final"])
                contract_error = _final_contract_error(record, evidence)
                if contract_error:
                    # Do not manufacture an action in Python.  Tell the same
                    # ReAct model precisely which output invariant it broke,
                    # then let it take its own next action from the existing
                    # observations.  This is a schema/sequence check, not a
                    # case-answer lookup or a second agent.
                    transcript.append({"role": "assistant",
                                       "content": move.get("thought", "")})
                    transcript.append({"role": "user",
                                       "content": "OUTPUT CONTRACT ERROR: %s "
                                                  "Return the next valid JSON move; "
                                                  "do not repeat prior tool calls."
                                                  % contract_error})
                    continue
                break

            # ---- act: one turn may carry SEVERAL calls ---------------
            turns += 1
            guards.check_turns(turns)

            # Only calls INDEPENDENT of each other belong in one turn.
            # A dependency chain cannot be shortened by running things at
            # once - that is why Problem B saves less than Problem A.
            # Different providers occasionally return ``{"calls": []}`` or
            # omit both action keys despite JSON mode.  Do not let a model
            # formatting lapse crash the Python process (or silently count as
            # a clinical decision).  Give the same ReAct model one explicit
            # protocol-repair turn instead.  A non-empty legacy single-tool
            # shape remains supported for compatibility with the scaffold.
            calls = move.get("calls")
            if calls is None and "tool" in move and "args" in move:
                calls = [(move["tool"], move["args"])]
            move_error = _calls_contract_error(calls)
            if move_error:
                transcript.append({"role": "assistant",
                                   "content": move.get("thought", "")})
                transcript.append({"role": "user",
                                   "content": "ACTION CONTRACT ERROR: %s "
                                              "Return one valid JSON move. "
                                              "Use final only to conclude, "
                                              "or calls with at least one "
                                              "[tool_name, args] pair."
                                              % move_error})
                continue
            observations = []

            for name, args in calls:
                guards.check_duplicate(name, args)

                # THE GATE goes in front of the irreversible step only.
                if name == tools.GATED_ACTION.get(problem):
                    if problem == "B":
                        guards.check_booking_eligibility(args)
                    if not guards.gate(name, args, approve):
                        raise GuardrailStop(
                            "gate_held",
                            "%s awaits human approval (autonomy=%s)"
                            % (name, config.AUTONOMY))

                result = tools.call(problem, name, args)
                evidence.append(name)
                observations.append({"tool": name, "args": args,
                                     "observation": result})
                if verbose:
                    print("       %-26s -> %s" % (name, _short(result)))

            transcript.append({"role": "assistant",
                               "content": move.get("thought", "")})
            transcript.append({"role": "user",
                               "content": repr(observations)})

    except GuardrailStop as stop:
        # A LOUD STOP. The record says what halted the run and where, so
        # this never looks like a quiet wrong answer.
        stopped_by = stop.reason
        record = {"decision": "escalate",
                  "reason": "halted by the %s guardrail - %s"
                            % (stop.reason, stop.detail)}

    provider_cost = (backend.measured_cost() if hasattr(backend, "measured_cost")
                     else None)
    cost = (provider_cost if provider_cost is not None else
            (tokens_in / 1e6) * config.PRICE_IN +
            (tokens_out / 1e6) * config.PRICE_OUT)

    record.update({
        "case_id": case_id,
        "evidence": evidence,
        "turns": turns,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": round(cost, 6),
        "cost_basis": ("provider_reported" if provider_cost is not None
                       else "configured_token_prices"),
        "seconds": round(time.time() - started, 3),
        "guardrails_fired": guards.fired,
        "stopped_by": stopped_by,
        "backend": backend.name,
    })
    return record


def _short(value, n=64):
    s = repr(value)
    return s if len(s) <= n else s[:n - 1] + "…"


def _final_contract_error(record, evidence):
    """Return an output-contract error without looking at the answer key.

    These are format and action-sequence invariants that apply to every
    Problem B referral. They deliberately do not decide whether a specific
    patient should be booked.
    """
    if record.get("decision") == "book" and "book_slot" not in evidence:
        return "a book decision requires an earlier book_slot action"
    if record.get("decision") == "request_information":
        missing = str(record.get("missing", ""))
        if not re.search(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)+\b", missing):
            return "missing must name the mandatory test and its code, e.g. VF-01"
    return None


def _calls_contract_error(calls):
    """Return a structural error for a non-final model move, else ``None``.

    This validates the wire format only.  It does not decide the referral
    outcome or invent a tool call, so the ReAct model remains responsible for
    choosing the next action.
    """
    if not isinstance(calls, list) or not calls:
        return "calls must be a non-empty JSON list"
    for call in calls:
        if (not isinstance(call, (list, tuple)) or len(call) != 2 or
                not isinstance(call[0], str) or not isinstance(call[1], dict)):
            return "each call must be [tool_name, args_object]"
    return None
