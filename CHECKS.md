# List of checks

The tool runs 32 checks against the practice application. The two cookie names are `visitor` and `session`, so the cookie group produces six results. Another target may produce a different number of cookie results.

A check **passes** when the protection is in place and **fails** when it is missing or weak.

## Part 1: Weakness scanner (14 checks)

| Check | Severity | Passes when |
| --- | --- | --- |
| Security header Content-Security-Policy is set | Medium | The header is present |
| Security header Strict-Transport-Security is set | Medium | The header is present |
| Security header X-Frame-Options is set | Low | The header is present |
| Security header X-Content-Type-Options is set | Low | The header is present |
| Security header Referrer-Policy is set | Low | The header is present |
| Security header Permissions-Policy is set | Low | The header is present |
| Server header does not reveal a version | Low | The Server header contains no digits |
| X-Powered-By header is not shown | Low | The header is absent |
| Cross-origin sharing is not open to every website | Medium | Access-Control-Allow-Origin is not `*` |
| Sensitive file `/.env` is not public | High | The address does not return status 200 |
| Sensitive file `/.git/config` is not public | High | The address does not return status 200 |
| Sensitive file `/backup.zip` is not public | High | The address does not return status 200 |
| Sensitive file `/config.json` is not public | High | The address does not return status 200 |
| Repeated wrong logins are limited | Medium | One of ten wrong logins in a row is answered with status 429 |

If a site answers status 200 even for pages that do not exist, the four file checks are replaced by one Info note, because the results would be unreliable.

## Part 2: Access-control tester (8 checks)

Run once for orders and once for profiles (six checks), plus two for the admin function.

| Check | Severity | Passes when |
| --- | --- | --- |
| A record cannot be read without logging in (orders, profiles) | High | The request with no login is refused |
| User A cannot read user B's record (orders, profiles) | High | The request is refused |
| User B cannot read user A's record (orders, profiles) | High | The request is refused |
| Admin function cannot be used without logging in | High | The request with no login is refused |
| Admin function is blocked for normal users | High | A normal user's request is refused |

"Refused" means any answer that is not a success (status 200 to 299).

## Part 3: Response analyzer (10 checks with two cookies)

| Check | Severity | Passes when |
| --- | --- | --- |
| Login errors do not reveal which usernames exist | Medium | An unknown user and a wrong password get the same answer |
| Error pages do not show internal details | High | No response contains a stack trace, file path with line number, or database text |
| Responses do not contain passwords or secrets | High | No response contains fields such as password, secret key or api key |
| Private responses forbid shared caching | Low | Every logged-in answer has Cache-Control with no-store or private |
| Cookie has the Secure flag (per cookie) | Medium | The Secure flag is present |
| Cookie has the HttpOnly flag (per cookie) | Medium | The HttpOnly flag is present |
| Cookie has a SameSite setting (per cookie) | Low | A SameSite value is present |

## Severity guide

- **High:** data can be read or control can be gained.
- **Medium:** a protection is weakened.
- **Low:** gives an attacker extra information or a small advantage.
- **Info:** a note about the test itself (for example, a login could not be completed).

## What these checks do not cover

Cross-site scripting, injection into forms, weak passwords, outdated software, encryption settings, file upload problems and many other weaknesses are outside this tool.
