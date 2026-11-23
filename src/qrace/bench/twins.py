"""Clifford twins: structure-preserving Clifford proxies of benchmark circuits.

A *Clifford twin* keeps every two-qubit gate, every barrier and the order of all
instructions of the source circuit, and only rounds the angle of each
single-qubit rotation (``rx``, ``ry``, ``rz``) to the nearest multiple of pi/2.
The twin therefore occupies the same physical qubits, has the same entangling
structure and (after transpilation) essentially the same timing as its source,
while its ideal expectation values can be computed exactly by stabilizer
simulation at any width. This idea follows Clifford data regression
(Czarnik et al., Quantum 5, 592, 2021); Q-RACE uses it to rank execution
strategies on hardware without knowing the source circuit's answer.

Benchmark generators in :mod:`qrace.bench.families` build all non-Clifford
structure from ``rx``/``ry``/``rz`` and Clifford entanglers only, so that the
twin of every circuit is guaranteed to be Clifford.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, Pauli

from .ideal import CLIFFORD_GATES, NON_UNITARY_IGNORED, ROTATION_GATES, to_clifford_gates

__all__ = [
    "TwinError",
    "clifford_twin",
    "signal_observables",
    "snap_angle",
    "two_qubit_structure",
]

_HALF_PI = np.pi / 2


class TwinError(ValueError):
    """Raised when a circuit contains an operation that cannot be twinned."""


def snap_angle(angle: float) -> float:
    """Round ``angle`` to the nearest multiple of pi/2, returned in ``[0, 2 pi)``."""
    k = int(np.round(float(angle) / _HALF_PI)) % 4
    return k * _HALF_PI


def clifford_twin(circuit: QuantumCircuit, name: str | None = None) -> QuantumCircuit:
    """Return the Clifford twin of ``circuit``.

    Parameters
    ----------
    circuit:
        Source circuit built from :data:`~qrace.bench.ideal.CLIFFORD_GATES`,
        ``rx``/``ry``/``rz`` rotations with bound numeric angles, and barriers.
    name:
        Name of the returned circuit (defaults to ``"<source name>-twin"``).

    Raises
    ------
    TwinError
        If the circuit contains any other operation (for example a generic ``u``
        gate, a controlled rotation, a measurement or an unbound parameter).
    """
    twin = QuantumCircuit(*circuit.qregs, *circuit.cregs, name=name or f"{circuit.name}-twin")
    for instruction in circuit.data:
        op = instruction.operation
        if op.name in ROTATION_GATES:
            angle = op.params[0]
            if not isinstance(angle, (int, float, np.floating)):
                raise TwinError(f"unbound parameter in {op.name} of {circuit.name!r}")
            new_op = op.copy()
            new_op.params = [snap_angle(float(angle))]
            twin.append(new_op, instruction.qubits, instruction.clbits)
        elif op.name in CLIFFORD_GATES or op.name in NON_UNITARY_IGNORED:
            twin.append(op, instruction.qubits, instruction.clbits)
        else:
            raise TwinError(f"cannot twin operation {op.name!r} in {circuit.name!r}")
    twin.metadata = dict(circuit.metadata or {})
    return twin


def two_qubit_structure(circuit: QuantumCircuit) -> list[tuple[str, tuple[int, ...]]]:
    """Ordered list of ``(gate name, qubit indices)`` for all multi-qubit gates.

    Used to verify that a twin preserves its source's entangling structure.
    """
    out = []
    for instruction in circuit.data:
        if instruction.operation.name in NON_UNITARY_IGNORED:
            continue
        if len(instruction.qubits) >= 2:
            idx = tuple(circuit.find_bit(q).index for q in instruction.qubits)
            out.append((instruction.operation.name, idx))
    return out


def signal_observables(twin: QuantumCircuit, k: int = 4) -> list[str]:
    """Up to ``k`` low-weight Pauli observables with ideal value +/-1 on ``twin|0...0>``.

    Snapping rotation angles often drives the source observables of a twin to an
    ideal value of 0, which carries no information about how much a strategy
    reduces error. These observables restore the signal: each single-qubit
    stabilizer ``Z_q`` of the input state is evolved through the twin's Clifford
    (``U Z_q U^dagger``), which by construction has expectation value +/-1. The
    ``k`` lowest-weight results are returned (ties broken by qubit index), so the
    observables stay as local as the circuit allows.
    """
    n = twin.num_qubits
    cliff = Clifford(to_clifford_gates(twin))
    candidates = []
    for q in range(n):
        z = ["I"] * n
        z[n - 1 - q] = "Z"
        evolved = Pauli("".join(z)).evolve(cliff, frame="s")
        label = Pauli((evolved.z, evolved.x)).to_label()
        weight = sum(c != "I" for c in label)
        candidates.append((weight, q, label))
    out: list[str] = []
    for _, _, label in sorted(candidates):
        if label not in out:
            out.append(label)
        if len(out) == k:
            break
    return out
