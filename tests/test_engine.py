"""Tests of the exact ideal-value engine (stabilizer vs state vector)."""

from __future__ import annotations

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, random_clifford

from qrace.bench import (
    IdealValueError,
    compute_ideal,
    is_clifford_circuit,
    stabilizer_expectations,
    statevector_expectations,
    to_clifford_gates,
)
from qrace.bench.ideal import MAX_STATEVECTOR_QUBITS


@pytest.mark.parametrize("gate", ["rx", "ry", "rz"])
@pytest.mark.parametrize("k", [0, 1, 2, 3, 4, -1, 5])
def test_quarter_turn_rotations_map_to_equivalent_cliffords(gate, k):
    qc = QuantumCircuit(1)
    getattr(qc, gate)(k * np.pi / 2, 0)
    assert is_clifford_circuit(qc)
    assert Operator(to_clifford_gates(qc)).equiv(Operator(qc))


@pytest.mark.parametrize("angle", [0.1, np.pi / 3, np.pi / 2 + 1e-6])
def test_non_clifford_angles_are_detected(angle):
    qc = QuantumCircuit(1)
    qc.rz(angle, 0)
    assert not is_clifford_circuit(qc)
    with pytest.raises(IdealValueError):
        to_clifford_gates(qc)


def test_unsupported_operations_are_not_clifford():
    qc = QuantumCircuit(2)
    qc.t(0)
    assert not is_clifford_circuit(qc)
    qc2 = QuantumCircuit(1, 1)
    qc2.measure(0, 0)
    assert not is_clifford_circuit(qc2)


@pytest.mark.parametrize("seed", range(10))
def test_stabilizer_matches_statevector_on_random_cliffords(seed):
    n = 5
    qc = random_clifford(n, seed=seed).to_circuit()
    qc.rz(np.pi / 2, 0)
    qc.ry(3 * np.pi / 2, 1)
    rng = np.random.default_rng(seed)
    labels = ["".join(rng.choice(list("IXYZ"), size=n)) for _ in range(20)]
    labels = [lab for lab in labels if set(lab) != {"I"}]
    np.testing.assert_allclose(
        stabilizer_expectations(qc, labels), statevector_expectations(qc, labels), atol=1e-12
    )


def test_auto_route_selection():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    vals, method = compute_ideal(qc, ["ZZ", "XX", "ZI"])
    assert method == "stabilizer"
    np.testing.assert_allclose(vals, [1, 1, 0])
    qc.rz(0.3, 0)
    vals, method = compute_ideal(qc, ["ZZ"])
    assert method == "statevector"
    np.testing.assert_allclose(vals, [1])


def test_little_endian_labels():
    qc = QuantumCircuit(3)
    qc.x(0)
    vals, _ = compute_ideal(qc, ["IIZ", "ZII"])
    np.testing.assert_allclose(vals, [-1, 1])


def test_errors():
    qc = QuantumCircuit(2)
    with pytest.raises(IdealValueError):
        compute_ideal(qc, ["Z"])  # wrong length
    with pytest.raises(IdealValueError):
        compute_ideal(qc, ["ZZ"], method="magic")
    big = QuantumCircuit(MAX_STATEVECTOR_QUBITS + 1)
    with pytest.raises(IdealValueError):
        statevector_expectations(big, ["Z" * big.num_qubits])
