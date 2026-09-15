"""
PE6201 · A2 scaffold — THE TWO BACKENDS
====================================================================
A backend answers ONE question: given the conversation so far, what
does the agent do next?

It returns either
    {"tool": "name", "args": {...}, "thought": "..."}      -> call a tool
    {"final": {...}, "thought": "..."}                     -> conclude

EXACTLY ONE FUNCTION IN THIS WHOLE REPOSITORY KNOWS A VENDOR EXISTS.
It is `_live_call` at the bottom. That is the D5 requirement, and it is
what makes swapping models a one-string change.

--------------------------------------------------------------------
WHY THE SCRIPTED BACKEND IS NOT A TOY

It replays a fixed sequence of decisions for a known case. That makes
your whole run deterministic, free, and reproducible by a stranger -
which is what D5(a) is marked on, and what makes D3(b) and D7 cost
nothing.

It is also the honest way to test your CODE. A guardrail either fires
or it does not; a model has no say in that. Scripting the model's
moves is how you test the parts you wrote.
====================================================================
"""
import json
import socket
import time
import urllib.error
import urllib.request
from getpass import getpass

import config


# =====================================================================
# SCRIPTED
# =====================================================================
# One entry per case you have scripted. The value is the list of moves
# the "model" makes, in order.
#
# ADD YOUR OWN CASES HERE. To script a case: work out what a correct
# agent would do, step by step, and write the steps down. If you cannot
# write them down, you do not yet understand the case - which is
# useful to discover now rather than at 2am on the 13th.
SCRIPTS = {

    # ---------------------------------------------------------------
    # PROBLEM B · REF-5602 - the booking from Appendix A.
    # Six tool calls. Turns 2 and 3 each fire two calls at once, so the
    # run is FOUR turns rather than six. See D2(c) in the brief.
    # ---------------------------------------------------------------
    "REF-5602": [
        {"thought": "I have a referral id and nothing else. Fetch the record.",
         "calls": [("get_referral", {"referral_id": "REF-5602"})]},

        {"thought": "Two things I need next do not depend on each other: "
                    "the specialty's rules, and whether this patient already "
                    "has an appointment. Fire both together.",
         "calls": [("check_referral_criteria", {"specialty": "OPH",
                                                "referral_id": "REF-5602"}),
                   ("lookup_patient", {"patient_id": "P-1180"})]},

        {"thought": "No red flag, right department, VF-01 attached, no "
                    "duplicate. Band is routine, so the window runs 8 weeks "
                    "from as_of 2026-09-09, to 2026-11-04. I will query both "
                    "halves of that window at once. This is a gamble: if the "
                    "near half had a slot, the second query was wasted.",
         "calls": [("get_clinic_slots", {"specialty": "OPH", "band": "routine",
                                         "from": "2026-09-09", "to": "2026-09-30"}),
                   ("get_clinic_slots", {"specialty": "OPH", "band": "routine",
                                         "from": "2026-10-01", "to": "2026-11-04"})]},

        {"thought": "OPH-C2 is full until 14 October. First bookable slot "
                    "inside the window is 2026-10-14 11:20. Book it - this is "
                    "the irreversible step, so it goes through the gate.",
         "calls": [("book_slot", {"clinic": "OPH-C2", "date": "2026-10-14",
                                  "time": "11:20", "referral_id": "REF-5602"})]},

        {"final": {
            "decision": "book",
            "booked": {"clinic": "OPH-C2", "date": "2026-10-14", "time": "11:20"},
            "reason": "Urgency band routine, so an 8-week window from as_of "
                      "2026-09-09 closing 2026-11-04; booked at 5 weeks. "
                      "VF-01 present. No existing OPH appointment for P-1180. "
                      "OPH-C2 was full until 2026-10-14.",
         },
         "thought": "Record the band, the window, the tests and the duplicate "
                    "check - the answer key asks for all four."},
    ],

    # ---------------------------------------------------------------
    # PROBLEM A · CLM-8842 - the partly payable claim from Appendix A.
    # Three lines, one of them excluded, one needing a pre-authorisation.
    # ---------------------------------------------------------------
    "CLM-8842": [
        {"thought": "Turn 1 must run alone: everything else needs the member, "
                    "the hospital and the LINE ITEMS this returns.",
         "calls": [("get_claim", {"claim_id": "CLM-8842"})]},

        {"thought": "Now five calls that depend on nothing but that record. "
                    "The policy, the hospital, and one coverage check PER LINE "
                    "- three lines, three checks. All independent, so one turn.",
         "calls": [("lookup_policy", {"member_id": "M-2214"}),
                   ("check_coverage", {"code": "47120", "policy_id": "POL-3310"}),
                   ("check_coverage", {"code": "31255", "policy_id": "POL-3310"}),
                   ("check_coverage", {"code": "62480", "policy_id": "POL-3310"}),
                   ("lookup_hospital", {"hospital_id": "H-114"})]},

        {"thought": "This one CANNOT join the turn above: I did not know which "
                    "line needed a pre-authorisation until coverage answered. "
                    "That is the dependency rule. Only 62480 needs one.",
         "calls": [("get_preauthorisation", {"member_id": "M-2214",
                                             "procedure_code": "62480",
                                             "date_of_service": "2026-09-02"})]},

        {"thought": "A disposition for every line, then send. This is the "
                    "irreversible step, so it goes through the gate - and it "
                    "is a turn like any other.",
         "calls": [("issue_decision_letter", {
             "claim_id": "CLM-8842",
             "decision": "approve_in_principle",
             "lines_resolved": 3,
             "approved_total": 2180,
             "refused_total": 300})]},

        {"final": {
            "decision": "approve_in_principle",
            "reason": "3 lines. 47120 covered (1400). 62480 covered, PA-5521 "
                      "cited, valid on 2026-09-02 (780). 31255 refused under "
                      "EX-14 cosmetic dermatology (300). approved_total 2180, "
                      "refused_total 300. H-114 is on panel.",
         },
         "thought": "Eight calls, four turns. Not an approve and not a "
                    "decline: one decision letter covering both."},
    ],
}


