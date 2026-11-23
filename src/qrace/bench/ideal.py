"""Exact (noise-free) expectation values for benchmark observables.

Every benchmark instance in Q-RACE carries observables whose ideal values are
known *exactly*. Three independent routes are supported:

``"stabilizer"``
    Clifford circuits. The circuit is converted to a :class:`~qiskit.quantum_info.Clifford`
    tableau and Pauli expectation values are read from a
    :class:`~qiskit.quantum_info.StabilizerState`. Cost is polynomial in the
    number of qubits, so this route scales to the 30-qubit Clifford families.

``"statevector"``
    Any circuit small enough for a dense state vector (``n <= MAX_STATEVECTOR_QUBITS``).

``"analytic"``
    Closed-form values supplied by the generator (e.g. mirror circuits, whose
    ideal output is a known computational-basis state).

The function :func:`reference_expectations` always uses the dense state vector
and is the reference against which the other routes are validated in the test
suite (acceptance criterion of deliverable D1.2).

Pauli labels follow Qiskit's little-endian convention: the right-most
character acts on qubit 0.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, Pauli, StabilizerState, Statevector

__all__ = [
    "CLIFFORD_GATES",
    "MAX_STATEVECTOR_QUBITS",
    "ROTATION_GATES",
    "IdealValueError",
    "compute_ideal",
    "is_clifford_circuit",
    "reference_expectations",
    "stabilizer_expectations",
    "statevector_expectations",
    "to_clifford_gates",
]

#: Largest register for which dense state-vector evaluation is allowed.
MAX_STATEVECTOR_QUBITS = 20

#: Gate names that are Clifford for every parameter value (they have none).
CLIFFORD_GATES = frozenset(
    {"id", "x", "y", "z", "h", "s", "sdg", "sx", "sxdg", "cx", "cy", "cz", "swap", "ecr"}
)

#: Single-qubit rotations that are Clifford when the angle is a multiple of pi/2.
ROTATION_GATES = frozenset({"rx", "ry", "rz"})

#: Operations that do not act on the quantum state and are ignored.
NON_UNITARY_IGNORED = frozenset({"barrier"})

_HALF_PI = np.pi / 2
_ANGLE_ATOL = 1e-9


class IdealValueError(ValueError):
    """Raised when an exact ideal value cannot be computed by the requested route."""


def _quarter_turns(angle: float) -> int | None:
    """Return ``k`` in ``{0, 1, 2, 3}`` if ``angle == k * pi/2 (mod 2 pi)``, else ``None``."""
    k = angle / _HALF_PI
    k_round = round(k)
    if abs(k - k_round) > _ANGLE_ATOL:
        return None
    return int(k_round) % 4


def is_clifford_circuit(circuit: QuantumCircuit) -> bool:
    """Return ``True`` if every instruction in ``circuit`` is a Clifford operation.

    Rotations ``rx``, ``ry`` and ``rz`` count as Clifford only when their angle is
    a multiple of pi/2 (within a tolerance of 1e-9 rad). Barriers are ignored.
    Circuits containing measurements, resets or unbound parameters are not Clifford.
    """
    for instruction in circuit.data:
        op = instruction.operation
        name = op.name
        if name in NON_UNITARY_IGNORED or name in CLIFFORD_GATES:
            continue
        if name in ROTATION_GATES:
            angle = op.params[0]
            if not isinstance(angle, (int, float, np.floating)):
                return False
            if _quarter_turns(float(angle)) is None:
                return False
            continue
        return False
    return True


def _append_clifford_rotation(qc: QuantumCircuit, name: str, k: int, q: int) -> None:
    """Append the Clifford gate sequence equal (up to global phase) to ``name(k*pi/2)`` on ``q``."""
    if k == 0:
        return
    if name == "rz":
        {1: qc.s, 2: qc.z, 3: qc.sdg}[k](q)
    elif name == "rx":
        {1: qc.sx, 2: qc.x, 3: qc.sxdg}[k](q)
    elif name == "ry":
        # Ry(theta) = S . Rx(theta) . S^dagger  (circuit order: sdg, rx, s)
        qc.sdg(q)
        _append_clifford_rotation(qc, "rx", k, q)
        qc.s(q)
    else:  # pragma: no cover - guarded by caller
        raise IdealValueError(f"unsupported rotation {name!r}")


def to_clifford_gates(circuit: QuantumCircuit) -> QuantumCircuit:
    """Return an equivalent circuit (up to global phase) built only from :data:`CLIFFORD_GATES`.

    Rotations with angles that are multiples of pi/2 are rewritten as named
    Clifford gates; barriers are dropped. Raises :class:`IdealValueError` if the
    circuit is not Clifford.
    """
    if not is_clifford_circuit(circuit):
        raise IdealValueError(f"circuit {circuit.name!r} is not a Clifford circuit")
    out = QuantumCircuit(circuit.num_qubits, name=circuit.name)
    for instruction in circuit.data:
        op = instruction.operation
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        if op.name in NON_UNITARY_IGNORED:
            continue
        if op.name in ROTATION_GATES:
            k = _quarter_turns(float(op.params[0]))
            assert k is not None
            _append_clifford_rotation(out, op.name, k, qubits[0])
        else:
            out.append(op, qubits)
    return out


def _as_paulis(observables: Sequence[str], num_qubits: int) -> list[Pauli]:
    paulis = []
    for label in observables:
        if len(label) != num_qubits:
            raise IdealValueError(f"observable {label!r} has length {len(label)}, expected {num_qubits}")
        paulis.append(Pauli(label))
    return paulis


def stabilizer_expectations(circuit: QuantumCircuit, observables: Sequence[str]) -> np.ndarray:
    """Exact Pauli expectation values of ``circuit|0...0>`` via the stabilizer formalism."""
    clifford = Clifford(to_clifford_gates(circuit))
    state = StabilizerState(clifford)
    paulis = _as_paulis(observables, circuit.num_qubits)
    return np.array([float(state.expectation_value(p)) for p in paulis], dtype=float)


def statevector_expectations(circuit: QuantumCircuit, observables: Sequence[str]) -> np.ndarray:
    """Exact Pauli expectation values of ``circuit|0...0>`` via a dense state vector."""
    if circuit.num_qubits > MAX_STATEVECTOR_QUBITS:
        raise IdealValueError(
            f"{circuit.num_qubits} qubits exceeds the state-vector limit "
            f"({MAX_STATEVECTOR_QUBITS}); use the stabilizer or analytic route"
        )
    bare = circuit.remove_final_measurements(inplace=False)
    state = Statevector(bare)
    paulis = _as_paulis(observables, circuit.num_qubits)
    values = np.array([complex(state.expectation_value(p)) for p in paulis])
    if values.size and np.max(np.abs(values.imag)) > 1e-9:  # Hermitian Paulis: real values
        raise IdealValueError("non-real expectation value; check the observable labels")
    return values.real.astype(float)


def reference_expectations(circuit: QuantumCircuit, observables: Sequence[str]) -> np.ndarray:
    """Dense state-vector reference used to validate every other route in the tests."""
    return statevector_expectations(circuit, observables)


def compute_ideal(
    circuit: QuantumCircuit,
    observables: Sequence[str],
    method: str = "auto",
) -> tuple[np.ndarray, str]:
    """Compute exact ideal values and return ``(values, method_used)``.

    ``method`` is ``"stabilizer"``, ``"statevector"`` or ``"auto"`` (stabilizer for
    Clifford circuits, otherwise state vector). The ``"analytic"`` route is owned by
    the generators, which pass their closed-form values directly.
    """
    if method == "auto":
        method = "stabilizer" if is_clifford_circuit(circuit) else "statevector"
    if method == "stabilizer":
        return stabilizer_expectations(circuit, observables), method
    if method == "statevector":
        return statevector_expectations(circuit, observables), method
    raise IdealValueError(f"unknown ideal-value method {method!r}")
