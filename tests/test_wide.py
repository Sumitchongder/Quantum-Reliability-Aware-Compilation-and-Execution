"""Wide circuits: stabilizer and analytic routes beyond state-vector reach."""

from __future__ import annotations

import numpy as np
import pytest

from qrace.bench import make_instance, reference_expectations


@pytest.mark.slow
@pytest.mark.parametrize(
    ("family", "params"),
    [
        ("F1", {"variant": "graph"}),
        ("F2", {"depth": 8}),
        ("F6", {"source": "F4", "p": 2}),
        ("F6", {"source": "F5", "reps": 3}),
    ],
)
def test_thirty_qubit_clifford_families(family, params):
    inst = make_instance(family, 30, index=0, **params)
    assert inst.ideal_method == "stabilizer"
    assert np.all(np.isin(np.round(inst.ideal, 12), [-1.0, 0.0, 1.0]))


@pytest.mark.slow
def test_mirror_analytic_matches_statevector_at_sixteen_qubits():
    inst = make_instance("F3", 16, index=0, depth=2)
    np.testing.assert_allclose(inst.ideal, reference_expectations(inst.circuit, inst.observables), atol=1e-9)
