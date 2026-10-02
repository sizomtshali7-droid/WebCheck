# Five-slide outline

## Slide 1: Problem and goal
- Common web weaknesses are simple mistakes that attackers look for first.
- Goal: one tool that scans a website, tests access controls in its programming interface, and analyzes responses.
- Tested safely on a practice website built for this purpose.

*Say:* Why simple, repeatable checks are useful, and why testing is done only on systems you own.

## Slide 2: Design of the tool
- Three parts: weakness scanner, access-control tester, response analyzer.
- One request helper, one report writer, 32 checks.
- Simple diagram: practice website <-> tool <-> report.

*Say:* Walk through the diagram in `docs/DESIGN.md`.

## Slide 3: The practice website
- Weak mode with planted weaknesses, fixed mode with all of them closed.
- Examples: one user can read another's order, admin function open to normal users, public secret file, detailed error pages, unprotected cookies.
- Fake data only, local computer only.

*Say:* Why a controlled environment matters.

## Slide 4: Results before the fix
- 27 of 32 checks failed: 9 High, 9 Medium, 9 Low.
- Show one example finding with its evidence line, for example `alice requested /api/orders/102 (belongs to bob) and got status 200`.
- Show the severity table.

*Say:* What the evidence line proves, and why the severity was chosen.

## Slide 5: Results after the fix and limits
- 0 of 32 checks failed after fixes.
- Limits: fixed list of checks, one login style, tested on one application.
- Next steps: more login styles, redirect check, charts.

*Say:* A passing report does not mean a site is secure.
