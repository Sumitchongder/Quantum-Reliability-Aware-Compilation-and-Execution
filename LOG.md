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

### Known issues / to discuss
- **Clifford twins after transpilation:** twins are made before transpiling. Transpiled
  separately for FakeMarrakesh (opt. level 3), twins lose most two-qubit gates
  (e.g. QAOA p=2: 94 CZ -> 0) and often get a different layout, so they don't see the
  same noise as their source. Rounding RZ angles after transpiling the source keeps
  identical pulses. Must be fixed before twins are used as hardware probes (D2.5).
- **F7** is a tilted-field Ising model; the guide says transverse-field. Confirm with Sumit.
- **F6 observables:** signal observables are added to the source observables (guide
  §7.1 says "same as source"); 77% of F6 observables have ideal value 0. Decide which
  observables count towards each arm's score.
- **HPC:** which cluster, scheduler (Slurm?) and Python versions? Needed for the setup
  script and a test job.
- **Idea:** MQT Bench circuits as an external held-out test set (decide before the freeze).

### Next
- Week-1 smoke tests: GHZ through the arms on FakeMarrakesh.
- D1.3 arm adapter (24 arms, equal-cost shot accounting).
- Read references [1], [17], [11]; start related-work notes.

### Blocked
- Nothing.