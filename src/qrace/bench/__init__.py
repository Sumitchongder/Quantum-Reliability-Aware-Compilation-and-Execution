"""Benchmark circuits with exactly known ideal values (deliverable D1.2).

Quick start::

    from qrace.bench import make_instance, build_suite, verify_suite

    inst = make_instance("F4", n=8, index=0, p=1)      # one QAOA instance
    print(inst.circuit_id, inst.observables[:2], inst.ideal[:2])

    suite = build_suite("pilot")                        # 104 training + 12 held-out circuits
    print(verify_suite(suite, max_qubits=10))           # re-check against a state vector
"""

from .core import BenchmarkInstance, circuit_stats, derive_seed
from .families import (
    DEFAULT_BASE_SEED,
    FAMILIES,
    ISING_REGIMES,
    FamilyInfo,
    make_instance,
    pauli_label,
    twin_instance,
)
from .ideal import (
    IdealValueError,
    compute_ideal,
    is_clifford_circuit,
    reference_expectations,
    stabilizer_expectations,
    statevector_expectations,
    to_clifford_gates,
)
from .suite import (
    SUITE_SPECS,
    SuiteSpec,
    build_suite,
    load_suite,
    save_suite,
    summarize,
    verify_suite,
)
from .twins import TwinError, clifford_twin, snap_angle, two_qubit_structure

__all__ = [
    "DEFAULT_BASE_SEED",
    "FAMILIES",
    "ISING_REGIMES",
    "SUITE_SPECS",
    "BenchmarkInstance",
    "FamilyInfo",
    "IdealValueError",
    "SuiteSpec",
    "TwinError",
    "build_suite",
    "circuit_stats",
    "clifford_twin",
    "compute_ideal",
    "derive_seed",
    "is_clifford_circuit",
    "load_suite",
    "make_instance",
    "pauli_label",
    "reference_expectations",
    "save_suite",
    "snap_angle",
    "stabilizer_expectations",
    "statevector_expectations",
    "summarize",
    "to_clifford_gates",
    "twin_instance",
    "two_qubit_structure",
    "verify_suite",
]
