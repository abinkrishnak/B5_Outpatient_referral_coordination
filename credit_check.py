#!/usr/bin/env python3
"""Show OpenRouter key usage without exposing the key or making a model call."""
import json
import urllib.request

from backends import get_api_key


def credit_check():
    """Ask OpenRouter for remaining credit; this does not run a model."""
    try:
        request = urllib.request.Request(
            "https://openrouter.ai/api/v1/key",
            headers={"Authorization": "Bearer " + get_api_key()},
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.load(response)["data"]

        used, cap = data.get("usage"), data.get("limit")
        if cap is None:
            print("spent so far: $%.4f (no cap set on this key)" % (used or 0))
        else:
            print("spent $%.4f of $%.2f -> $%.4f remaining"
                  % (used or 0, cap, cap - (used or 0)))

        rate_limit = data.get("rate_limit") or {}
        if rate_limit:
            print("rate limit: %s requests per %s"
                  % (rate_limit.get("requests"), rate_limit.get("interval")))
    except Exception as error:
        print("Could not check credit: %s" % str(error)[:160])


if __name__ == "__main__":
    credit_check()
