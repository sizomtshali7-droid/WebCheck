# Testing

## Test environment

- Python 3.12.3, Flask 3.1.3, requests 2.33.1
- Practice application on `http://127.0.0.1:5050`
- Command used: `python run_demo.py`

## Results

| Version | Checks | Passed | Failed | High | Medium | Low |
| --- | --- | --- | --- | --- | --- | --- |
| Weak (`SECURE=0`) | 32 | 5 | 27 | 9 | 9 | 9 |
| Fixed (`SECURE=1`) | 32 | 32 | 0 | 0 | 0 | 0 |

The five checks that passed on the weak version were: an order cannot be read with no login, the admin function cannot be used with no login, and the files `/.git/config`, `/backup.zip` and `/config.json` are not public. These are correct passes, because the weak application protects those on purpose.

## Examples of what the weak version produced

- `alice requested /api/orders/102 (belongs to bob) and got status 200`
- `alice (a normal user) requested /api/admin/users and got status 200`
- `GET /.env returned status 200`
- `Sent 10 wrong logins in a row. Status codes seen: [404]`
- `Unknown user: status 404 ... Known user, wrong password: status 401 ...`
- `/api/users/1 contains 'password'`

## Safety test

Running the tool against a website that is not on this computer, without `--i-have-permission`, stops immediately with exit code 2 and sends no requests.

## How to repeat the tests

1. Set up as described in the README.
2. Run `python run_demo.py` and compare your numbers with the table above.
3. For one weakness at a time, start the weak application by hand, run the tool, then open the report and find the matching result.
4. Fix one weakness in `practice_app/app.py`, restart the application, run the tool again, and confirm that result changes from FAIL to PASS.

## Known limits of this testing

- The tool was only tested against its own practice application, so results on other websites may need option changes (login path, record paths).
- Tests ran on one computer setup. Results should be the same elsewhere, but the exact version text may differ.
- Passing every check shows the checks work as designed. It does not prove a real website is secure.
