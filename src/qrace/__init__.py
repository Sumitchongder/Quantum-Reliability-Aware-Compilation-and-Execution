"""Q-RACE: Quantum Reliability-Aware Compilation and Execution.

Learns which combination of qubit layout, error suppression and error mitigation
gives a quantum circuit the lowest error on IBM Quantum hardware, under a fixed
QPU-time budget.

Subpackages
-----------
bench
    Benchmark families F1-F8, Clifford twins and exact ideal values (deliverable D1.2).

Further subpackages (execution strategies, noise models, features, models and
evaluation) are added in later deliverables; see ``docs/ROADMAP.md``.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