class ScriptedBackend:
    """Replays SCRIPTS[case_id]. Deterministic, free, offline."""

    name = "scripted"

    def __init__(self, case_id):
        if case_id not in SCRIPTS:
            raise SystemExit(
                "\n  No script for case %r.\n"
                "  The scripted backend replays moves you wrote down; it does\n"
                "  not invent them. Two ways forward:\n"
                "    1. add %r to SCRIPTS in backends.py, or\n"
                "    2. set BACKEND = \"live\" in config.py (this costs money).\n"
                "  Scripted cases so far: %s\n"
                % (case_id, case_id, ", ".join(sorted(SCRIPTS))))
        self.steps = SCRIPTS[case_id]
        self.i = 0

    def next_move(self, transcript):
        """`transcript` is ignored on purpose - a script does not react.
        That is what makes it reproducible."""
        if self.i >= len(self.steps):
            return {"final": {"decision": "escalate",
                              "reason": "script ended without a conclusion"},
                    "thought": "script exhausted"}
        step = self.steps[self.i]
        self.i += 1
        return step

    # Token counts on the scripted backend are ESTIMATES, so your cost
    # arithmetic has something to chew on. They are not measurements and
    # you must not report them as such - D6 wants MEASURED counts, which
    # means the live battery.
    @staticmethod
    def token_estimate(transcript):
        return 1800 + 600 * len(transcript), 120


