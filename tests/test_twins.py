"""Tests of Clifford twins (structure preservation and exactness)."""

from __future__ import annotations

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

from qrace.bench import (
    TwinError,
    clifford_twin,
    is_clifford_circuit,
    make_instance,
    snap_angle,
    twin_instance,
    two_qubit_structure,
)

from conftest import FAMILY_CASES, case_id


@pytest.mark.parametrize(
    ("angle", "expected"),
    [(0.0, 0.0), (0.7, 0.0), (0.8, np.pi / 2), (np.pi, np.pi), (-np.pi / 2, 3 * np.pi / 2), (2 * np.pi, 0.0)],
)
def test_snap_angle(angle, expected):
    assert snap_angle(angle) == pytest.approx(expected)


@pytest.mark.parametrize("case", FAMILY_CASES, ids=case_id)
def test_twin_preserves_structure_and_is_clifford(case):
    family, params = case
    inst = make_instance(family, 8, index=0, **params)
    twin = clifford_twin(inst.circuit)
    assert is_clifford_circuit(twin)
    assert two_qubit_structure(twin) == two_qubit_structure(inst.circuit)
    assert len(twin.data) == len(inst.circuit.data)
    assert twin.count_ops().get("barrier", 0) == inst.circuit.count_ops().get("barrier", 0)


@pytest.mark.parametrize("case", FAMILY_CASES, ids=case_id)
def test_twin_instance_has_signal(case):
    family, params = case
    twin = twin_instance(make_instance(family, 8, index=1, **params))
    assert twin.twin_of is not None
    assert np.any(np.abs(twin.ideal) == 1.0), "twin needs at least one +/-1 observable"


def test_twins_of_heldout_stay_heldout():
    twin = twin_instance(make_instance("F7", 6, index=0, regime="chaotic", steps=2))
    assert twin.split == "heldout"


def test_twin_rejects_unsupported_gates():
    qc = QuantumCircuit(1)
    qc.t(0)
    with pytest.raises(TwinError):
        clifford_twin(qc)
    qc2 = QuantumCircuit(1)
    qc2.rz(Parameter("theta"), 0)
    with pytest.raises(TwinError):
        clifford_twin(qc2)
