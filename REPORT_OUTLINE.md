# Two-page report outline (with draft text)

Replace anything in [square brackets]. Aim for two pages.

---

**Title:** Webcheck: a tool to find common web and programming-interface weaknesses

**Author:** [your name]   **Date:** [date]   **Code:** [link to your repository]

## 1. Goal

The aim was to build a tool that (1) detects common web application weaknesses in a controlled environment, (2) identifies insecure access controls in a programming interface, and (3) analyzes responses for suspicious behaviour.

## 2. Approach

Webcheck has three parts that share one request helper and one report writer.

- **Weakness scanner:** checks six security headers, version leaks, open cross-origin sharing, four commonly exposed files, and whether repeated wrong logins are limited.
- **Access-control tester:** logs in as two users and tests whether one can read the other's records, whether records can be read with no login, and whether a normal user can reach an admin function.
- **Response analyzer:** studies every response for stack traces, passwords or secrets, login messages that reveal usernames, missing cache protection, and cookie flags.

## 3. Controlled environment

To test safely, a practice website was built with fake data on the local computer. It has a weak mode with planted weaknesses and a fixed mode with the same weaknesses closed. This allowed a before and after comparison and confirmed the tool finds what it should.

## 4. Results

| Version | Checks | Passed | Failed | High | Medium | Low |
| --- | --- | --- | --- | --- | --- | --- |
| Weak | 32 | 5 | 27 | 9 | 9 | 9 |
| Fixed | 32 | 32 | 0 | 0 | 0 | 0 |

Selected findings on the weak version:

1. **Broken access control (High):** one user could read another user's order (status 200 instead of a refusal), and a normal user could use the admin function.
2. **Sensitive data exposure (High):** a public `/.env` file and a profile answer that included a password.
3. **Internal details in errors (High):** a stack trace and database text were shown to the visitor.
4. **Weak cookies (Medium):** cookies had no Secure or HttpOnly flag.
5. **Username guessing (Medium):** "User not found" and "Wrong password" revealed which names exist.

## 5. Fixes and re-test

Each weakness was closed in the fixed mode: ownership checks on records, role checks on the admin function, generic error messages, removal of the public file, a login attempt limit, security headers, and cookie flags. The second scan passed all 32 checks.

## 6. Limits

- It checks a fixed list of well-known weaknesses and does not try to break in.
- It supports one common login style (token in the Authorization header).
- It was tested only on its own practice application.
- A passing report does not mean a site is secure.

## 7. Next steps

Add checks for redirects to the encrypted address, support more login styles, and draw before and after charts from saved result data.

---

**Tip:** put the severity table and two example findings from `reports/report_weak.md` in the report, and link to the repository for everything else.
