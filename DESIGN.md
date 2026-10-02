# Design

This document explains how Webcheck is built and why.

## Goal

Detect common web application weaknesses in a controlled environment, identify insecure access controls in a programming interface, and analyze responses for suspicious behaviour.

## The two programs

1. **The practice application** (`practice_app/app.py`). A small website built with Flask. It runs in two modes chosen by the `SECURE` setting: weak (`SECURE=0`) and fixed (`SECURE=1`). It uses fake data only and listens only on the local computer (`127.0.0.1`, port 5050).
2. **The tool** (`tool/webcheck.py`). It sends requests to a target, runs three groups of checks, and writes a report.

Keeping the target under your own control is what makes this a controlled environment: nothing is tested without permission, and every weakness is known in advance, so you can confirm the tool finds what it should.

## How the tool works

```
webcheck.py  (reads options, safety check on the target)
    |
    +--> client.py              sends every request and keeps a Record of every response
    |
    +--> weakness_scanner.py    part 1: headers, leaks, exposed files, login limit
    +--> access_control_tester.py part 2: two users, one admin path
    +--> response_analyzer.py   part 3: studies all saved responses
    |
    +--> report.py              collects results and writes the report
```

1. **Safety check.** If the target is not on this computer, the tool stops unless `--i-have-permission` is given.
2. **Client.** Every request goes through `client.py`. It uses a fresh request each time, so cookies never carry over between calls and the "no login" tests are honest. Each response is saved as a `Record` (status, headers, cookies, first 5000 characters of the body, whether the request was logged in).
3. **Part 1, weakness scanner.** Loads the home page and checks its headers. Then asks for a list of well-known sensitive files and sends ten wrong logins in a row.
4. **Part 2, access-control tester.** Logs in as two ordinary users. It then tries: reading a record with no login, reading the other user's record, and using an admin function as an ordinary user. It first confirms each user can read their own record, so a wrong setting does not produce a false result.
5. **Part 3, response analyzer.** Sends two extra requests (a missing page and a request designed to cause an error), compares the login answers for an unknown user and a known user, and then studies every saved response.
6. **Report.** Every check becomes one result: area, title, severity, pass or fail, evidence, and fix. The report lists all of them, then explains each failure.

## Why part 3 runs last

Cookies from logging in only exist after part 2 has run, and the analyzer needs the full set of saved responses. Running it last lets it study everything the tool saw.

## Design choices

- **Simple and readable.** Plain Python, two libraries, no database. Each part is one short file so you can explain it.
- **One result format.** Every check calls the same `collector.add(...)`, which makes the report uniform and easy to extend.
- **A part can fail without stopping the rest.** If a login fails, the tool records an Info result and still reports what the other parts found. If the target cannot be reached at all, it stops with a clear message.
- **Evidence in every result.** Each result says what was actually seen (for example the status number), so a finding can be checked by hand.

## How to add a new check

1. Choose the file that fits (part 1, 2 or 3).
2. Write a function that sends requests with `client.request(...)`.
3. Call `collector.add(AREA, "Title", "High/Medium/Low/Info", passed, "what was seen", "how to fix")`.
4. Call your function from that file's `run(...)` function.
5. If the practice application should demonstrate it, add a weakness to `practice_app/app.py` and a fix under the `SECURE` branch.
