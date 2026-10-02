# Webcheck

A small Python tool that checks a website and its programming interface for common security weaknesses. It comes with a practice website that is weak on purpose, so you can test the tool safely.

> **Only test websites you own or have written permission to test.** The tool refuses any website that is not on your own computer unless you add `--i-have-permission`.

## What it checks

| Group | Checks |
| --- | --- |
| Settings | Five security headers are present; the Server header does not reveal a version |
| Access | An order cannot be read without logging in; one user cannot read another user's order; a normal user cannot use an admin page |
| Responses | Login errors do not reveal which users exist; error pages do not show internal details; responses do not contain passwords or secrets |
| Cookies | Each cookie has the Secure and HttpOnly flags |

That is 16 checks on the practice website. Every failed check is explained in the report with what was seen and how to fix it.

## Files

```
webcheck-simple/
├── webcheck.py        the tool
├── practice_app.py    the practice website (weak and fixed versions)
├── run_demo.py        optional: runs both versions and scans them
├── requirements.txt   libraries needed
├── LICENSE
└── README.md
```

## Installation

You need Python 3.9 or newer. Run these commands in a terminal inside the project folder.

**Windows**

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac or Linux**

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

After activating, you should see `(venv)` at the start of your terminal line.

## Usage

### Option 1: one command

```
python run_demo.py
```

It starts the weak practice website, scans it, stops it, then does the same for the fixed version. Expected result:

```
Weak version : SUMMARY checks=16 passed=1 failed=15
Fixed version: SUMMARY checks=16 passed=16 failed=0
```

Two reports are created: `report_weak.md` and `report_fixed.md`.

### Option 2: step by step (two terminals)

**Terminal 1: start the weak practice website**

| System | Command |
| --- | --- |
| Windows Command Prompt | `set SECURE=0` then `python practice_app.py` |
| Windows PowerShell | `$env:SECURE="0"` then `python practice_app.py` |
| Mac or Linux | `SECURE=0 python3 practice_app.py` |

Leave it running. It listens on `http://127.0.0.1:5050`.

**Terminal 2: run the tool** (activate the virtual environment first)

```
python webcheck.py --target http://127.0.0.1:5050 --report report_weak.md
```

**Try the fixed version:** press `Ctrl+C` in terminal 1, start the website again with `SECURE=1` instead of `SECURE=0`, then run the tool again with `--report report_fixed.md`.

### Options

| Option | Meaning | Default |
| --- | --- | --- |
| `--target` | Website address to check (required) | none |
| `--report` | Report file to write | `report.md` |
| `--user-a` | First test user as `name:password` | `alice:alicepass` |
| `--user-b` | Second test user as `name:password` | `bob:bobpass` |
| `--i-have-permission` | Confirms you may test a website that is not on your computer | off |

### Reading the results

The terminal shows `PASS` or `FAIL` for each check, with what was seen for every failure. The report file lists all checks, then explains each failed check and how to fix it.

## Testing a different website

Open `webcheck.py` and change the paths at the top (login, order, admin and error paths) to match the website. You also need two ordinary test accounts on it, never real people's accounts, and the order numbers that belong to each of them.

## Limits

- It checks a short list of well-known weaknesses. It does not find everything and does not try to break in.
- It supports one login style: a token sent in the `Authorization` header.
- A passing report does not mean a website is secure. It means these specific checks passed.

## License

MIT License. See the `LICENSE` file.
