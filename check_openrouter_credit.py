#!/usr/bin/env python3
"""Check OpenRouter key usage without saving or displaying the key."""
import getpass
import json
import os
import urllib.request


def credit_check(api_key):
    """Print usage and remaining credit. The status request itself is free."""
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": "Bearer " + api_key},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)["data"]

    used = data.get("usage")
    cap = data.get("limit")
    if cap is None:
        print("Spent so far: ${:.4f} (no spend cap set on this key).".format(used or 0))
    else:
        print("Spent ${:.4f} of ${:.2f}; ${:.4f} remaining.".format(
            used or 0, cap, cap - (used or 0)))

    rate_limit = data.get("rate_limit") or {}
    if rate_limit:
        print("Rate limit: {} requests per {}.".format(
            rate_limit.get("requests", "?"), rate_limit.get("interval", "?")))


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        api_key = getpass.getpass("OpenRouter API key (input is hidden): ").strip()
    if not api_key:
        raise SystemExit("No key entered. Nothing was sent.")

    try:
        credit_check(api_key)
    except Exception as error:
        print("Could not check credit: {}".format(str(error)[:160]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
