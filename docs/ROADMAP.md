# Roadmap

Deliverables follow the project's *Deliverables & Checkpoints* plan (QAMP 2026).
Each module is added in its own pull request with tests and documentation.

| ID | Deliverable | Module | Status |
|---|---|---|---|
| D1.1 | Repository, CI, pinned environment (laptop + HPC) | repository | **done** |
| D1.2 | Benchmark suite F1–F8, Clifford twins, exact ideal values | `qrace.bench` | **done** |
| D1.3 | 24-arm execution adapter with equal-cost shot accounting | `qrace.arms`, `qrace.run` | planned |
| D1.4 | Feature extractor v1 (circuit, timing, hardware, physics) | `qrace.features` | planned |
| D1.5 | Noise regimes A–E and pilot simulation dataset | `qrace.noise`, `qrace.data` | planned |
| D1.6 | QPU pilot and first hardware oracle batch | `qrace.run`, `qpu/` | planned |
| D1.7 | Hardware heatmap (circuits × arms) | `qrace.eval` | planned |
| D1.8 | Related-work table and pre-registration draft | `docs/` | planned |
| D2.x | Full dataset, Stages 1–3, freeze and pre-registration | `qrace.models`, `qrace.select` | Phase 2 |
| D3.x | Blind test, release v1.0, tutorials, showcase | all | Phase 3 |

## Conventions carried into later modules

* Benchmark instances are consumed through `qrace.bench.load_suite` and identified
  by `circuit_id`; every dataset row keys on it.
* Held-out families (F7, F8) are filtered by `instance.split == "heldout"` and must
  not reach training code or hardware before the pre-registered freeze.
* Hardware probes use `qrace.bench.twin_instance`, whose signal observables have
  ideal values of ±1.
