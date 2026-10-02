"""Webcheck: a simple tool that checks a website for common weaknesses.

Only use it on websites you own or have written permission to test.
"""
import argparse
import re
import sys
from datetime import datetime
from urllib.parse import urlparse

import requests

# Paths on the website being tested. Change these to match another website.
LOGIN_PATH = "/api/login"
ORDER_PATH = "/api/orders/{id}"
ORDER_A, ORDER_B = "101", "102"       # order owned by user A, order owned by user B
ADMIN_PATH = "/api/admin/users"
ERROR_PATH = "/api/search?q=%27"      # a request that makes the website raise an error

SECURITY_HEADERS = ["Content-Security-Policy", "Strict-Transport-Security",
                    "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy"]
ERROR_PATTERNS = [r"Traceback \(most recent call last\)", r'File ".*", line \d+', r"SELECT .* FROM"]
SECRET_PATTERN = re.compile(r"[\"']?(password|secret\w*|api[_-]?key)[\"']?\s*[:=]", re.IGNORECASE)

BASE = ""
RESULTS = []    # (group, name, passed, evidence, fix)
COOKIES = []    # every Set-Cookie line seen
BODIES = []     # (path, text) of every response seen


def check(group, name, passed, evidence, fix):
    RESULTS.append((group, name, passed, evidence, fix))


def send(method, path, token=None, body=None):
    headers = {"Authorization": "Bearer " + token} if token else {}
    try:
        r = requests.request(method, BASE + path, headers=headers, json=body,
                             timeout=10, allow_redirects=False)
    except requests.RequestException as error:
        sys.exit(f"Could not reach {BASE}{path}. Is the website running?\n{error}")
    raw = r.raw.headers
    COOKIES.extend(raw.getlist("Set-Cookie") if hasattr(raw, "getlist") else [])
    BODIES.append((path, r.text[:5000]))
    return r


def login(who):
    name, password = who.split(":", 1)
    r = send("POST", LOGIN_PATH, body={"username": name, "password": password})
    if r.status_code != 200:
        sys.exit(f"Could not log in as {name} (status {r.status_code}). Check the user and password.")
    return name, r.json()["token"]


def ok(response):
    return 200 <= response.status_code < 300


def scan_settings():
    home = send("GET", "/")
    for name in SECURITY_HEADERS:
        value = home.headers.get(name)
        check("Settings", f"Header {name} is set", bool(value),
              value or "header is missing", f"Add the {name} header.")
    server = home.headers.get("Server", "")
    check("Settings", "Server header hides its version", not any(c.isdigit() for c in server),
          f"Server: {server or 'not set'}", "Remove the version number from the Server header.")


def test_access(user_a, user_b):
    name_a, token_a = login(user_a)
    name_b, token_b = login(user_b)
    path_a, path_b = ORDER_PATH.format(id=ORDER_A), ORDER_PATH.format(id=ORDER_B)

    r = send("GET", path_a)
    check("Access", "An order needs a login", not ok(r),
          f"{path_a} with no login: status {r.status_code}", "Require a login on every order.")
    r = send("GET", path_b, token_a)
    check("Access", "User A cannot read user B's order", not ok(r),
          f"{name_a} asked for {path_b} (belongs to {name_b}): status {r.status_code}",
          "Check on the server that the logged-in user owns the order.")
    r = send("GET", ADMIN_PATH, token_a)
    check("Access", "A normal user cannot use the admin page", not ok(r),
          f"{name_a} asked for {ADMIN_PATH}: status {r.status_code}",
          "Check the user's role on the server before running admin functions.")
    return name_a