# =====================================================================
# LIVE
# =====================================================================
class LiveBackend:
    """Real model through OpenRouter. Costs money. D5(b) only."""

    name = "live"

    def __init__(self, case_id, tool_descriptors, system_prompt):
        self.case_id = case_id
        self.tools = tool_descriptors
        self.system_prompt = system_prompt
        self._last_usage = (0, 0)
        self._reported_costs = []
        self.last_raw_response = ""

    def next_move(self, transcript):
        messages = [{"role": "system", "content": self.system_prompt}]
        for entry in transcript:
            messages.append({"role": entry["role"], "content": entry["content"]})
        response = _live_call(messages)
        self.last_raw_response = response.get("content", "")
        usage = response.get("usage") or {}
        # OpenRouter uses prompt_tokens/completion_tokens.  The aliases make
        # this adapter tolerant of an OpenAI-compatible provider that calls
        # them input/output tokens instead.
        self._last_usage = (int(usage.get("prompt_tokens",
                                          usage.get("promptTokens",
                                          usage.get("input_tokens", 0))) or 0),
                            int(usage.get("completion_tokens",
                                          usage.get("completionTokens",
                                          usage.get("output_tokens", 0))) or 0))
        if usage.get("cost") is not None:
            try:
                self._reported_costs.append(float(usage["cost"]))
            except (TypeError, ValueError):
                pass
        return _parse_move(self.last_raw_response)

    def token_estimate(self, transcript):
        """Measured usage from the immediately preceding API response."""
        return self._last_usage

    def measured_cost(self):
        """Provider-reported cost when OpenRouter supplied it, else None."""
        return sum(self._reported_costs) if self._reported_costs else None


def _parse_move(text):
    """Parse the required JSON without mistaking Markdown fences for a run.

    The API requests JSON mode, but accepting a surrounding ```json fence is
    a harmless compatibility measure.  We never infer an action from prose:
    genuinely invalid output remains a loud, gradeable failed record.
    """
    candidate = (text or "").strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    try:
        return _normalise_move(json.loads(candidate))
    except json.JSONDecodeError:
        # Some providers add one short sentence before/after an otherwise
        # valid object.  Recover only the complete outer object, never a
        # partial fragment or a tool call hidden in prose.
        left, right = candidate.find("{"), candidate.rfind("}")
        if left >= 0 and right > left:
            try:
                return _normalise_move(json.loads(candidate[left:right + 1]))
            except json.JSONDecodeError:
                pass
        return {"final": {"decision": "escalate",
                          "reason": "model did not return parseable JSON: %s"
                                    % candidate[:200]},
                "thought": "unparseable: %s" % candidate[:200]}


def _normalise_move(move):
    """Accept an OpenAI-compatible final-answer spelling used by some models.

    The agent protocol specifies ``{\"final\": {...}}``.  Some providers
    instead emit a single pseudo-tool call for either ``final`` or a known
    decision such as ``request_information``.  Normalising only those *single*,
    structured forms at the vendor adapter boundary keeps the core ReAct loop
    vendor-neutral.  It deliberately does not turn an arbitrary unknown tool
    into a final answer.
    """
    if not isinstance(move, dict):
        return move

    thought = move.get("thought", "")
    decision_names = {
        "approve_in_principle", "book", "escalate", "request_document",
        "request_information",
    }

    def as_final(name, payload):
        record = dict(payload)
        if name != "final":
            record.setdefault("decision", name)
        return {"thought": thought, "final": record}

    if (move.get("tool") == "final" or move.get("tool") in decision_names) \
            and isinstance(move.get("args"), dict):
        return as_final(move["tool"], move["args"])

    calls = move.get("calls")
    if (isinstance(calls, list) and len(calls) == 1 and
            isinstance(calls[0], (list, tuple)) and len(calls[0]) == 2 and
            calls[0][0] in decision_names | {"final"} and
            isinstance(calls[0][1], dict)):
        return as_final(calls[0][0], calls[0][1])

    return move


def get_api_key():
    """Return an OpenRouter key without ever writing it to disk.

    A key in the environment is preferred for automation. If it is absent,
    an interactive terminal run asks once with hidden input. The key remains
    only in this Python process and is never printed or committed.
    """
    if not config.API_KEY:
        config.API_KEY = getpass("OpenRouter API key (input hidden): ").strip()
    if not config.API_KEY:
        raise SystemExit("No API key entered. Set BACKEND = 'scripted' to run free.")
    return config.API_KEY


LIVE_TIMEOUT_SECONDS = 90
LIVE_MAX_ATTEMPTS = 3


