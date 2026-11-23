"""D1.2 acceptance test: stored ideal values match a dense state vector for n <= 10.

Every family and variant is generated at 4, 6, 8 and 10 qubits with three seeds.
The ideal values stored by the generator (stabilizer, state-vector or analytic
route) must agree with an independent state-vector calculation to 1e-9.
"""

from __future__ import annotations

import numpy as np
import pytest

from qrace.bench import make_instance, reference_expectations, twin_instance

from conftest import FAMILY_CASES, INDICES, SMALL_WIDTHS, case_id

ATOL = 1e-9


def _cases():
    for case in FAMILY_CASES:
        family, params = case
        widths = list(SMALL_WIDTHS)
        if family == "F4" or (family == "F6" and params.get("source") == "F4"):
            widths = [n for n in widths if n % 2 == 0]
        for n in widths:
            for index in INDICES:
                yield pytest.param(family, params, n, index, id=f"{case_id(case)}-n{n}-s{index}")


@pytest.mark.parametrize(("family", "params", "n", "index"), list(_cases()))
def test_ideal_matches_statevector(family, params, n, index):
    inst = make_instance(family, n, index=index, **params)
    ref = reference_expectations(inst.circuit, inst.observables)
    np.testing.assert_allclose(inst.ideal, ref, atol=ATOL, rtol=0)


@pytest.mark.parametrize(("family", "params", "n", "index"), list(_cases()))
def test_twin_ideal_matches_statevector(family, params, n, index):
    twin = twin_instance(make_instance(family, n, index=index, **params))
    assert twin.ideal_method == "stabilizer"
    ref = reference_expectations(twin.circuit, twin.observables)
    np.testing.assert_allclose(twin.ideal, ref, atol=ATOL, rtol=0)


def test_acceptance_grid_is_complete():
    """Guard against the acceptance grid silently shrinking."""
    families = {family for family, _ in FAMILY_CASES}
    assert families == {f"F{i}" for i in range(1, 9)}
    assert len(list(_cases())) >= 180