def analyze_responses(name_a):
    send("GET", ERROR_PATH)
    unknown = send("POST", LOGIN_PATH, body={"username": "nobody-here", "password": "x"})
    known = send("POST", LOGIN_PATH, body={"username": name_a, "password": "wrong-password"})
    same = unknown.status_code == known.status_code and unknown.text == known.text
    check("Responses", "Login errors do not reveal which users exist", same,
          f"Unknown user: {unknown.status_code} {unknown.text.strip()[:50]} | "
          f"Wrong password: {known.status_code} {known.text.strip()[:50]}",
          "Give the same answer for an unknown user and a wrong password.")

    bad = [p for p, text in BODIES if any(re.search(x, text) for x in ERROR_PATTERNS)]
    check("Responses", "Error pages do not show internal details", not bad,
          "Internal details shown at: " + ", ".join(dict.fromkeys(bad)) if bad else "none found",
          "Show a short generic error message and keep the details in the server log.")
    leaks = [p for p, text in BODIES if SECRET_PATTERN.search(text)]
    check("Responses", "Responses do not contain passwords or secrets", not leaks,
          "Password or secret found at: " + ", ".join(dict.fromkeys(leaks)) if leaks else "none found",
          "Never send passwords or secrets in a response.")


def check_cookies():
    seen = {}
    for text in COOKIES:
        parts = [p.strip() for p in text.split(";")]
        seen.setdefault(parts[0].split("=")[0], [p.lower() for p in parts[1:]])
    for name, flags in seen.items():
        check("Cookies", f"Cookie {name} has the Secure flag", "secure" in flags,
              f"flags: {', '.join(flags) or 'none'}", "Add the Secure flag.")
        check("Cookies", f"Cookie {name} has the HttpOnly flag", "httponly" in flags,
              f"flags: {', '.join(flags) or 'none'}", "Add the HttpOnly flag.")


def write_report(path):
    failed = [r for r in RESULTS if not r[2]]
    lines = ["# Webcheck report", "", f"- Target: {BASE}",
             f"- Date: {datetime.now():%Y-%m-%d %H:%M}",
             f"- Checks: {len(RESULTS)}, passed: {len(RESULTS) - len(failed)}, failed: {len(failed)}", "",
             "## All checks", "", "| Result | Group | Check |", "| --- | --- | --- |"]
    lines += [f"| {'PASS' if r[2] else 'FAIL'} | {r[0]} | {r[1]} |" for r in RESULTS]
    lines += ["", "## Failed checks and fixes", ""]
    for r in failed:
        lines += [f"### {r[1]}", f"- What was seen: {r[3]}", f"- How to fix: {r[4]}", ""]
    if not failed:
        lines.append("No failed checks.")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main():
    global BASE
    p = argparse.ArgumentParser(description="Check a website for common weaknesses.")
    p.add_argument("--target", required=True, help="Website address, for example http://127.0.0.1:5050")
    p.add_argument("--report", default="report.md", help="Report file to write (default: report.md)")
    p.add_argument("--user-a", default="alice:alicepass", help="First test user as name:password")
    p.add_argument("--user-b", default="bob:bobpass", help="Second test user as name:password")
    p.add_argument("--i-have-permission", action="store_true",
                   help="Required when the target is not on this computer")
    args = p.parse_args()

    if urlparse(args.target).hostname not in ("127.0.0.1", "localhost", "::1") and not args.i_have_permission:
        sys.exit("Refused: this website is not on your computer.\n"
                 "Only test websites you own or have written permission to test.\n"
                 "If you have permission, add --i-have-permission.")
    BASE = args.target.rstrip("/")

    print(f"Checking {BASE} ...\n")
    scan_settings()
    name_a = test_access(args.user_a, args.user_b)
    analyze_responses(name_a)
    check_cookies()

    for group, name, passed, evidence, _ in RESULTS:
        print(f"{'PASS' if passed else 'FAIL'}  [{group}] {name}")
        if not passed:
            print(f"        {evidence}")
    failed = sum(1 for r in RESULTS if not r[2])
    print(f"\nSUMMARY checks={len(RESULTS)} passed={len(RESULTS) - failed} failed={failed}")
    write_report(args.report)
    print(f"Report written to {args.report}")


if __name__ == "__main__":
    main()
