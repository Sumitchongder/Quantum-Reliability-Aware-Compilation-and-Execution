# Q-RACE log

One entry per week: done, next, blocked. Newest first.

## Week 1 (17–23 Nov 2026)

### Done
- **D1.1 repository:** package skeleton, README, Apache-2.0 licence, pinned
  `requirements.lock` (uv, universal, Python 3.11 and 3.12), GitHub Actions CI
  (Ubuntu 3.11/3.12, Windows 3.12): green.
- **Fresh clone install** (Windows, Python 3.12, `pip install -r requirements.lock`):
  2 min 47 s. Tests pass. Limit: 15 min. Also set up on a second laptop
  (Windows, venv, Python 3.12): tests pass.
- **Package moved to `src/` layout** (`src/qrace/`), so tests always run against the
  installed package.
- **D1.2 benchmark suite** imported from Sumit's version into `src/qrace/bench/`
  (families F1-F8, Clifford twins, exact ideal values). Acceptance test
  `tests/test_ideal_values.py`: 865 tests pass (ideal values vs statevector,
  n = 4-10, 3 seeds, tolerance 1e-9). Full suite: ~1157 passed. CI: green.
  `qrace-bench verify` on the smoke suite: passed.

### Next
- Week-1 smoke tests: GHZ through the arms on FakeMarrakesh.
- D1.3 arm adapter (24 arms, equal-cost shot accounting).
- Read references [1], [17], [11]; start related-work notes.

### Blocked
- Nothing.