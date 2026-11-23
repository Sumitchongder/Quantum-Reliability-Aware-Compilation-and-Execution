"""Core data structures shared by all benchmark families."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from .ideal import NON_UNITARY_IGNORED, is_clifford_circuit

__all__ = [
    "IDEAL_METHODS",
    "SPLITS",
    "BenchmarkInstance",
    "circuit_stats",
    "derive_rng",
    "derive_seed",
]

#: Allowed values for :attr:`BenchmarkInstance.split`.
SPLITS = ("train", "heldout")

#: Allowed values for :attr:`BenchmarkInstance.ideal_method`.
IDEAL_METHODS = ("stabilizer", "statevector", "analytic")


def derive_seed(*parts: Any) -> int:
    """Deterministic 63-bit seed from arbitrary parts (stable across platforms and runs).

    Python's built-in ``hash`` is salted per process, so a SHA-256 digest is used instead.
    """
    text = "|".join(str(p) for p in parts).encode()
    return int.from_bytes(hashlib.sha256(text).digest()[:8], "big") >> 1


def derive_rng(*parts: Any) -> np.random.Generator:
    """NumPy generator seeded by :func:`derive_seed`."""
    return np.random.default_rng(derive_seed(*parts))


def circuit_stats(circuit: QuantumCircuit) -> dict[str, Any]:
    """Structural statistics of an (untranspiled) benchmark circuit."""
    n_1q = n_2q = 0
    for instruction in circuit.data:
        if instruction.operation.name in NON_UNITARY_IGNORED:
            continue
        if len(instruction.qubits) == 1:
            n_1q += 1
        else:
            n_2q += 1
    two_q = QuantumCircuit(circuit.num_qubits)
    for instruction in circuit.data:
        if len(instruction.qubits) >= 2 and instruction.operation.name not in NON_UNITARY_IGNORED:
            two_q.append(instruction.operation, instruction.qubits)
    return {
        "depth": int(circuit.depth(lambda ins: ins.operation.name not in NON_UNITARY_IGNORED)),
        "depth_2q": int(two_q.depth()),
        "n_1q": n_1q,
        "n_2q": n_2q,
        "is_clifford": bool(is_clifford_circuit(circuit)),
    }


@dataclass
class BenchmarkInstance:
    """One benchmark circuit with its observables and exact ideal values.

    Attributes
    ----------
    circuit_id:
        Stable identifier, e.g. ``"F4-qaoa-p2-n08-s0003"``. Unique within a suite.
    family:
        Family code ``"F1"`` ... ``"F8"``.
    variant:
        Sub-type inside the family (e.g. ``"ghz"``, ``"graph"``, ``"qaoa-p2"``).
    circuit:
        Measurement-free circuit acting on ``|0...0>``; observables are measured by
        an Estimator-style primitive.
    observables:
        Pauli labels (Qiskit little-endian: right-most character is qubit 0).
    ideal:
        Exact noise-free expectation value of each observable.
    ideal_method:
        How ``ideal`` was obtained: ``"stabilizer"``, ``"statevector"`` or ``"analytic"``.
    split:
        ``"train"`` or ``"heldout"``. Held-out families (F7, F8) must not be used for
        training or hardware runs before the pre-registered blind test.
    seed:
        Seed from which every random choice of this instance was derived.
    params:
        Generator parameters (JSON-serialisable), sufficient to regenerate the circuit.
    twin_of:
        For Clifford twins, the ``circuit_id`` of the source structure; otherwise ``None``.
    """

    circuit_id: str
    family: str
    variant: str
    circuit: QuantumCircuit
    observables: list[str]
    ideal: np.ndarray
    ideal_method: str
    split: str
    seed: int
    params: dict[str, Any] = field(default_factory=dict)
    twin_of: str | None = None

    def __post_init__(self) -> None:
        self.ideal = np.asarray(self.ideal, dtype=float)
        if self.split not in SPLITS:
            raise ValueError(f"split must be one of {SPLITS}, got {self.split!r}")
        if self.ideal_method not in IDEAL_METHODS:
            raise ValueError(f"ideal_method must be one of {IDEAL_METHODS}")
        if len(self.observables) != len(self.ideal):
            raise ValueError("observables and ideal values differ in length")
        if not self.observables:
            raise ValueError(f"{self.circuit_id}: at least one observable is required")
        for label in self.observables:
            if len(label) != self.n_qubits or set(label) - set("IXYZ"):
                raise ValueError(f"{self.circuit_id}: invalid Pauli label {label!r}")
            if set(label) == {"I"}:
                raise ValueError(f"{self.circuit_id}: identity is not a useful observable")
        if np.any(np.abs(self.ideal) > 1 + 1e-9):
            raise ValueError(f"{self.circuit_id}: Pauli expectation outside [-1, 1]")
        self.circuit.name = self.circuit_id

    @property
    def n_qubits(self) -> int:
        return self.circuit.num_qubits

    @property
    def stats(self) -> dict[str, Any]:
        return circuit_stats(self.circuit)

    def observable_weights(self) -> list[int]:
        """Number of non-identity factors in each observable."""
        return [sum(c != "I" for c in label) for label in self.observables]

    def to_record(self) -> dict[str, Any]:
        """JSON-serialisable description (everything except the circuit itself)."""
        return {
            "circuit_id": self.circuit_id,
            "family": self.family,
            "variant": self.variant,
            "n_qubits": self.n_qubits,
            "split": self.split,
            "seed": int(self.seed),
            "params": self.params,
            "twin_of": self.twin_of,
            "ideal_method": self.ideal_method,
            "observables": list(self.observables),
            "ideal": [float(v) for v in self.ideal],
            "observable_weights": self.observable_weights(),
            "stats": self.stats,
        }