def _is_transport_timeout(error):
    """True only for a connection/read timeout, never an HTTP/model error."""
    if isinstance(error, (TimeoutError, socket.timeout)):
        return True
    return (isinstance(error, urllib.error.URLError)
            and isinstance(error.reason, (TimeoutError, socket.timeout)))


def _live_call(messages):
    """>>> THE ONLY FUNCTION IN THIS REPOSITORY THAT KNOWS A VENDOR <<<

    Everything else speaks in terms of moves and transcripts. Swapping
    vendor means rewriting this one function, and changing MODEL and
    BASE_URL in config.py. Nothing else.
    """
    api_key = get_api_key()
    body = json.dumps({
        "model": config.MODEL,
        "messages": messages,
        "temperature": 0,
        # The prompt still states the schema so the experiment is portable;
        # this API-level constraint makes a live run gradeable rather than
        # charging for prose we cannot execute.
        "response_format": {"type": "json_object"},
    }).encode()
    req = urllib.request.Request(
        config.BASE_URL.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Authorization": "Bearer " + api_key,
                 "Content-Type": "application/json"})
    # A transient transport or provider-capacity failure is not an agent
    # decision. Retry it twice, but never turn it into a clinical outcome.
    # A lost response can theoretically duplicate a request, so provider-
    # reported cost remains the authority for the final evidence.
    for attempt in range(1, LIVE_MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=LIVE_TIMEOUT_SECONDS) as r:
                payload = json.load(r)
            if (isinstance(payload, dict) and isinstance(payload.get("choices"), list)
                    and payload["choices"]):
                return {"content": payload["choices"][0]["message"].get("content", ""),
                        "usage": payload.get("usage") or {}}

            # OpenRouter can return a JSON error object (sometimes with a 2xx
            # status) when an upstream provider is temporarily unavailable.
            # The old code indexed ``choices`` and hid the useful reason behind
            # KeyError. Capture it and give a transient provider response a
            # bounded retry before failing explicitly.
            error_info = payload.get("error", payload) if isinstance(payload, dict) else payload
            if attempt == LIVE_MAX_ATTEMPTS:
                raise RuntimeError(
                    "OpenRouter returned no completion after %s attempts: %s"
                    % (LIVE_MAX_ATTEMPTS, str(error_info)[:500]))
            time.sleep(attempt)
            continue
        except urllib.error.HTTPError as error:
            # HTTPError exposes the provider's JSON/text response on the
            # exception itself.  Surface it instead of leaving the runner
            # with only "HTTP 400", which cannot distinguish an invalid
            # parameter from a provider-side availability refusal.
            try:
                detail = error.read().decode("utf-8", errors="replace")
            except Exception:
                detail = "(could not read response body)"
            raise RuntimeError(
                "OpenRouter HTTP %s for model %s: %s"
                % (error.code, config.MODEL, detail[:800])) from error
        except (TimeoutError, socket.timeout, urllib.error.URLError) as error:
            timed_out = _is_transport_timeout(error)
            if not timed_out or attempt == LIVE_MAX_ATTEMPTS:
                if timed_out:
                    raise TimeoutError(
                        "OpenRouter read timed out after %s attempts of %ss. "
                        "No result was recorded; rerun this battery."
                        % (LIVE_MAX_ATTEMPTS, LIVE_TIMEOUT_SECONDS)) from error
                raise
            time.sleep(1)


def make_backend(case_id, tool_descriptors=None, system_prompt=""):
    if config.BACKEND == "scripted":
        return ScriptedBackend(case_id)
    if config.BACKEND == "live":
        return LiveBackend(case_id, tool_descriptors or [], system_prompt)
    raise SystemExit("BACKEND must be 'scripted' or 'live', not %r"
                     % config.BACKEND)


# LOAD_PROBLEM_B_40_CASE_SCRIPTS
# Frozen deterministic fixtures used by D3(b), D5(a), and D7.
# They do not represent live-model accuracy.
from problem_b_scripts import PROBLEM_B_SCRIPTS
SCRIPTS.update(PROBLEM_B_SCRIPTS)
